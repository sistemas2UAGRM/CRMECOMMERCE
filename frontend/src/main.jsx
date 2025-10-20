import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom';
import './index.css'
import App from './App.jsx'
import { ProductosProvider } from './modulos/productos/context/ProductosContext.jsx';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext.jsx';
import { UsersProvider } from './modulos/usuarios/context/UsersContext.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ProductosProvider>
          <UsersProvider>
            <App />
            <Toaster
              position="top-right" // Posición de las notificaciones
              reverseOrder={false}
              toastOptions={{
                success: {
                  style: {
                    background: '#28a745', // Fondo verde
                    color: 'white',       // Texto blanco
                  },
                },
                error: {
                  style: {
                    background: '#dc3545', // Fondo rojo
                    color: 'white',       // Texto blanco
                  },
                },
              }}
            />
          </UsersProvider>
        </ProductosProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
