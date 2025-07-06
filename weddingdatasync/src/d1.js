import { getEnvVars } from './env';

export async function testD1() {
    const envVars = getEnvVars();
	const { results } = await envVars.DB.prepare("PRAGMA table_list").run();
	return results;
}

export async function queryD1({ params = [], sql }) {
    const envVars = getEnvVars();
    const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${envVars.CLOUDFLARE_ACCOUNT_ID}/d1/database/${envVars.CLOUDFLARE_DB_ID}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${envVars.CLOUDFLARE_AUTH_TOKEN}`
        },
        body: JSON.stringify({
            params: params,
            sql: sql
        })
    });

    if (!response.ok) {
        const body = await response.json();
        console.error(body);
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

export async function insertD1Gifts(gifts) {
    const envVars = getEnvVars();
    const values = gifts.map(gift => `('${gift.id}', '${gift.lastEdited}', '${gift.name}', '${gift.url}', '${gift.rrp}', '${gift.category}', '${gift.purchased}')`).join(', ');

    const query = {
        params: [],
        sql: `INSERT OR REPLACE INTO gifts (id, lastEdited, name, url, rrp, category, purchased) VALUES ${values}`,
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

export async function getD1GuestResponses() {
    const query = {
        params: [],
        sql: `SELECT name, response, dietary, comments, lastEdited FROM rsvp_submission`,
    };

    const response = await queryD1(query);
    return response.result[0].results;
}

export async function getD1GiftResponses() {
    const query = {
        params: [],
        sql: `SELECT gift, guest, lastEdited FROM gift_submission`,
    };

    const response = await queryD1(query);
    return response.result[0].results;
}