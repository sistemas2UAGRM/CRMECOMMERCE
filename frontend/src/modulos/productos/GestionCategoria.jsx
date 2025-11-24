// frontend/src/modulos/productos/GestionCategoria.jsx
import React, { useState, useEffect } from "react";
import { useCategorias } from "./hooks/useCategorias";
import Modal from "./Modal";
import CategoriaForm from "./CategoriaForm";

export default function GestionCategorias() {
  const { categorias: categoriasRaw, cargando, error, crearCategoria, editarCategoria, eliminarCategoria, obtenerCategorias } = useCategorias();
  const [categorias, setCategorias] = useState([]);
  const [abiertoModal, setAbiertoModal] = useState(false);
  const [categoriaEdit, setCategoriaEdit] = useState(null);

  // Normalizar la respuesta del backend
  useEffect(() => {
    if (Array.isArray(categoriasRaw)) {
      setCategorias(categoriasRaw);
    } else if (categoriasRaw && Array.isArray(categoriasRaw.results)) {
      setCategorias(categoriasRaw.results);
    } else {
      setCategorias([]);
    }
  }, [categoriasRaw]);

  const abrirEditar = (cat) => {
    setCategoriaEdit(cat);
    setAbiertoModal(true);
  };

  const handleGuardar = async (datos) => {
    try {
        if (categoriaEdit && categoriaEdit.id) {
            await editarCategoria(categoriaEdit.id, datos);
            setCategoriaEdit(null);
        } else {
            await crearCategoria(datos);
        }
        setAbiertoModal(false);
        await obtenerCategorias(); // recargar listado
    } catch (err) {
        console.error(err);
        alert(
            err?.response?.data?.detail || "Error guardando categoría"
        );
    }
  };


  const handleEliminar = async (id) => {
    if (!window.confirm("¿Eliminar categoría?")) return;
    try {
      await eliminarCategoria(id);
      await obtenerCategorias(); // recargar listado
    } catch (err) {
      console.error(err);
      alert("Error eliminando categoría");
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gestión de Categorías</h1>
        <button
          onClick={() => { setCategoriaEdit(null); setAbiertoModal(true); }}
          className="px-4 py-2 bg-green-600 text-white rounded"
        >
          Nueva categoría
        </button>
      </div>

      {cargando && <div className="mb-4 text-gray-600">Cargando categorías...</div>}
      {error && <div className="mb-4 text-red-600">Error al cargar categorías</div>}

      <table className="w-full border rounded">
        <thead className="bg-gray-100">
          <tr>
            <th className="border px-3 py-2 text-left">Nombre</th>
            <th className="border px-3 py-2 text-left">Descripción</th>
            <th className="border px-3 py-2 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {(!categorias || categorias.length === 0) && (
            <tr>
              <td colSpan={3} className="text-center py-4 text-gray-500">No hay categorías</td>
            </tr>
          )}
          {Array.isArray(categorias) && categorias.map(cat => (
            <tr key={cat.id}>
              <td className="border px-3 py-2">{cat.nombre}</td>
              <td className="border px-3 py-2">{cat.descripcion}</td>
              <td className="border px-3 py-2 text-center space-x-2">
                <button
                  onClick={() => abrirEditar(cat)}
                  className="px-2 py-1 rounded bg-indigo-600 text-white text-sm"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleEliminar(cat.id)}
                  className="px-2 py-1 rounded bg-red-600 text-white text-sm"
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Modal
        abierto={abiertoModal}
        titulo={categoriaEdit ? "Editar categoría" : "Nueva categoría"}
        onCerrar={() => setAbiertoModal(false)}
      >
        <CategoriaForm
          categoriaInicial={categoriaEdit}
          onSubmit={handleGuardar}
          onCancelar={() => setAbiertoModal(false)}
        />
      </Modal>
    </div>
  );
}
