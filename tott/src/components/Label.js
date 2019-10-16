import React from 'react';
import { css } from 'glamor';

export default ({children, ...props}) => (
  <label
    {...css({
      display: 'block',
      paddingBottom: 4,
      color: '#777777',
    })}
    {...props}>
    {children}
  </label>
);
