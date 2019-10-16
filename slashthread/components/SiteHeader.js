import React from 'react';
import TopicList from './TopicList';

export default ({topics}) => (
  <header className="pb4">
    <h1 className="f1 mb0 lh-title"><span className="red">/</span>thread</h1>
    <p className="f6 measure lh-copy">
      Get information. Collected by <a className="red link" target="_blank" href="http://jackwreid.uk">Jack W. Reid</a>. To submit a thread, <a className="red link" target="_blank" href="https://twitter.com/jackreid">tweet me a link</a> to the first tweet.
    </p>
    <TopicList topics={topics} />
  </header>
);
