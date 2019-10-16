const fetch = require('node-fetch');

function getAllThreads(callback) {
  return fetch(`https://s3.eu-west-2.amazonaws.com/jackwreid/slashthread/threads.json`)
  .then(response => response.json())
  .then(json => callback(json))
  .catch(error => console.log(error));
}

function getThread(threadId, callback) {
  return fetch(`https://s3.eu-west-2.amazonaws.com/jackwreid/slashthread/threads.json`)
  .then(response => response.json())
  .then(json => callback(json[parseInt(threadId)]))
  .catch(error => console.log(error));
}

module.exports = {
  getAllThreads,
  getThread,
};
