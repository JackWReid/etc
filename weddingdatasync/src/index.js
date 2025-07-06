/**
 * Welcome to Cloudflare Workers! This is your first scheduled worker.
 *
 * - Run `wrangler dev --local` in your terminal to start a development server
 * - Run `curl "http://localhost:8787/cdn-cgi/mf/scheduled"` to trigger the scheduled event
 * - Go back to the console to see what your worker has logged
 * - Update the Cron trigger in wrangler.toml (see https://developers.cloudflare.com/workers/wrangler/configuration/#triggers)
 * - Run `wrangler publish --name my-worker` to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/runtime-apis/scheduled-event/
 */
import { Client } from "@notionhq/client";
import { setEnvVars } from "./env";
import { getNotionGiftList, getNotionGuestList, syncGiftResponses, syncGuestResponses } from "./notion";
import { insertD1Gifts, insertD1Guests, getD1GiftResponses, getD1GuestResponses } from "./d1";

async function trigger(env) {
	console.log('Starting wedding data sync');
	const notionClient  = new Client({ auth: env.NOTION_TOKEN });
	setEnvVars({ ...env, notionClient });

	const guestList = await getNotionGuestList();
	await insertD1Guests(guestList);
	console.log('Synced guest list Notion -> D1');

	const giftList = await getNotionGiftList();
	await insertD1Gifts(giftList);
	console.log('Synced gift list Notion -> D1');

	const rsvps = await getD1GuestResponses();
	await syncGuestResponses(rsvps);
	console.log('Synced guest responses D1 -> Notion');

	const giftRegs = await getD1GiftResponses();
	await syncGiftResponses(giftRegs);
	console.log('Synced gift registrations D1 -> Notion');
}

export default {
	async scheduled(controller, env, ctx) {
		await trigger(env);
		console.log('Finished wedding data sync');
	},

	async fetch(request, env, ctx) {
		const url = new URL(request.url);
		const { pathname } = url;

		console.log(request.method, request.pathname)
		if (request.method === 'GET' && pathname == "/trigger") {
			await trigger(env);
			return new Response('Finished wedding data sync');
		}
		return new Response('ok');
	}
};
