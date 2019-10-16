import React from 'react';
import { css } from 'glamor';

export default ({children, ...props}) => (
  <div {...css({
    maxWidth: 800,
    margin: '0 auto',
    padding: 18,
  })}
  {...props}>
    {children}
  </div>
);
