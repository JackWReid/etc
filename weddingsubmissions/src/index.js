/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */
import { insertD1GiftRegistration, insertD1RSVP, getD1Gifts } from "./d1";
import { setEnvVars } from "./env";

export default {
	async fetch(request, env, ctx) {
		setEnvVars(env);
		const cache = caches.default;
		const url = new URL(request.url);
		const { pathname } = url;

		if (request.method === 'GET') {
			if (['/gifts', '/api/gifts'].includes(pathname)) {
				// curl "http://localhost:59843/gifts"
				// curl "https://weddingsubmissions.hello-f16.workers.dev/gifts"

				let response;
				let cacheResponse = await cache.match(request);

				if (!cacheResponse) {
					console.log(`MISS: ${url}`);
					const giftList = await getD1Gifts();
					response = new Response(JSON.stringify(giftList), {
						headers: {
							'content-type': 'application/json;charset=UTF-8',
							'Cache-Control': 's-maxage=3600'
						},
					});
					ctx.waitUntil(cache.put(request, response.clone()));
				} else {
					console.log(`HIT: ${url}`);
					response = cacheResponse;
				}
				return response;
			}
		}

		if (request.method === 'POST') {
			// curl -X POST -H "Content-Type: multipart/form-data" -F "name=John Doe" -F "response=Yes" -F "dietary=Vegan" -F "comments=Looking forward to it" "http://localhost:59843/rsvp"
			// curl -X POST -H "Content-Type: multipart/form-data" -F "name=John Doe" -F "response=Yes" -F "dietary=Vegan" -F "comments=Looking forward to it" "https://weddingsubmissions.hello-f16.workers.dev/rsvp"
			if (['/rsvp', '/api/rsvp'].includes(pathname)) {
				const formData = await request.formData();
				const name = formData.get('name');
				const response = formData.get('response');
				const dietary = formData.get('dietary');
				const comments = formData.get('comments');
				await insertD1RSVP({ name, response, dietary, comments });
				return new Response(null, {
					status: 301,
					headers: {
						Location: 'https://sarahandjack.wedding/submitted',
					},
				});

			// curl -X POST -H "Content-Type: multipart/form-data" -F "gift=Book" -F "name=John Doe" "http://localhost:59843/gift"
			// curl -X POST -H "Content-Type: multipart/form-data" -F "gift=Book" -F "name=John Doe" "https://weddingsubmissions.hello-f16.workers.dev/gift"
			} else if ([ '/gift', '/api/gift' ].includes(pathname)) {
				const formData = await request.formData();
				const name = formData.get('name');
				const gift = formData.get('response');
				await insertD1GiftRegistration({ name, gift });
				return new Response(null, {
					status: 302,
					headers: {
						Location: 'https://sarahandjack.wedding/submitted',
					},
				});
			}
		}

		// Handle other request methods and paths...
		return new Response('ok');
	},
};