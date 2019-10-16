import React from 'react';

export default ({size = 100, color = 'currentColor'}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <g id="Symbols" stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
      <g id="Logo-Blue" fill={color}>
        <path d="M30.7029732,96.1640974 C12.6693304,88.6112241 0,70.7917103 0,50.012383 C0,22.3913066 22.3857625,0 50,0 C61.3972243,0 71.9037985,3.81427072 80.3134464,10.2362372 L30.7029732,96.1640974 Z M94.0816406,26.3890429 C97.8579276,33.4244023 100,41.4681768 100,50.012383 C100,77.1039639 78.4642804,99.1643622 51.5822084,100.000201 L94.0816357,26.3890338 Z" id="Combined-Shape"></path>
      </g>
    </g>
  </svg>
);
