import React from 'react';
import { css } from 'glamor';

export default () => (
  <div {...css({
    width: '100%',
    marginTop: 16,
    padding: 16,
    textAlign: 'center',
    color: '#FFF',
    backgroundColor: '#357EDD',
    '@media print': {display: 'none'},
  })}>
    <p>Created by <a {...css({color: 'inherit', textDecoration: 'underline'})} href="http://jackwreid.uk">Jack Reid</a>.</p>
  </div>
);
