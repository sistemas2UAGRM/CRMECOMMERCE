// frontend/src/modulos/usuarios/hooks/useUsers.js
import { useContext } from "react";
import { UsersContext } from "../context/UsersContext";

export const useUsers = () => {
  const context = useContext(UsersContext);
  if (!context) {
    throw new Error("useUsers debe usarse dentro de un UsersProvider");
  }
  return context;
};