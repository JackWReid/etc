import { getEnvVars } from "./env";

export async function testD1() {
    const envVars = getEnvVars();
	const { results } = await envVars.DB.prepare("PRAGMA table_list").run();
	return results;
}

export async function queryD1(sql) {
    const envVars = getEnvVars();
    const { DB } = envVars;
    const stmt = await DB.prepare(sql);
    const results = await stmt.all();
    return results;
}

export async function insertD1RSVP(rsvp) {
    const sql = `INSERT OR REPLACE INTO rsvp_submission (name, response, dietary, comments, lastEdited) VALUES ('${rsvp.name}', '${rsvp.response}', '${rsvp.dietary}', '${rsvp.comments}', datetime('now'))`;
    const response = await queryD1(sql);
    return response;
}

export async function insertD1GiftRegistration(giftReg) {
    const sql = `INSERT OR REPLACE INTO gift_submission (guest, gift, lastEdited) VALUES ('${giftReg.name}', '${giftReg.gift}', datetime('now'))`;
    const response = await queryD1(sql);
    return response.results;
}

export async function getD1Gifts() {
    const sql = `SELECT id, lastEdited, name, url, rrp, category, purchased FROM gifts WHERE purchased != "Yes"`;
    const response = await queryD1(sql);
    return response.results;
}