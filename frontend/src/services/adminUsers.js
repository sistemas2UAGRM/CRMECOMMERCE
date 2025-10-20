// src/services/adminUsers.js
import api from "./api";

const BASE = "/users/users/";

export const adminListUsers = (params = {}) => api.get(BASE, { params });
export const adminCreateUser = (payload) => api.post(BASE, payload);
export const adminGetUser = (id) => api.get(`${BASE}${id}/`);
export const adminUpdateUser = (id, payload) => api.put(`${BASE}${id}/`, payload);
export const adminPartialUpdateUser = (id, payload) => api.patch(`${BASE}${id}/`, payload);
export const adminDeleteUser = (id) => api.delete(`${BASE}${id}/`);
export const adminActivateUser = (id) => api.post(`${BASE}${id}/activate/`);
export const adminDeactivateUser = (id) => api.post(`${BASE}${id}/deactivate/`);
export const adminGetActivityLog = (id, params = {}) => api.get(`${BASE}${id}/activity_log/`, { params });

// Search endpoints (from your urls)
export const searchUsers = (q) => api.get(`${BASE}search/`, { params: { q } });
export const searchActiveUsers = () => api.get(`${BASE}active/`);
export const searchUsersByRole = (role) => api.get(`${BASE}by-role/${role}/`);
export const getUserStats = () => api.get(`${BASE}stats/`);
