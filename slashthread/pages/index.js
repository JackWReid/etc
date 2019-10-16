import React, { Component } from 'react';
import Head from 'next/head';
import 'isomorphic-fetch';

import SiteHeader from '../components/SiteHeader';
import ThreadList from '../components/ThreadList';

import { getThreads, getTopics } from '../service'

export default class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {
      threads: props.threads,
      topics: props.topics,
      currentTopic: props.currentTopic,
      pages: 1,
      hasMorePages: true,
    };
  }

  static async getInitialProps({query: { topic }}) {
    return Promise.all([
      getThreads({topic}),
      getTopics(),
    ]).then(values => ({
      threads: values[0],
      topics: values[1],
      currentTopic: topic,
    }));
  }

  async loadMoreThreads(pages, topic) {
    const threads = await getThreads({length: 3 * (pages + 1), topic});
    return this.setState(old => ({
      threads,
      pages: old.pages + 1,
    }));
  }

  componentWillReceiveProps = ({currentTopic, threads, topics}) => {
    return this.setState({
      currentTopic,
      threads,
      topics,
    });
  }

  render() {
    const { threads, topics, pages, currentTopic, hasMorePages } = this.state;

    return (
      <div className="sans-serif pa4">
        <Head>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="stylesheet" href="https://unpkg.com/tachyons/css/tachyons.min.css" />
          <link rel="icon" href="/static/favicon.png" />
          <title>/thread</title>
        </Head>
        <SiteHeader topics={topics} />
        <ThreadList threads={threads} hasMore={hasMorePages} loadMore={() => this.loadMoreThreads(pages, currentTopic)} />
      </div>
    );
  }
}
