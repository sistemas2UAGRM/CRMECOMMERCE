
import React from 'react';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';

import HomePage from './pages/Home.jsx';
import Layout from './pages/Layout.jsx';
import LoginPage from './pages/Login.jsx';
import RegisterPage from './pages/Register.jsx';
import ProductosPage from './pages/Productos.jsx';
import ProductosAdd from './pages/ProductosAdd.jsx';
import CarritosPage from './pages/Carritos.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
    <Route path="productos" element={<ProductosPage />} />
    <Route path="productos/add" element={<ProductosAdd />} />
          <Route path="carritos" element={<CarritosPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);

//imagenes son place holders