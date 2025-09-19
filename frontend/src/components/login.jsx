import { useState } from "react";
import API from "../services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("token/", { username: email, password });
      localStorage.setItem("token", res.data.access);
      alert("Login exitoso 🚀");
    }catch (err) {
      setError("Credenciales inválidas");
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input type="text" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Contraseña" />
      <button type="submit">Login</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
}
