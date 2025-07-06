
import { getEnvVars } from "./env";
import { getD1GiftResponses, getD1GuestResponses } from "./d1";

export async function getNotionGuestList() {
  const envVars = getEnvVars();
  const { notionClient } = envVars;
  let guestList = [];
  let nextGuests
  let response;

  response = await notionClient.databases.query({ database_id: envVars.GUEST_DB });
  nextGuests = response.results.slice(1);
  guestList = [...guestList, ...nextGuests];

  while (response.has_more) {
      response = await notionClient.databases.query({ database_id: envVars.GUEST_DB, start_cursor: response.next_cursor });
      nextGuests = response.results.slice(1);
      guestList = [...guestList, ...nextGuests];
  }

  const transformedGuests = guestList.map((page) => ({
      id: page.id,
      lastEdited: page.last_edited_time,
      name: page.properties.Name.title[0]?.plain_text,
      home: page.properties.Home.select?.name,
      side: page.properties.Side.select?.name,
      email: page.properties.Email.email,
      diet: page.properties.Diet.multi_select.map((item) => item.name),
      confirmed: page.properties.Confirmed.select?.name || null,
      group: page.properties.Group.select?.name,
  }));

  return transformedGuests;
}

export async function getNotionGiftList() {
  const envVars = getEnvVars();
  const { notionClient } = envVars;
  let giftList = [];
  let nextGifts
  let response;
  response = await notionClient.databases.query({ database_id: envVars.GIFT_DB });
  nextGifts = response.results.slice(1);
  giftList = [...giftList, ...nextGifts];

  while (response.has_more) {
      response = await notionClient.databases.query({ database_id: envVars.GIFT_DB, start_cursor: response.next_cursor });
      nextGifts = response.results.slice(1);
      giftList = [...giftList, ...nextGifts];
  }

  const transformedGifts = giftList.map((page) => {
      return {
          id: page.id,
          lastEdited: page.last_edited_time,
          name: page.properties.Name.title[0]?.plain_text,
          url: page.properties.URL.url,
          rrp: page.properties.RRP.number,
          category: page.properties.Category.select?.name,
          purchased: page.properties.Purchased.select?.name || null,
      };
  });

  return transformedGifts;

}

export async function syncGiftResponses(d1GiftResponses) {
  const envVars = getEnvVars();
  const { notionClient } = envVars;

  const pages = await notionClient.databases.query({ database_id: envVars.GIFT_RES_DB });
  for (const page of pages.results) {
    await notionClient.pages.update({ page_id: page.id, archived: true });
  }
  
  for (const giftResponse of d1GiftResponses) {
    const properties = {
      Gift: {
        type: 'title',
        title: [ { type: 'text', text: { content: giftResponse.gift } } ]
      },
      Guest: {
        type: 'rich_text',
        rich_text: [{ type: 'text', text: { content: giftResponse.guest } }]
      },
      Date: {
        type: 'date',
        date: {
          start: giftResponse.lastEdited
        }
      }
    };

    await notionClient.pages.create({
      parent: { type: 'database_id', database_id: envVars.GIFT_RES_DB },
      properties,
    });
  }

}

export async function syncGuestResponses(d1GuestResponses) {
  const envVars = getEnvVars();
  const { notionClient } = envVars;

  const pages = await notionClient.databases.query({ database_id: envVars.GUEST_RES_DB });
  for (const page of pages.results) {
    await notionClient.pages.update({ page_id: page.id, archived: true });
  }
  
  for (const guestResponse of d1GuestResponses) {
    const properties = {
      Name: {
        type: 'title',
        title: [ { type: 'text', text: { content: guestResponse.name } } ]
      },
      Response: {
        type: 'rich_text',
        rich_text: [{ type: 'text', text: { content: guestResponse.response } }]
      },
      Dietary: {
        type: 'rich_text',
        rich_text: [{ type: 'text', text: { content: guestResponse.dietary } }]
      },
      Comments: {
        type: 'rich_text',
        rich_text: [{ type: 'text', text: { content: guestResponse.comments } }]
      },
      Date: {
        type: 'date',
        date: {
          start: guestResponse.lastEdited
        }
      }
    }

    await notionClient.pages.create({
      parent: { type: 'database_id', database_id: envVars.GUEST_RES_DB },
      properties,
    });
  }
}