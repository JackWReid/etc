const fs = require('fs');
const randomFromArray = require('unique-random-array');
const wordList = require('./wordList');

module.exports = randomFromArray(wordList);
