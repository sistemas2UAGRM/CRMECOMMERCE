// src/modulos/productos/Productos.jsx
import React, { useEffect, useState } from "react";
import {
  PlusCircle, Edit, Trash2, Search as SearchIcon,
  Image as ImageIcon, X, Package, FolderOpen, Tags
} from "lucide-react";
import api from '../../services/api';
import { toast } from 'react-hot-toast';

// Estado inicial del formulario para poder resetearlo fácilmente
const INITIAL_FORM_STATE = {
  nombre: "",
  descripcion: "",
  precio_venta: "",
  garantia: "",
  categoria_id: "",
  stock: {
    stock_min: "",
    stock_actual: ""
  }
};

// Estado inicial para formulario de categorías
const INITIAL_CATEGORY_FORM_STATE = {
  nombre: "",
  descripcion: ""
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
  const [categorias, setCategorias] = useState([]);

  // Estados para sistema de pestañas
  const [activeTab, setActiveTab] = useState("productos"); // "productos" | "categorias"

  // Estados para gestión de categorías
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [categoryFormMode, setCategoryFormMode] = useState("create"); // 'create' | 'edit'
  const [currentCategory, setCurrentCategory] = useState(null);
  const [categoryFormState, setCategoryFormState] = useState(INITIAL_CATEGORY_FORM_STATE);
  const [categoryFormError, setCategoryFormError] = useState(null);
  const [categoriesLoading, setCategoriesLoading] = useState(false);

  // Función para obtener las categorías de la API
  const fetchCategorias = async () => {
    try {
      const { data } = await api.get("/ecommerce/categorias/");
      setCategorias(data.results || data);
    } catch (err) {
      console.error("Error al cargar categorías:", err);
      toast.error("Error al cargar categorías.");
    }
  };

  // Función para obtener los productos de la API
  const fetchProducts = async (currentPage = 1, searchQuery = "") => {
    setLoading(true);
    setFormError(null);
    try {
      const { data } = await api.get("/ecommerce/productos/", {
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

  // Carga inicial de productos y categorías
  useEffect(() => {
    fetchProducts(1, "");
    fetchCategorias();
  }, []);

  // Handler para la búsqueda
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1); // Resetea a la página 1 en cada nueva búsqueda
    fetchProducts(1, query);
  };

  // Resetea el formulario y cierra el modal
  const resetFormAndClose = () => {
    setFormState({ ...INITIAL_FORM_STATE });
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
  const openEditModal = async (product) => {
    // Si el producto viene del listado, necesitamos obtener el detalle completo
    let productDetail = product;

    if (!product.descripcion || !product.stock?.stock_min) {
      try {
        const { data } = await api.get(`/ecommerce/productos/${product.id}/`);
        productDetail = data;
      } catch (err) {
        console.error("Error al cargar detalle del producto:", err);
        toast.error("Error al cargar los detalles del producto");
        return;
      }
    }

    setFormState({
      nombre: productDetail.nombre || "",
      descripcion: productDetail.descripcion || "",
      precio_venta: productDetail.precio_venta ?? "",
      garantia: productDetail.garantia || "",
      categoria_id: productDetail.categoria?.id || "",
      stock: {
        stock_min: productDetail.stock?.stock_min ?? "",
        stock_actual: productDetail.stock?.stock_actual ?? ""
      }
    });
    setCurrentProduct(productDetail);
    setFormMode("edit");
    setShowFormModal(true);
  };

  // Elimina un producto
  const handleDelete = async (productId) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este producto?")) return;

    try {
      await api.delete(`/ecommerce/productos/${productId}/`);
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

    // Manejar campos de stock anidados
    if (name === "stock_min" || name === "stock_actual") {
      setFormState((prev) => ({
        ...prev,
        stock: {
          ...prev.stock,
          [name]: value
        }
      }));
    } else {
      setFormState((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    }
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
    const url = isCreating ? "/ecommerce/productos/" : `/ecommerce/productos/${currentProduct.id}/`;
    const method = isCreating ? 'post' : 'patch';

    // Validaciones básicas
    if (!formState.nombre.trim()) {
      setFormError("El nombre es requerido");
      return;
    }
    if (!formState.categoria_id) {
      setFormError("Debe seleccionar una categoría");
      return;
    }
    if (!formState.precio_venta || parseFloat(formState.precio_venta) <= 0) {
      setFormError("El precio debe ser mayor a 0");
      return;
    }

    // Preparar los datos según el formato del backend
    let dataPayload;

    if (isCreating) {
      // Para crear: incluir todos los campos incluido stock
      dataPayload = {
        nombre: formState.nombre.trim(),
        descripcion: formState.descripcion.trim(),
        precio_venta: parseFloat(formState.precio_venta),
        garantia: formState.garantia.trim(),
        categoria_id: parseInt(formState.categoria_id),
        stock: {
          stock_min: parseInt(formState.stock.stock_min) || 0,
          stock_actual: parseInt(formState.stock.stock_actual) || 0
        }
      };
    } else {
      // Para editar: solo campos del producto (el stock se actualiza por separado si es necesario)
      dataPayload = {
        nombre: formState.nombre.trim(),
        descripcion: formState.descripcion.trim(),
        precio_venta: parseFloat(formState.precio_venta),
        garantia: formState.garantia.trim(),
        categoria_id: parseInt(formState.categoria_id)
      };
    }

    const config = {
      headers: { "Content-Type": "application/json" }
    }; try {
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

  // ===============================
  // FUNCIONES PARA GESTIÓN DE CATEGORÍAS
  // ===============================

  // Resetea el formulario de categorías y cierra el modal
  const resetCategoryFormAndClose = () => {
    setCategoryFormState({ ...INITIAL_CATEGORY_FORM_STATE });
    setCurrentCategory(null);
    setCategoryFormMode("create");
    setShowCategoryModal(false);
    setCategoryFormError(null);
  };

  // Abre el modal para crear una nueva categoría
  const openCreateCategoryModal = () => {
    resetCategoryFormAndClose();
    setCategoryFormMode("create");
    setShowCategoryModal(true);
  };

  // Abre el modal para editar una categoría existente
  const openEditCategoryModal = (category) => {
    setCategoryFormState({
      nombre: category.nombre || "",
      descripcion: category.descripcion || ""
    });
    setCurrentCategory(category);
    setCategoryFormMode("edit");
    setShowCategoryModal(true);
  };

  // Elimina una categoría
  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar esta categoría?")) return;

    try {
      await api.delete(`/ecommerce/categorias/${categoryId}/`);
      toast.success("Categoría eliminada.");
      fetchCategorias(); // Recargar categorías
    } catch (err) {
      console.error(err);
      if (err.response?.status === 400) {
        toast.error("No se puede eliminar: la categoría tiene productos asociados.");
      } else {
        toast.error("Error al eliminar la categoría.");
      }
    }
  };

  // Maneja los cambios en los inputs del formulario de categoría
  const handleCategoryFormChange = (e) => {
    const { name, value } = e.target;
    setCategoryFormState((prev) => ({ ...prev, [name]: value }));
  };

  // Envía el formulario de categoría (crear o editar)
  const handleCategoryFormSubmit = async (e) => {
    e.preventDefault();
    setCategoryFormError(null);

    const isCreating = categoryFormMode === "create";
    const url = isCreating ? "/ecommerce/categorias/" : `/ecommerce/categorias/${currentCategory.id}/`;
    const method = isCreating ? 'post' : 'patch';

    // Validaciones básicas
    if (!categoryFormState.nombre.trim()) {
      setCategoryFormError("El nombre es requerido");
      return;
    }

    const dataPayload = {
      nombre: categoryFormState.nombre.trim(),
      descripcion: categoryFormState.descripcion.trim()
    };

    try {
      await api[method](url, dataPayload, {
        headers: { "Content-Type": "application/json" }
      });
      toast.success(`Categoría ${isCreating ? "creada" : "actualizada"} con éxito.`);
      resetCategoryFormAndClose();
      fetchCategorias(); // Recargar categorías
    } catch (err) {
      console.error("Error submitting category form:", err.response?.data || err.message);
      const apiErrors = err.response?.data;
      if (typeof apiErrors === 'object' && apiErrors !== null) {
        const errorMessages = Object.entries(apiErrors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join(' ');
        setCategoryFormError(`Error: ${errorMessages}`);
      } else {
        setCategoryFormError("Error al guardar la categoría. Revisa los datos.");
      }
      toast.error("Error al guardar la categoría.");
    }
  };

  return (
    <div className="p-4 space-y-6">
      {/* Cabecera del Módulo */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Productos y Categorías</h2>

        {/* Sistema de Pestañas */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("productos")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === "productos"
                  ? "border-[#2e7e8b] text-[#2e7e8b]"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
            >
              <div className="flex items-center gap-2">
                <Package size={18} />
                Productos ({products.length})
              </div>
            </button>
            <button
              onClick={() => setActiveTab("categorias")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === "categorias"
                  ? "border-[#2e7e8b] text-[#2e7e8b]"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
            >
              <div className="flex items-center gap-2">
                <Tags size={18} />
                Categorías ({categorias.length})
              </div>
            </button>
          </nav>
        </div>

        {/* Barra de acciones según la pestaña activa */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {activeTab === "productos" && (
              <form onSubmit={handleSearchSubmit} className="relative">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Buscar productos..."
                  className="rounded-full border border-gray-300 px-4 py-2 pl-10 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
                />
                <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </form>
            )}
          </div>

          <div className="flex items-center gap-2">
            {activeTab === "productos" ? (
              <button
                onClick={openCreateModal}
                className="inline-flex items-center gap-2 rounded-md bg-[#f0a831] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-opacity-90 transition"
              >
                <PlusCircle size={18} /> Nuevo Producto
              </button>
            ) : (
              <button
                onClick={openCreateCategoryModal}
                className="inline-flex items-center gap-2 rounded-md bg-[#2e7e8b] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-opacity-90 transition"
              >
                <PlusCircle size={18} /> Nueva Categoría
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Contenido de las Pestañas */}
      {activeTab === "productos" && (
        <>
          {/* Tabla de Productos */}
          <div className="bg-white rounded-lg shadow overflow-x-auto">
            <table className="w-full table-auto">
              <thead className="bg-gray-50 text-left text-gray-600 uppercase text-sm">
                <tr>
                  <th className="px-6 py-3">#</th>
                  <th className="px-6 py-3">Imagen</th>
                  <th className="px-6 py-3">Nombre</th>
                  <th className="px-6 py-3">Categoría</th>
                  <th className="px-6 py-3">Precio</th>
                  <th className="px-6 py-3">Stock Disponible</th>
                  <th className="px-6 py-3">Disponibilidad</th>
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
                      <td className="px-6 py-4 font-medium text-gray-900">{prod.nombre}</td>
                      <td className="px-6 py-4 text-gray-700">
                        {/* El backend devuelve categoria como string en lista, objeto en detalle */}
                        {typeof prod.categoria === 'string' ? prod.categoria : prod.categoria?.nombre || 'Sin categoría'}
                      </td>
                      <td className="px-6 py-4 text-gray-700">${parseFloat(prod.precio_venta || 0).toFixed(2)}</td>
                      <td className="px-6 py-4 text-gray-700">
                        {/* El backend devuelve stock_disponible en lista, stock.stock_actual en detalle */}
                        {prod.stock_disponible !== undefined ? prod.stock_disponible : (prod.stock?.stock_actual || 0)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${(prod.disponible !== undefined ? prod.disponible : (prod.activo !== undefined ? prod.activo : true))
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                          }`}>
                          {(prod.disponible !== undefined ? prod.disponible : (prod.activo !== undefined ? prod.activo : true)) ? "Disponible" : "No disponible"}
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
        </>
      )}

      {/* Pestaña de Categorías */}
      {activeTab === "categorias" && (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="w-full table-auto">
            <thead className="bg-gray-50 text-left text-gray-600 uppercase text-sm">
              <tr>
                <th className="px-6 py-3">#</th>
                <th className="px-6 py-3">Nombre</th>
                <th className="px-6 py-3">Descripción</th>
                <th className="px-6 py-3">Productos</th>
                <th className="px-6 py-3">Fecha Creación</th>
                <th className="px-6 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {categoriesLoading ? (
                <tr><td className="p-6 text-center text-gray-500" colSpan={6}>Cargando categorías...</td></tr>
              ) : categorias.length === 0 ? (
                <tr><td className="p-6 text-center text-gray-500" colSpan={6}>No se encontraron categorías.</td></tr>
              ) : (
                categorias.map((categoria, index) => (
                  <tr key={categoria.id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-500">{index + 1}</td>
                    <td className="px-6 py-4 font-medium text-gray-900">{categoria.nombre}</td>
                    <td className="px-6 py-4 text-gray-700">
                      {categoria.descripcion || <span className="text-gray-400 italic">Sin descripción</span>}
                    </td>
                    <td className="px-6 py-4 text-gray-700">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {categoria.productos_count || 0} productos
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-700 text-sm">
                      {categoria.fecha_creacion ? new Date(categoria.fecha_creacion).toLocaleDateString('es-ES') : 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-3">
                        <button
                          onClick={() => openEditCategoryModal(categoria)}
                          title="Editar"
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteCategory(categoria.id)}
                          title="Eliminar"
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal del Formulario */}
      {showFormModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-2xl animate-fade-in-down">
            <div className="flex items-center justify-between pb-3 border-b">
              <h3 className="text-xl font-semibold text-gray-800">
                {formMode === "create" ? "Crear Nuevo Producto" : `Editar: ${currentProduct?.nombre}`}
              </h3>
              <button onClick={resetFormAndClose} className="p-1 rounded-full hover:bg-gray-100"><X size={20} className="text-gray-600" /></button>
            </div>
            <form className="mt-4" onSubmit={handleFormSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                  <input id="nombre" name="nombre" value={formState.nombre} onChange={handleFormChange} placeholder="Ej: Laptop Pro" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" required />
                </div>
                <div>
                  <label htmlFor="categoria_id" className="block text-sm font-medium text-gray-700 mb-1">
                    Categoría
                    {categorias.length === 0 && <span className="text-xs text-red-500 ml-1">(Cargando...)</span>}
                  </label>
                  <select
                    id="categoria_id"
                    name="categoria_id"
                    value={formState.categoria_id}
                    onChange={handleFormChange}
                    className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                    required
                    disabled={categorias.length === 0}
                  >
                    <option value="">
                      {categorias.length === 0 ? "Cargando categorías..." : "Seleccione una categoría"}
                    </option>
                    {categorias.map((categoria) => (
                      <option key={categoria.id} value={categoria.id}>
                        {categoria.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="precio_venta" className="block text-sm font-medium text-gray-700 mb-1">Precio de Venta</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                    <input
                      id="precio_venta"
                      name="precio_venta"
                      value={formState.precio_venta}
                      onChange={handleFormChange}
                      type="number"
                      step="0.01"
                      min="0.01"
                      placeholder="999.99"
                      className="w-full rounded border-gray-300 pl-8 pr-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="garantia" className="block text-sm font-medium text-gray-700 mb-1">Garantía</label>
                  <input id="garantia" name="garantia" value={formState.garantia} onChange={handleFormChange} placeholder="Ej: 1 año" className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
                </div>
                <div>
                  <label htmlFor="stock_actual" className="block text-sm font-medium text-gray-700 mb-1">
                    Stock Actual {formMode === "edit" && <span className="text-xs text-gray-500">(cantidad disponible)</span>}
                  </label>
                  <input
                    id="stock_actual"
                    name="stock_actual"
                    value={formState.stock.stock_actual}
                    onChange={handleFormChange}
                    type="number"
                    min="0"
                    placeholder="Ej: 50"
                    className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="stock_min" className="block text-sm font-medium text-gray-700 mb-1">
                    Stock Mínimo {formMode === "edit" && <span className="text-xs text-gray-500">(alerta de reposición)</span>}
                  </label>
                  <input
                    id="stock_min"
                    name="stock_min"
                    value={formState.stock.stock_min}
                    onChange={handleFormChange}
                    type="number"
                    min="0"
                    placeholder="Ej: 10"
                    className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea id="descripcion" name="descripcion" value={formState.descripcion} onChange={handleFormChange} rows="3" placeholder="Descripción detallada del producto..." className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]" />
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

      {/* Modal del Formulario de Categoría */}
      {showCategoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-2xl animate-fade-in-down">
            <div className="flex items-center justify-between pb-3 border-b">
              <h3 className="text-xl font-semibold text-gray-800">
                {categoryFormMode === "create" ? "Crear Nueva Categoría" : `Editar: ${currentCategory?.nombre}`}
              </h3>
              <button onClick={resetCategoryFormAndClose} className="p-1 rounded-full hover:bg-gray-100">
                <X size={20} className="text-gray-600" />
              </button>
            </div>
            <form className="mt-4 space-y-4" onSubmit={handleCategoryFormSubmit}>
              <div>
                <label htmlFor="category-nombre" className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de la Categoría
                </label>
                <input
                  id="category-nombre"
                  name="nombre"
                  value={categoryFormState.nombre}
                  onChange={handleCategoryFormChange}
                  placeholder="Ej: Electrónicos"
                  className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                  required
                />
              </div>
              <div>
                <label htmlFor="category-descripcion" className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción (Opcional)
                </label>
                <textarea
                  id="category-descripcion"
                  name="descripcion"
                  value={categoryFormState.descripcion}
                  onChange={handleCategoryFormChange}
                  rows="3"
                  placeholder="Descripción de la categoría..."
                  className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                />
              </div>
              {categoryFormError && (
                <div className="mt-3 text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">
                  {categoryFormError}
                </div>
              )}
              <div className="flex items-center justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={resetCategoryFormAndClose}
                  className="px-4 py-2 rounded-md border bg-gray-50 text-gray-700 font-medium hover:bg-gray-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-md bg-[#2e7e8b] text-white font-semibold hover:bg-[#256a76]"
                >
                  {categoryFormMode === "create" ? "Crear Categoría" : "Guardar Cambios"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}