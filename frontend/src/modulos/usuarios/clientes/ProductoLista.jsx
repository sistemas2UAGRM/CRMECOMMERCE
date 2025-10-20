import React, { useState, useEffect } from 'react';
import productosService from '../../../services/productosService'; // ¡Importa tu servicio!

// --- Componente para la Tarjeta de un Producto ---
const ProductCard = ({ product }) => (
    <div className="group relative border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-shadow duration-300 bg-white flex flex-col">
        <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden">
            <img
                src={product.imagenes_payload?.[0]?.url || 'https://via.placeholder.com/400'}
                alt={product.nombre}
                className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
            />
        </div>
        <div className="p-4 flex flex-col flex-grow">
            <h3 className="text-md font-semibold text-gray-800">
                <a href="#"> {/* Idealmente, aquí va el link al detalle del producto */}
                    <span aria-hidden="true" className="absolute inset-0" />
                    {product.nombre}
                </a>
            </h3>
            <p className="text-sm text-gray-500 mt-1">{product.categoria?.nombre || 'Categoría'}</p>
            <div className="flex-grow"></div> {/* Empuja el precio hacia abajo */}
            <p className="text-lg font-bold text-gray-900 mt-2">${parseFloat(product.precio_venta).toFixed(2)}</p>
        </div>
         <div className="p-4 pt-0">
             <button className="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                Añadir al carrito
            </button>
        </div>
    </div>
);

// --- Componente Principal de la Lista de Productos ---
export default function ProductList() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoading(true);
                const data = await productosService.listar(); // Usa tu función 'listar'
                setProducts(data.results || data); // Funciona con y sin paginación
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
                        <ProductCard key={product.id} product={product} />
                    ))
                ) : (
                    <p>No hay productos disponibles en este momento.</p>
                )}
            </div>
        </div>
    );
}