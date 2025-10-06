// src/modulos/carrito/Carrito.jsx
import React, { useEffect, useState } from "react";
import {
  ShoppingCart, Plus, Minus, Trash2, Package2,
  CreditCard, ArrowRight, RefreshCw, AlertCircle,
  CheckCircle, Eye, X
} from "lucide-react";
import api from '../../services/api';
import { toast } from 'react-hot-toast';

export default function Carrito() {
  const [carrito, setCarrito] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  // Función para obtener el carrito del usuario
  const fetchCarrito = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get("/ecommerce/carritos/mi-carrito/");
      setCarrito(data);
    } catch (err) {
      console.error("Error al cargar carrito:", err);
      if (err.response?.status === 401) {
        setError("Debes iniciar sesión para ver tu carrito.");
      } else {
        setError("Error al cargar el carrito.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Función para actualizar cantidad de un producto
  const actualizarCantidad = async (productoId, nuevaCantidad) => {
    setUpdating(true);
    try {
      await api.patch("/ecommerce/carritos/actualizar-cantidad/", {
        producto_id: productoId,
        cantidad: nuevaCantidad
      });

      toast.success("Cantidad actualizada");
      fetchCarrito(); // Recargar carrito
    } catch (err) {
      console.error("Error al actualizar cantidad:", err);
      const errorMessage = err.response?.data?.error || "Error al actualizar cantidad";
      toast.error(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  // Función para eliminar producto del carrito
  const eliminarProducto = async (productoId) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este producto del carrito?")) {
      return;
    }

    setUpdating(true);
    try {
      await api.patch("/ecommerce/carritos/actualizar-cantidad/", {
        producto_id: productoId,
        cantidad: 0
      });

      toast.success("Producto eliminado del carrito");
      fetchCarrito(); // Recargar carrito
    } catch (err) {
      console.error("Error al eliminar producto:", err);
      const errorMessage = err.response?.data?.error || "Error al eliminar producto";
      toast.error(errorMessage);
    } finally {
      setUpdating(false);
    }
  };

  // Función para proceder al checkout
  const procederAlCheckout = () => {
    if (!carrito || carrito.productos.length === 0) {
      toast.error("No hay productos en el carrito");
      return;
    }

    // Aquí se implementaría la navegación al checkout
    toast.info("Funcionalidad de checkout próximamente");
  };

  // Cargar carrito al montar el componente
  useEffect(() => {
    fetchCarrito();
  }, []);

  // Función para formatear precio
  const formatearPrecio = (precio) => {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB'
    }).format(precio);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#2e7e8b] rounded-lg">
                <ShoppingCart size={24} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Mi Carrito de Compras</h1>
                <p className="text-gray-600">Gestiona tus productos seleccionados</p>
              </div>
            </div>

            <button
              onClick={fetchCarrito}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-200 transition disabled:opacity-50"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
              Actualizar
            </button>
          </div>
        </div>

        {/* Estado de carga */}
        {loading && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <div className="flex items-center justify-center">
              <RefreshCw className="animate-spin h-8 w-8 text-[#2e7e8b]" />
              <span className="ml-3 text-gray-600">Cargando carrito...</span>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle size={24} />
              <div>
                <h3 className="font-semibold">Error al cargar carrito</h3>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Contenido del carrito */}
        {!loading && !error && carrito && (
          <>
            {/* Carrito vacío */}
            {carrito.productos.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <Package2 size={48} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Tu carrito está vacío</h3>
                <p className="text-gray-600 mb-6">Agrega algunos productos para comenzar tu compra</p>
                <button className="inline-flex items-center gap-2 rounded-md bg-[#2e7e8b] px-6 py-3 text-white font-semibold hover:bg-[#256a76] transition">
                  <ShoppingCart size={20} />
                  Ver Productos
                </button>
              </div>
            ) : (
              <>
                {/* Lista de productos */}
                <div className="bg-white rounded-lg shadow-sm mb-6">
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-900">
                      Productos en tu carrito ({carrito.productos.length})
                    </h2>
                  </div>

                  <div className="divide-y divide-gray-200">
                    {carrito.productos.map((item, index) => (
                      <div key={index} className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 flex-1">
                            <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                              <Package2 size={24} className="text-gray-400" />
                            </div>

                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900">
                                {item.producto_nombre}
                              </h3>
                              <p className="text-sm text-gray-600">
                                SKU: {item.producto_sku || 'N/A'}
                              </p>
                              <p className="text-lg font-semibold text-[#2e7e8b]">
                                {formatearPrecio(item.precio_unitario)}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-4">
                            {/* Control de cantidad */}
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => actualizarCantidad(item.producto_id, item.cantidad - 1)}
                                disabled={updating || item.cantidad <= 1}
                                className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <Minus size={16} />
                              </button>

                              <span className="w-12 text-center font-semibold">
                                {item.cantidad}
                              </span>

                              <button
                                onClick={() => actualizarCantidad(item.producto_id, item.cantidad + 1)}
                                disabled={updating}
                                className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <Plus size={16} />
                              </button>
                            </div>

                            {/* Subtotal */}
                            <div className="text-right min-w-[100px]">
                              <p className="font-semibold text-gray-900">
                                {formatearPrecio(item.subtotal)}
                              </p>
                            </div>

                            {/* Botón eliminar */}
                            <button
                              onClick={() => eliminarProducto(item.producto_id)}
                              disabled={updating}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-md transition disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Eliminar producto"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Resumen del carrito */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumen del pedido</h2>

                  <div className="space-y-3">
                    <div className="flex justify-between text-gray-600">
                      <span>Subtotal ({carrito.total_productos} productos)</span>
                      <span>{formatearPrecio(carrito.subtotal || 0)}</span>
                    </div>

                    {carrito.descuento > 0 && (
                      <div className="flex justify-between text-green-600">
                        <span>Descuento</span>
                        <span>-{formatearPrecio(carrito.descuento)}</span>
                      </div>
                    )}

                    <div className="border-t pt-3">
                      <div className="flex justify-between text-lg font-semibold text-gray-900">
                        <span>Total</span>
                        <span>{formatearPrecio(carrito.total)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Botones de acción */}
                  <div className="mt-6 space-y-3">
                    <button
                      onClick={procederAlCheckout}
                      className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-[#2e7e8b] px-6 py-3 text-white font-semibold hover:bg-[#256a76] transition"
                    >
                      <CreditCard size={20} />
                      Proceder al Checkout
                      <ArrowRight size={16} />
                    </button>

                    <button className="w-full inline-flex items-center justify-center gap-2 rounded-md border border-gray-300 px-6 py-3 text-gray-700 font-semibold hover:bg-gray-50 transition">
                      <ShoppingCart size={20} />
                      Continuar Comprando
                    </button>
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {/* Indicador de actualización */}
        {updating && (
          <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 border">
            <div className="flex items-center gap-3">
              <RefreshCw className="animate-spin h-5 w-5 text-[#2e7e8b]" />
              <span className="text-sm font-medium">Actualizando carrito...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
