import dotenv from 'dotenv';
import fetch from 'node-fetch';

dotenv.config();

export async function queryD1({ params = [], sql }) {
  const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${process.env.CLOUDFLARE_ACCOUNT_ID}/d1/database/${process.env.CLOUDFLARE_DB_ID}/query`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.CLOUDFLARE_AUTH_TOKEN}`
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