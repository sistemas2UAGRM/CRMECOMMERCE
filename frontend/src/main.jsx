import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import './index.css'
import App from './App.jsx'
import { ProductosProvider } from './modulos/productos/context/ProductosContext.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ProductosProvider>
        <App />
      </ProductosProvider>
    </BrowserRouter>
  </StrictMode>,
)
