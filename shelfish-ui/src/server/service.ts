import { getBookStats, insertOkuBookRecords, insertOkuBookEvents } from "./db";
import { executeNextJob, generateIdentifierJobs } from "./jobs";
import { getParsedOkuFeed } from "./oku";

async function syncOkuDb() {
  for (const feedName of ["read", "toread", "reading"]) {
    const { Books, Events } = await getParsedOkuFeed(feedName);
    await insertOkuBookRecords(Books);
    await insertOkuBookEvents(Events);
  }
}

async function startJobWatcher() {
  // await generateIdentifierJobs();
  while (true) {
    await new Promise((resolve) => setTimeout(resolve, 2000));
    await executeNextJob();
  }
}

export async function startService() {
  await syncOkuDb();
  startJobWatcher();

  const bookStats = await getBookStats();

  return { bookStats };
}
