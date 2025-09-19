import { Routes, Route } from "react-router-dom";
import Login from "../components/login";
import Dashboard from '../components/dashboard';

export default function AppRouter() {
  return (
    <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
    </Routes>
  );
}
