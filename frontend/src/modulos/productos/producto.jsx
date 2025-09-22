// src/modulos/productos/Productos.jsx
import React, { useEffect, useState } from "react";
import { 
  PlusCircle, Edit, Trash2, Search as SearchIcon, 
  Image as ImageIcon, X 
} from "lucide-react";
import api from '../../services/api'; 
import { toast } from 'react-hot-toast'; 

// Estado inicial del formulario para poder resetearlo fácilmente
const INITIAL_FORM_STATE = {
  name: "",
  sku: "",
  price: "",
  stock: "",
  category: "",
  description: "",
  active: true,
};

export default function Productos() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageInfo, setPageInfo] = useState({ next: null, previous: null, count: 0 });
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  
  const [showFormModal, setShowFormModal] = useState(false);
  const [formMode, setFormMode] = useState("create"); // 'create' | 'edit'
  const [currentProduct, setCurrentProduct] = useState(null); // Almacena el producto que se está editando
  const [formState, setFormState] = useState(INITIAL_FORM_STATE);
  const [imageFile, setImageFile] = useState(null);
  const [formError, setFormError] = useState(null);

  // Función para obtener los productos de la API
  const fetchProducts = async (currentPage = 1, searchQuery = "") => {
    setLoading(true);
    setFormError(null);
    try {
      const { data } = await api.get("/products/", { 
        params: { page: currentPage, search: searchQuery } 
      });
      setProducts(data.results || data); // Compatible con API paginada o simple
      setPageInfo({ 
        next: data.next, 
        previous: data.previous, 
        count: data.count || (Array.isArray(data) ? data.length : 0) 
      });
      setPage(currentPage);
    } catch (err) {
      console.error(err);
      setFormError("Error al cargar productos.");
      toast.error("Error al cargar productos.");
    } finally {
      setLoading(false);
    }
  };

  // Carga inicial de productos
  useEffect(() => {
    fetchProducts(1, "");
  }, []);

  // Handler para la búsqueda
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1); // Resetea a la página 1 en cada nueva búsqueda
    fetchProducts(1, query);
  };
  
  // Resetea el formulario y cierra el modal
  const resetFormAndClose = () => {
    setFormState(INITIAL_FORM_STATE);
    setImageFile(null);
    setCurrentProduct(null);
    setFormMode("create");
    setShowFormModal(false);
    setFormError(null);
  };

  // Abre el modal para crear un nuevo producto
  const openCreateModal = () => {
    resetFormAndClose();
    setFormMode("create");
    setShowFormModal(true);
  };

  // Abre el modal para editar un producto existente
  const openEditModal = (product) => {
    setFormState({
      name: product.name || "",
      sku: product.sku || "",
      price: product.price ?? "",
      stock: product.stock ?? "",
      category: product.category || "",
      description: product.description || "",
      active: product.active ?? true,
    });
    setCurrentProduct(product);
    setFormMode("edit");
    setShowFormModal(true);
  };

  // Elimina un producto
  const handleDelete = async (productId) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este producto?")) return;
    
    try {
      await api.delete(`/products/${productId}/`);
      toast.success("Producto eliminado.");
      fetchProducts(page, query); // Recargar datos
    } catch (err) {
      console.error(err);
      toast.error("Error al eliminar el producto.");
    }
  };

  // Maneja los cambios en los inputs del formulario
  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormState((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };
  
  // Maneja la subida de la imagen
  const handleImageChange = (e) => {
    setImageFile(e.target.files[0] || null);
  };
  
  // Envía el formulario (crear o editar)
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);

    const isCreating = formMode === "create";
    const url = isCreating ? "/products/" : `/products/${currentProduct.id}/`;
    const method = isCreating ? 'post' : 'patch';
    
    let dataPayload;
    const config = {};

    if (imageFile) {
      dataPayload = new FormData();
      Object.keys(formState).forEach(key => dataPayload.append(key, formState[key]));
      dataPayload.append("image", imageFile);
      config.headers = { "Content-Type": "multipart/form-data" };
    } else {
      dataPayload = { ...formState };
    }
    
    try {
      await api[method](url, dataPayload, config);
      toast.success(`Producto ${isCreating ? "creado" : "actualizado"} con éxito.`);
      resetFormAndClose();
      // Vuelve a la primera página si se crea un producto, o se queda en la actual si edita
      fetchProducts(isCreating ? 1 : page, query);
    } catch (err) {
      console.error("Error submitting form:", err.response?.data || err.message);
      const apiErrors = err.response?.data;
      if (typeof apiErrors === 'object' && apiErrors !== null) {
        const errorMessages = Object.entries(apiErrors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join(' ');
        setFormError(`Error: ${errorMessages}`);
      } else {
        setFormError("Error al guardar el producto. Revisa los datos.");
      }
      toast.error("Error al guardar el producto.");
    }
  };

  return (
    <div className="p-4 space-y-6">
      {/* Cabecera del Módulo */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Productos</h2>
        <div className="flex items-center gap-4">
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar productos..."
              className="rounded-full border border-gray-300 px-4 py-2 pl-10 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
            />
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          </form>
          <button
            onClick={openCreateModal}
            className="inline-flex items-center gap-2 rounded-md bg-[#f0a831] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-opacity-90 transition"
          >
            <PlusCircle size={18} /> Nuevo Producto
          </button>
        </div>
      </div>

      {/* Tabla de Productos */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full table-auto">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-sm">
            <tr>
              <th className="px-6 py-3">#</th>
              <th className="px-6 py-3">Imagen</th>
              <th className="px-6 py-3">Nombre</th>
              <th className="px-6 py-3">SKU</th>
              <th className="px-6 py-3">Precio</th>
              <th className="px-6 py-3">Stock</th>
              <th className="px-6 py-3">Estado</th>
              <th className="px-6 py-3">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {loading ? (
              <tr><td className="p-6 text-center text-gray-500" colSpan={8}>Cargando...</td></tr>
            ) : products.length === 0 ? (
              <tr><td className="p-6 text-center text-gray-500" colSpan={8}>No se encontraron productos.</td></tr>
            ) : (
              products.map((prod, index) => (
                <tr key={prod.id || index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-500">{(page - 1) * 10 + index + 1}</td>
                  <td className="px-6 py-4">
                    {prod.image ? (
                      <img src={prod.image} alt={prod.name} className="h-12 w-12 object-cover rounded-md" />
                    ) : (
                      <div className="h-12 w-12 flex items-center justify-center rounded-md bg-gray-100 text-gray-400">
                        <ImageIcon size={24} />
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900">{prod.name}</td>
                  <td className="px-6 py-4 text-gray-700">{prod.sku}</td>
                  <td className="px-6 py-4 text-gray-700">${parseFloat(prod.price).toFixed(2)}</td>
                  <td className="px-6 py-4 text-gray-700">{prod.stock}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${prod.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {prod.active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-3">
                      <button onClick={() => openEditModal(prod)} title="Editar" className="text-blue-600 hover:text-blue-800"><Edit size={18} /></button>
                      <button onClick={() => handleDelete(prod.id)} title="Eliminar" className="text-red-600 hover:text-red-800"><Trash2 size={18} /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div>
          Mostrando <strong>{products.length}</strong> de <strong>{pageInfo.count}</strong> resultados
        </div>
        <div className="flex gap-2">
          <button onClick={() => setPage(page - 1)} disabled={!pageInfo.previous} className="px-4 py-2 rounded-md border bg-white disabled:opacity-50 disabled:cursor-not-allowed">Anterior</button>
          <button onClick={() => setPage(page + 1)} disabled={!pageInfo.next} className="px-4 py-2 rounded-md border bg-white disabled:opacity-50 disabled:cursor-not-allowed">Siguiente</button>
        </div>
      </div>

      {/* Modal del Formulario */}
      {showFormModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-2xl animate-fade-in-down">
            <div className="flex items-center justify-between pb-3 border-b">
              <h3 className="text-xl font-semibold text-gray-800">
                {formMode === "create" ? "Crear Nuevo Producto" : `Editar: ${currentProduct?.name}`}
              </h3>
              <button onClick={resetFormAndClose} className="p-1 rounded-full hover:bg-gray-100"><X size={20} className="text-gray-600" /></button>
            </div>
            <form className="mt-4" onSubmit={handleFormSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                  <input id="name" name="name" value={formState.name} onChange={handleFormChange} placeholder="Ej: Laptop Pro" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" required />
                </div>
                <div>
                  <label htmlFor="sku" className="block text-sm font-medium text-gray-700 mb-1">SKU</label>
                  <input id="sku" name="sku" value={formState.sku} onChange={handleFormChange} placeholder="Ej: LP-001" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
                </div>
                <div>
                  <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">Precio</label>
                  <input id="price" name="price" value={formState.price} onChange={handleFormChange} type="number" step="0.01" placeholder="Ej: 999.99" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
                </div>
                <div>
                  <label htmlFor="stock" className="block text-sm font-medium text-gray-700 mb-1">Stock</label>
                  <input id="stock" name="stock" value={formState.stock} onChange={handleFormChange} type="number" placeholder="Ej: 50" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
                </div>
                <div className="md:col-span-2">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea id="description" name="description" value={formState.description} onChange={handleFormChange} rows="3" placeholder="Descripción detallada del producto..." className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Imagen</label>
                  <input type="file" accept="image/*" onChange={handleImageChange} className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
                </div>
                <div className="flex items-center gap-2 self-end">
                  <input id="active" name="active" type="checkbox" checked={formState.active} onChange={handleFormChange} className="h-4 w-4 rounded border-gray-300 text-[#2e7e8b] focus:ring-[#2e7e8b]" />
                  <label htmlFor="active" className="text-sm font-medium text-gray-700">Activo</label>
                </div>
              </div>
              {formError && <div className="mt-3 text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">{formError}</div>}
              <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t">
                <button type="button" onClick={resetFormAndClose} className="px-4 py-2 rounded-md border bg-gray-50 text-gray-700 font-medium hover:bg-gray-100">Cancelar</button>
                <button type="submit" className="px-4 py-2 rounded-md bg-[#2e7e8b] text-white font-semibold hover:bg-[#256a76]">
                  {formMode === "create" ? "Crear Producto" : "Guardar Cambios"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}