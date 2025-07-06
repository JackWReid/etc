import express from 'express';
import morgan from 'morgan';
import dotenv from 'dotenv';

import { queryD1 } from './d1.mjs';
import { getNotionGuestList, getNotionGiftList, getD1GuestList, getD1GiftList, insertD1Guests, insertD1Gifts } from './controllers.mjs';

dotenv.config();

const app = express();
app.use(express.json());
app.use(morgan('short'));

app.get('/notion/guests', async (req, res) => {
    const guestList = await getNotionGuestList();
    return res.json(guestList);
});

app.get('/notion/gifts', async (req, res) => {
    const giftList = await getNotionGiftList();
    return res.json(giftList);
});

app.get('/d1/guests', async (req, res) => {
    const guestList = await getD1GuestList();
    return res.json(guestList);
});

app.get('/d1/gifts', async (req, res) => {
    const giftList = await getD1GiftList();
    return res.json(giftList);
});

app.post('/sync', async (req, res) => {
    const guestList = await getNotionGuestList();
    const giftList = await getNotionGiftList();

    await insertD1Guests(guestList);
    await insertD1Gifts(giftList);

    return res.json({ message: "ok" });
});

// curl -X POST http://localhost:3000/submission/rsvp \
// -H "Content-Type: application/json" \
// -d '{
//     "name": "John Doe",
//     "response": "Yes",
//     "dietary": "Vegan",
//     "notes": "Looking forward to it!"
// }'

app.post('/submission/rsvp', async (req, res) => {
    const { name, response, dietary, comments } = req.body;

    const query = {
        params: [name, response, dietary, comments],
        sql: `INSERT INTO rsvp_submission (name, response, dietary, comments, lastEdited) VALUES (?, ?, ?, ?, datetime('now', 'localtime'))`,
    };

    await queryD1(query);
    return res.json({ message: "ok" });
});

// curl -X POST http://localhost:3000/submission/gift \
// -H "Content-Type: application/json" \
// -d '{
//     "gift": "Some Gift",
//     "guest": "John Doe"
// }'

app.post('/submission/gift', async (req, res) => {
    const { gift, guest } = req.body;

    const query = {
        params: [gift, guest],
        sql: `INSERT INTO gift_submission (gift, guest, lastEdited) VALUES (?, ?, datetime('now', 'localtime'))`,
    };

    await queryD1(query);
    return res.json({ message: "ok" });
});

app.get('/', async (req, res) => {
    return res.json({ message: "ok" });
});

app.delete('/', async (req, res) => {
    await queryD1({ sql: `DELETE FROM guests` });
    await queryD1({ sql: `DELETE FROM gifts` });
    await queryD1({ sql: `DELETE FROM gift_submission` });
    await queryD1({ sql: `DELETE FROM rsvp_submission` });

    return res.json({ message: "ok" });
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});