// frontend/src/modulos/productos/almacenes/InventarioModal.jsx
import React, { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import almacenesService from '../../../services/almacenesService';
import Modal from '../Modal'; 

export default function InventarioModal({ almacen, abierto, onCerrar }) {
  const [articulos, setArticulos] = useState([]);
  const [cargando, setCargando] = useState(false);

  const cargarArticulos = useCallback(async () => {
    if (!almacen) return;
    setCargando(true);
    try {
      const data = await almacenesService.articulos(almacen.id);
      setArticulos(data);
    } catch (error) {
      toast.error(`Error al cargar el inventario de ${almacen.nombre}.`);
      console.error(error);
    } finally {
      setCargando(false);
    }
  }, [almacen]);

  useEffect(() => {
    if (abierto) {
      cargarArticulos();
    }
  }, [abierto, cargarArticulos]);

  return (
    <Modal abierto={abierto} onCerrar={onCerrar} titulo={`Inventario de: ${almacen?.nombre}`} size="lg">
      <div className="overflow-auto border rounded" style={{ maxHeight: '60vh' }}>
        <table className="min-w-full">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Producto</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Reservado</th>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Disponible</th>
            </tr>
          </thead>
          <tbody>
            {cargando ? (
              <tr><td colSpan="5" className="p-4 text-center text-gray-500">Cargando...</td></tr>
            ) : articulos.length > 0 ? (
              articulos.map(item => (
                <tr key={item.id} className="border-t">
                  <td className="px-3 py-2 font-medium">{item.producto.nombre}</td>
                  <td className="px-3 py-2 text-sm text-gray-600">{item.producto.codigo}</td>
                  <td className="px-3 py-2 text-sm">{item.cantidad}</td>
                  <td className="px-3 py-2 text-sm">{item.reservado}</td>
                  <td className="px-3 py-2 text-sm font-bold">{item.disponible}</td>
                </tr>
              ))
            ) : (
              <tr><td colSpan="5" className="p-4 text-center text-gray-500">Este almacén no tiene inventario.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Modal>
  );
}