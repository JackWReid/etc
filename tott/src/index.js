import React from 'react';
import ReactDOM from 'react-dom';
import qs from 'qs';

import App from './App';

import './index.css';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/service-worker.js')
    .then(registration => console.log(`ServiceWorker registration: ${registration.scope}`))
    .catch(error => console.error(`ServiceWorker failed to register: ${error}`)));
}

const environment = process.env.NODE_ENV || 'development';

const rootURL = environment === 'production' ? 'https://tott.now.sh' : 'http://localhost:3000';

const getQueryState = () => {
  const defaultState = () => ({
    people: [{
      name: '',
      salary: 0,
    }],
    payments: [{
      name: '',
      amount: 0,
    }]
  });

  const { appState } = qs.parse(window.location.search.replace('?', ''));

  if (!appState) {
    return defaultState();
  }

  const parsedState = JSON.parse(appState);

  if (!parsedState.people || !parsedState.payments) {
    return defaultState();
  }

  return parsedState;
}

const updateQueryState = state => {
  const encodedState = JSON.stringify(state);
  const queryString = qs.stringify({appState: encodedState});
  const newURL = `${rootURL}/?${queryString}`;
  window.history.pushState({appState: encodedState}, '', newURL);
  return queryString;
}

ReactDOM.render(
  <App
    updateQueryState={updateQueryState}
    appState={getQueryState()} />,
  document.getElementById('root')
);
