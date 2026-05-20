/**
 * Entry point for the ReqEngine frontend.
 * Wraps the application in React strict mode and BrowserRouter for routing.
 * Imports the global stylesheet before mounting the root component.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './styles/global.css';
import App from './App';

const rootElement = document.getElementById('root');
if (rootElement === null) {
  throw new Error('Root element #root not found in the DOM.');
}

createRoot(rootElement).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
