function cleanResponse(threads) {
  if (typeof threads === 'object') {
    const convertedObject = Object.keys(threads).map(key => threads[key]);
    return convertedObject.filter(thread => !!thread);
  } else {
    return threads.filter(thread => !!thread);
  }
}

export async function getThreads({length = 3, offset = 0, topic = ''}) {
  const response = await fetch(`https://api.slashthread.space/?limit=${length}&offset=${offset}&topic=${topic}`);
  const threads = await response.json();
  return cleanResponse(threads);
}

export async function getTopics() {
  const response = await fetch(`https://api.slashthread.space/topics`);
  const topics = await response.json();
  return topics;
}
