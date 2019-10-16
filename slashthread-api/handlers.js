const uniq = require('lodash/uniq');
const chalk = require('chalk');
const controllers = require('./controllers');

const filterForTopics = threads => uniq([].concat.apply([], threads.map(thread => thread.topics)));
const filterByAuthor = (threads, author) => threads.filter(thread => thread.author === author);
const filterByTopic = (threads, topic) => threads.filter(thread => thread.topics.includes(topic));

const getAllThreads = (request, response) => {
  const timerStart = process.hrtime();
  const { limit = 1000, offset = 0, author, topic } = request.query;
  return controllers.getAllThreads(threads => {
    const { author, topic } = request.query;
    let theThreads = threads;
    theThreads = author ? filterByAuthor(theThreads, author) : theThreads;
    theThreads = topic ? filterByTopic(theThreads, topic) : theThreads;
    theThreads = theThreads.slice(parseInt(offset), parseInt(offset) + parseInt(limit));

    const requestTiming = `${Math.round(process.hrtime(timerStart)[1]/1000000)}ms`;
    console.log(`${chalk.bold.inverse('GET')} | ${chalk.blue(request.originalUrl)} | ${chalk.green(requestTiming)}`);
    return response.status(theThreads.length > 0 ? 200 : 204).json(theThreads);
  });
}

const getThreadById = (request, response) => {
  const timerStart = process.hrtime();
  return controllers.getThread(
    request.params.id,
    thread => {
      const requestTiming = `${Math.round(process.hrtime(timerStart)[1]/1000000)}ms`;
      console.log(`${chalk.bold.inverse('GET')} | ${chalk.blue(request.originalUrl)} | ${chalk.green(requestTiming)}`);
      return response.status(200).json(thread);
  });
}

const getAllTopics = (request, response) => controllers.getAllThreads(threads => response.status(200).json(filterForTopics(threads)));

module.exports = {
  getAllThreads,
  getThreadById,
  getAllTopics,
};
