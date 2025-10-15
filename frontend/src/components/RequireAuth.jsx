// src/components/RequireAuth.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { getAuthToken, getUser, clearAuthTokens } from '../utils/auth';

export default function RequireAuth({ requiredRole = null, redirectTo = '/login' }) {
  const token = getAuthToken();
  const user = getUser();

  if (!token) {
    clearAuthTokens();
    return <Navigate to={redirectTo} replace />;
  }

  if (requiredRole) {
    const groups = user?.groups ?? [];
    if (!groups.includes(requiredRole)) {
      return <Navigate to="/dashboard" replace />;
    }
  }
  return <Outlet />;
}
