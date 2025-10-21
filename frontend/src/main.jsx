import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloProvider, ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './index.css';

export const client = new ApolloClient({
  link: new HttpLink({
    uri: import.meta.env.VITE_API_URL, // Use env variable
    credentials: 'include',
  }),
  cache: new InMemoryCache(),
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ApolloProvider client={client}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ApolloProvider>
  </React.StrictMode>
);