// frontend/src/modulos/productos/almacenes/GestionAlmacenes.jsx
import React, { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import almacenesService from "../../../services/almacenesService";
import Modal from "../Modal"; 
import AlmacenTable from "./AlmacenTable";
import AlmacenForm from "./AlmacenForm";
// Opcional: un modal para ver el inventario
import InventarioModal from "./InventarioModal"; 

export default function GestionAlmacenes() {
  const [almacenes, setAlmacenes] = useState([]);
  const [cargando, setCargando] = useState(false);
  
  // Estado para el modal de CRUD
  const [modalFormAbierto, setModalFormAbierto] = useState(false);
  const [almacenEdit, setAlmacenEdit] = useState(null);

  // Estado para el modal de inventario
  const [modalInventarioAbierto, setModalInventarioAbierto] = useState(false);
  const [almacenSeleccionado, setAlmacenSeleccionado] = useState(null);

  const cargarAlmacenes = useCallback(async () => {
    setCargando(true);
    try {
      const res = await almacenesService.listar();
      // Maneja respuestas paginadas y no paginadas
      setAlmacenes(Array.isArray(res) ? res : res.results || []);
    } catch (error) {
      toast.error("Error al cargar los almacenes.");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    cargarAlmacenes();
  }, [cargarAlmacenes]);

  const abrirModalParaCrear = () => {
    setAlmacenEdit(null);
    setModalFormAbierto(true);
  };

  const abrirModalParaEditar = (almacen) => {
    setAlmacenEdit(almacen);
    setModalFormAbierto(true);
  };
  
  const abrirModalInventario = (almacen) => {
    setAlmacenSeleccionado(almacen);
    setModalInventarioAbierto(true);
  }

  const handleGuardar = async (datos) => {
    const promesa = almacenEdit 
      ? almacenesService.actualizar(almacenEdit.id, datos) 
      : almacenesService.crear(datos);

    toast.promise(promesa, {
      loading: 'Guardando...',
      success: `Almacén ${almacenEdit ? 'actualizado' : 'creado'} con éxito.`,
      error: `No se pudo guardar el almacén.`,
    }).then(() => {
      setModalFormAbierto(false);
      cargarAlmacenes();
    }).catch(err => console.error(err));
  };

  const handleEliminar = async (id) => {
    if (window.confirm("¿Seguro que quieres eliminar este almacén? Esta acción no se puede deshacer.")) {
      toast.promise(almacenesService.eliminar(id), {
        loading: 'Eliminando...',
        success: 'Almacén eliminado.',
        error: 'No se pudo eliminar el almacén.',
      }).then(() => {
        cargarAlmacenes();
      }).catch(err => console.error(err));
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Gestión de Almacenes</h1>
          <p className="text-sm text-gray-500">Crea y administra tus almacenes o sucursales.</p>
        </div>
        <button onClick={abrirModalParaCrear} className="px-4 py-2 bg-green-600 text-white rounded">
          Nuevo Almacén
        </button>
      </div>

      <AlmacenTable
        almacenes={almacenes}
        onEditar={abrirModalParaEditar}
        onEliminar={handleEliminar}
        onVerInventario={abrirModalInventario}
        cargando={cargando}
      />

      <Modal
        abierto={modalFormAbierto}
        onCerrar={() => setModalFormAbierto(false)}
        titulo={almacenEdit ? "Editar Almacén" : "Crear Nuevo Almacén"}
      >
        <AlmacenForm
          almacenInicial={almacenEdit}
          onSubmit={handleGuardar}
          onCancelar={() => setModalFormAbierto(false)}
        />
      </Modal>
      
      {almacenSeleccionado && (
        <InventarioModal
          almacen={almacenSeleccionado}
          abierto={modalInventarioAbierto}
          onCerrar={() => setModalInventarioAbierto(false)}
        />
      )}
    </div>
  );
}