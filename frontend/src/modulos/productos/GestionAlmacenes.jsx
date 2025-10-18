import React, { useEffect, useState } from "react";
import almacenesService from "../../services/almacenesService";
import movimientosService from "../../services/movimientosService";
import Modal from "./Modal";

export default function GestionAlmacenes() {
  const [almacenes, setAlmacenes] = useState([]);
  const [selectedAlmacen, setSelectedAlmacen] = useState(null);
  const [articulos, setArticulos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [abiertoAjuste, setAbiertoAjuste] = useState(false);
  const [ajusteData, setAjusteData] = useState({ producto: null, almacen: null, cantidad: 0, tipo: "ajuste", referencia: "" });

  useEffect(() => {
    (async () => {
      setCargando(true);
      try {
        const lista = await almacenesService.listar();
        setAlmacenes(lista);
      } catch (err) {
        console.error(err);
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  const verArticulos = async (alm) => {
    setSelectedAlmacen(alm);
    try {
      const items = await almacenesService.articulos(alm.id);
      setArticulos(items);
    } catch (err) {
      console.error(err);
      setArticulos([]);
    }
  };

  const abrirAjuste = (producto, almacen) => {
    setAjusteData({ producto: producto.id, almacen: almacen.id, cantidad: 0, tipo: "ajuste", referencia: "", producto_obj: producto });
    setAbiertoAjuste(true);
  };

  const submitAjuste = async () => {
    try {
      const payload = {
        producto: ajusteData.producto,
        almacen: ajusteData.almacen,
        cantidad: Number(ajusteData.cantidad),
        tipo: ajusteData.tipo,
        referencia: ajusteData.referencia
      };
      await movimientosService.crear(payload);
      alert("Movimiento registrado");
      setAbiertoAjuste(false);
      // recargar articulos
      if (selectedAlmacen) await verArticulos(selectedAlmacen);
    } catch (err) {
      console.error(err);
      alert("Error registrando movimiento: " + (err?.response?.data || err.message));
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Gestión de Almacenes</h1>
      </div>

      {cargando ? <div>Cargando almacenes...</div> : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h3 className="font-semibold mb-2">Almacenes</h3>
            <ul className="border rounded p-2">
              {almacenes.map(a => (
                <li key={a.id} className="py-2 flex justify-between items-center">
                  <div>
                    <div className="font-medium">{a.nombre}</div>
                    <div className="text-xs text-gray-500">{a.codigo}</div>
                  </div>
                  <button onClick={() => verArticulos(a)} className="px-2 py-1 border rounded text-sm">Ver</button>
                </li>
              ))}
            </ul>
          </div>

          <div className="md:col-span-2">
            <h3 className="font-semibold mb-2">Artículos en {selectedAlmacen ? selectedAlmacen.nombre : "..."}</h3>
            {!selectedAlmacen && <div className="text-sm text-gray-500">Selecciona un almacén.</div>}
            {selectedAlmacen && (
              <div className="overflow-auto border rounded">
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left">Producto</th>
                      <th className="px-3 py-2 text-left">SKU</th>
                      <th className="px-3 py-2 text-left">Cantidad</th>
                      <th className="px-3 py-2 text-left">Reservado</th>
                      <th className="px-3 py-2 text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {articulos.map(it => (
                      <tr key={it.id} className="border-t">
                        <td className="px-3 py-2">{it.producto.nombre}</td>
                        <td className="px-3 py-2">{it.producto.codigo}</td>
                        <td className="px-3 py-2">{it.cantidad}</td>
                        <td className="px-3 py-2">{it.reservado}</td>
                        <td className="px-3 py-2 text-right">
                          <button onClick={() => abrirAjuste(it.producto, selectedAlmacen)} className="px-2 py-1 rounded bg-indigo-600 text-white text-sm">Ajustar</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      <Modal abierto={abiertoAjuste} titulo="Registrar movimiento de stock" onCerrar={() => setAbiertoAjuste(false)}>
        <div>
          <p className="mb-2"><strong>Producto:</strong> {ajusteData.producto_obj ? ajusteData.producto_obj.nombre : ""}</p>
          <div className="space-y-2">
            <div>
              <label className="block text-sm">Tipo</label>
              <select value={ajusteData.tipo} onChange={(e) => setAjusteData(prev => ({...prev, tipo: e.target.value}))} className="w-full border rounded p-2">
                <option value="entrada">Entrada</option>
                <option value="salida">Salida</option>
                <option value="ajuste">Ajuste</option>
              </select>
            </div>
            <div>
              <label className="block text-sm">Cantidad (usar negativo para restar si usas API que lo permita)</label>
              <input type="number" value={ajusteData.cantidad} onChange={(e) => setAjusteData(prev => ({...prev, cantidad: e.target.value}))} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm">Referencia</label>
              <input value={ajusteData.referencia} onChange={(e) => setAjusteData(prev => ({...prev, referencia: e.target.value}))} className="w-full border rounded p-2" />
            </div>
            <div className="flex justify-end space-x-2 mt-3">
              <button onClick={() => setAbiertoAjuste(false)} className="px-4 py-2 border rounded">Cancelar</button>
              <button onClick={submitAjuste} className="px-4 py-2 bg-green-600 text-white rounded">Registrar</button>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
