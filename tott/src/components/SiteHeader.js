import React from 'react';
import { css } from 'glamor';

import Logo from './Logo';

export default () => (
  <div {...css({
    padding: 32,
    textAlign: 'center',
    color: '#FFFFFF',
    backgroundColor: '#357EDD',
    userSelect: 'none',
    cursor: 'default',
    '@media print': {display: 'none'},
    '@media(max-width: 600px)': {
      padding: 16,
    },
  })}>
    <a href="/" {...css({
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      color: 'inherit',
      textDecoration: 'none',
      transform: 'translateX(-2vw)',
    })}>
      <h1 {...css({
        marginLeft: 80,
        fontSize: 80,
        letterSpacing: 40,
        '@media(max-width: 600px)': {
          fontSize: 64,
        },
      })}>tott</h1>
      <div {...css({
        '@media(max-width: 600px)': {
          display: 'none',
        },
      })}>
        <Logo color="white" />
      </div>
    </a>
    <p {...css({
      margin: '-10px auto 1em',
      maxWidth: '20em',
      fontWeight: 'bold',
      fontSize: 24,
    })}>
      Split your bills based on how much you’re working with.
      </p>
  </div>
);
