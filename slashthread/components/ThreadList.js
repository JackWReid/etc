import React, { Component } from 'react';
import Link from 'next/link';
import InfiniteScroll from 'react-infinite-scroller';
import TopicList from './TopicList';

const ThreadListItem = ({thread}) => (
  <li className="pb4">
    <h1 className="mb0">
      <a className="black link underline" target="_blank" href={thread.url}>{thread.title}</a>
    </h1>
    <h2 className="f6 normal lh-title">
      by <a className="red link" target="_blank" href={`https://twitter.com/${thread.author}`}>@{thread.author}</a>
    </h2>
    <p className="f4 lh-copy measure">{thread.info}</p>
    <TopicList topics={thread.topics} />
  </li>
);

const ThreadList = ({loadMore, hasMore, threads}) => (
  <ul className="list pa0">
    <InfiniteScroll
      pageStart={0}
      hasMore={hasMore}
      loadMore={loadMore}
      loader={<div>Loading...</div>}>
      {threads.map((thread, index) => <ThreadListItem thread={thread} key={index} />)}
    </InfiniteScroll>
  </ul>
);

export default ThreadList;
