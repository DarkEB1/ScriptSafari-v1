import ReactDOM from 'react-dom/client';
import App from './App';
import { Auth0Provider } from '@auth0/auth0-react';
 
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Auth0Provider
  domain='dev-dic5qyxmh3023gsq.us.auth0.com'
  clientId='WsWUDvT0VtriDCaey0ZHu74mQ2Av3iUb'
  authorizationParams={{ redirect_uri: window.location.origin }}>
  <App />
</Auth0Provider>
);