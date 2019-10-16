const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');
const compression = require('compression');
const apicache = require('apicache');
const cors = require('cors');
const morgan = require('morgan');
const responseTime = require('response-time');
require('now-logs')('slashthread-api');
const app = express();

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(morgan('combined'));
app.use(responseTime());
app.use(compression());
app.use(apicache.middleware('5 minutes'));
app.use(cors());

const handler = require('./handlers');

app.get('/', handler.getAllThreads);
app.get('/topics', handler.getAllTopics);
app.get('/:id', handler.getThreadById);

const port = process.env.PORT || 8080;
app.listen(port);
