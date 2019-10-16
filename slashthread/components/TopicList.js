import React from 'react';
import Link from 'next/link';

export default ({topics}) => (
  <nav>
    <ul className="list ma0 pa0">
      {topics.map((topic, index) => <li className="dib mr2 f6" key={index}>
        <Link href={`/?topic=${topic}`}><a className="red link">#{topic}</a></Link>
      </li>)}
    </ul>
  </nav>
);
