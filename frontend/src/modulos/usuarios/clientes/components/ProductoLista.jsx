// frontend/src/modulos/usuarios/clientes/components/ProductoLista.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import productosService from '../../../../services/productosService'; // ¡Importa tu servicio!
import carritoService from '../../../../services/carritosService';

// --- Componente para la Tarjeta de un Producto ---
const ProductCard = ({ product, onClick }) => {
    const navigate = useNavigate();

    const handleAddToCart = async () => {
        try {
            await carritoService.agregarItem(product.id, 1); // Añade el producto con cantidad 1
            console.log(`Producto añadido al carrito: ${product.nombre}`);
            alert('Producto añadido al carrito'); // Notificación en lugar de redirección
        } catch (error) {
            console.error('Error al añadir al carrito:', error);
            alert('Hubo un problema al añadir el producto al carrito.');
        }
    };

    const imageUrl = product.imagen_principal_url || 'https://via.placeholder.com/400';

    return (
        <div
            className="group relative border rounded-md overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300 bg-white flex flex-col w-64 h-80 cursor-pointer"
            onClick={onClick}
        >
            <div className="relative w-full h-48 bg-gray-200 overflow-hidden flex items-center justify-center">
                {imageUrl ? (
                    <img
                        src={imageUrl}
                        alt={product.nombre || 'Imagen del producto'}
                        className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
                    />
                ) : (
                    <span className="text-gray-500 text-sm">Sin imagen</span>
                )}
            </div>
            <div className="p-4 flex flex-col flex-grow">
                <h3 className="text-md font-semibold text-gray-800 group-hover:text-indigo-600 transition-colors">
                    {product.nombre}
                </h3>
                <p className="text-sm text-gray-500 mt-1">{product.categoria?.nombre || 'Categoría'}</p>
                <div className="flex-grow"></div>
                <div className="mt-2">
                    {product.precio_original && (
                        <p className="text-sm line-through text-gray-400">${parseFloat(product.precio_original).toFixed(2)}</p>
                    )}
                    <p className="text-lg font-bold text-gray-900">${parseFloat(product.precio).toFixed(2)}</p>
                </div>
            </div>
            <div className="p-3 pt-0">
                <button
                    onClick={(e) => {
                        e.stopPropagation(); // Evita que se active el evento onClick del contenedor
                        handleAddToCart();
                    }}
                    className="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                    Añadir al carrito
                </button>
            </div>
        </div>
    );
};

// --- Componente Modal para Detalles del Producto ---
const ProductModal = ({ product, onClose }) => {
    const [cantidad, setCantidad] = useState(1);

    const handleAddToCart = async () => {
        try {
            await carritoService.agregarItem(product.id, cantidad); // Añade el producto con la cantidad seleccionada
            console.log(`Añadido al carrito: ${product.nombre} (Cantidad: ${cantidad})`);
            alert('Producto añadido al carrito');
            onClose();
        } catch (error) {
            console.error('Error al añadir al carrito:', error);
            alert('Hubo un problema al añadir el producto al carrito.');
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
            <div className="bg-white rounded-lg shadow-lg w-11/12 md:w-2/3 lg:w-1/2 flex flex-col md:flex-row">
                <div className="md:w-1/2 w-full h-64 md:h-auto bg-gray-200 overflow-hidden flex items-center justify-center">
                    <img
                        src={product.imagen_principal_url || 'https://via.placeholder.com/400'}
                        alt={product.nombre}
                        className="w-full h-full object-cover object-center"
                    />
                </div>
                <div className="md:w-1/2 w-full flex flex-col">
                    <div className="p-4 border-b flex justify-between items-center">
                        <h2 className="text-xl font-bold text-gray-800">{product.nombre}</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-500 hover:text-gray-800 focus:outline-none"
                        >
                            ✕
                        </button>
                    </div>
                    <div className="p-4 flex-grow">
                        <p className="text-lg font-bold text-gray-900 mb-2">Precio: ${parseFloat(product.precio).toFixed(2)}</p>
                        {product.precio_original && (
                            <p className="text-sm line-through text-gray-400 mb-2">Precio original: ${parseFloat(product.precio_original).toFixed(2)}</p>
                        )}
                        <p className="text-gray-600 text-sm mb-4">Descripción: {product.descripcion || 'Sin descripción disponible.'}</p>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setCantidad(Math.max(1, cantidad - 1))}
                                className="px-2 py-1 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                            >
                                -
                            </button>
                            <span className="text-sm text-gray-800">{cantidad}</span>
                            <button
                                onClick={() => setCantidad(cantidad + 1)}
                                className="px-2 py-1 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                            >
                                +
                            </button>
                        </div>
                    </div>
                    <div className="p-4 border-t">
                        <button
                            onClick={handleAddToCart}
                            className="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Añadir al carrito
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- Componente Principal de la Lista de Productos ---
export default function ProductList() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedProduct, setSelectedProduct] = useState(null);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoading(true);
                const data = await productosService.listar();
                console.log("Productos obtenidos:", data); // Registro para depuración
                setProducts(data.results || data);
                setError(null);
            } catch (err) {
                setError("No se pudieron cargar los productos. Intenta de nuevo más tarde.");
                console.error("Error fetching products:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    if (loading) return <div className="text-center py-12 text-gray-500">Cargando productos...</div>;
    if (error) return <div className="text-center py-12 text-red-600 bg-red-50 p-4 rounded-md">{error}</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8">Novedades</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-10">
                {products.length > 0 ? (
                    products.map(product => (
                        <ProductCard
                            key={product.id}
                            product={product}
                            onClick={() => setSelectedProduct(product)}
                        />
                    ))
                ) : (
                    <p>No hay productos disponibles en este momento.</p>
                )}
            </div>

            {selectedProduct && (
                <ProductModal
                    product={selectedProduct}
                    onClose={() => setSelectedProduct(null)}
                />
            )}
        </div>
    );
}