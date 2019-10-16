import React from 'react';
import { css } from 'glamor';

const styles = {
  padding: 8,
  fontSize: 16,
  fontFamily: 'Helvetica, Arial, sans-serif',
  appearance: 'none',
  border: '1px solid #979797',
  borderRadius: 4,
};

export default ({placeholder = '', onChange = () => false, type = 'text', name, ...props}) => (
  <input
    type={type}
    id={`input-${name}`}
    onChange={onChange}
    placeholder={placeholder}
    {...css(styles)}
    {...props} />
);
