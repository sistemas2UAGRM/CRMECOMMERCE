// frontend/src/modulos/productos/hooks/useProductos.js
import { useContext } from "react";
import { ProductosContext } from "../context/ProductosContext";

export const useProductos = () => {
  const ctx = useContext(ProductosContext);
  if (!ctx) throw new Error("useProductos debe usarse dentro de ProductosProvider");
  return ctx;
};
