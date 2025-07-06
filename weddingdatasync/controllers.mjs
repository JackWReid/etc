import dotenv from 'dotenv';
import { Client } from '@notionhq/client';

import { queryD1 } from './d1.mjs';

dotenv.config();

const notion = new Client({ auth: process.env.NOTION_TOKEN });

export async function getD1GuestList() {
    const query = {
        params: [],
        sql: `SELECT * FROM guests`,
    };

    const response = await queryD1(query);
    return response;
}

export async function getD1GiftList() {
    const query = {
        params: [],
        sql: `SELECT * FROM gifts`,
    };

    const response = await queryD1(query);
    return response;
}

export async function insertD1Guests(guests) {
    const values = guests.map(guest => `('${guest.id}', '${guest.lastEdited}', '${guest.name}', '${guest.home}', '${guest.side}', '${guest.email}', '${guest.diet}', '${guest.confirmed}', '${guest.group}')`).join(', ');

    const query = {
        params: [],
        sql: `INSERT OR REPLACE INTO guests (id, lastEdited, name, home, side, email, diet, confirmed, "group") VALUES ${values}`,
    };

    const response = await queryD1(query);
    return response;
}

export async function insertD1Gifts(gifts) {
    const values = gifts.map(gift => `('${gift.id}', '${gift.lastEdited}', '${gift.name}', '${gift.url}', '${gift.rrp}', '${gift.category}', '${gift.purchased}')`).join(', ');

    const query = {
        params: [],
        sql: `INSERT OR REPLACE INTO gifts (id, lastEdited, name, url, rrp, category, purchased) VALUES ${values}`,
    };

    const response = await queryD1(query);
    return response;
}

export async function getNotionGuestList() {
    let guestList = [];
    let nextGuests
    let response;

    response = await notion.databases.query({ database_id: process.env.GUEST_DB });
    nextGuests = response.results.slice(1);
    guestList = [...guestList, ...nextGuests];

    while (response.has_more) {
        response = await notion.databases.query({ database_id: process.env.GUEST_DB, start_cursor: response.next_cursor });
        nextGuests = response.results.slice(1);
        guestList = [...guestList, ...nextGuests];
    }

    const transformedGuests = guestList.map((page) => ({
        id: page.id,
        lastEdited: page.last_edited_time,
        name: page.properties.Name.title[0]?.plain_text,
        home: page.properties.Home.select?.name,
        side: page.properties.Side.select?.name,
        email: page.properties.Email,
        diet: page.properties.Diet.multi_select.map((item) => item.name),
        confirmed: page.properties.Confirmed.select?.name || null,
        group: page.properties.Group.select?.name,
    }));

    return transformedGuests;
}

export async function getNotionGiftList() {
    let giftList = [];
    let nextGifts
    let response;

    response = await notion.databases.query({ database_id: process.env.GIFT_DB });
    nextGifts = response.results.slice(1);
    giftList = [...giftList, ...nextGifts];

    while (response.has_more) {
        response = await notion.databases.query({ database_id: process.env.GIFT_DB, start_cursor: response.next_cursor });
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