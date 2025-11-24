import React from 'react';
import {
    BookOpen,
    Package,
    Users,
    ShoppingCart,
    Bot,
    Shield,
    Calendar,
    MessageSquare,
    TrendingUp,
    HelpCircle,
    CheckCircle,
    Info,
    ArrowRight
} from 'lucide-react';

export default function ManualAdmin() {
    return (
        <div className="p-6 max-w-7xl mx-auto space-y-10">

            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-700 rounded-3xl p-10 text-white shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 opacity-10 transform translate-x-10 -translate-y-10">
                    <BookOpen size={300} />
                </div>
                <div className="relative z-10 flex items-center gap-6">
                    <div className="p-4 bg-white/20 rounded-2xl backdrop-blur-md shadow-inner">
                        <BookOpen size={48} />
                    </div>
                    <div>
                        <h1 className="text-4xl font-extrabold tracking-tight">Manual de Usuario</h1>
                        <p className="text-indigo-100 mt-3 text-xl font-light">Guía completa para dominar tu sistema de gestión</p>
                    </div>
                </div>
            </div>

            {/* Introducción */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
                <h2 className="text-2xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <Info className="text-indigo-500" /> ¿Cómo usar este manual?
                </h2>
                <p className="text-slate-600 text-lg leading-relaxed">
                    Bienvenido a la documentación oficial de tu plataforma. Hemos diseñado este sistema para que sea intuitivo, pero aquí encontrarás una explicación detallada de cada módulo.
                    Usa esta guía para capacitar a tu personal y sacar el máximo provecho a las herramientas de Inteligencia Artificial y CRM.
                </p>
            </div>

            {/* Secciones Detalladas */}
            <div className="grid gap-10">

                {/* Módulo 1: Productos */}
                <section className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
                    <div className="bg-blue-600 p-6 text-white flex items-center gap-4">
                        <Package size={32} />
                        <h3 className="text-2xl font-bold">1. Gestión de Productos e Inventario</h3>
                    </div>
                    <div className="p-8 grid md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <h4 className="text-xl font-semibold text-blue-700 flex items-center gap-2">
                                <CheckCircle size={20} /> Catálogo de Productos
                            </h4>
                            <p className="text-slate-600">
                                En la sección <strong>"Listado"</strong> puedes ver todos tus artículos.
                            </p>
                            <ul className="list-disc list-inside space-y-2 text-slate-700 ml-2">
                                <li><strong>Crear Nuevo:</strong> Pulsa el botón "Nuevo Producto". Deberás ingresar nombre, precio, descripción y subir una imagen atractiva.</li>
                                <li><strong>Editar:</strong> Si cambias de precio o descripción, usa el botón de lápiz en la tabla.</li>
                                <li><strong>Eliminar:</strong> Usa con precaución el botón de basura para retirar productos obsoletos.</li>
                            </ul>
                        </div>
                        <div className="space-y-4">
                            <h4 className="text-xl font-semibold text-blue-700 flex items-center gap-2">
                                <CheckCircle size={20} /> Organización y Stock
                            </h4>
                            <p className="text-slate-600">
                                Mantén tu tienda ordenada para que los clientes encuentren lo que buscan.
                            </p>
                            <ul className="list-disc list-inside space-y-2 text-slate-700 ml-2">
                                <li><strong>Categorías:</strong> Crea grupos como "Hombres", "Mujeres", "Accesorios". Un producto debe pertenecer a una categoría.</li>
                                <li><strong>Almacenes:</strong> Si tienes múltiples depósitos, registra aquí cuánto stock tienes en cada uno. El sistema descontará automáticamente al vender.</li>
                            </ul>
                        </div>
                    </div>
                </section>

                {/* Módulo 2: CRM */}
                <section className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
                    <div className="bg-purple-600 p-6 text-white flex items-center gap-4">
                        <Users size={32} />
                        <h3 className="text-2xl font-bold">2. CRM: Clientes y Relaciones</h3>
                    </div>
                    <div className="p-8 grid md:grid-cols-3 gap-8">
                        <div className="space-y-4">
                            <h4 className="text-lg font-bold text-purple-700">Calendario</h4>
                            <p className="text-sm text-slate-600">
                                Tu agenda personal. Haz clic en cualquier día para agregar un recordatorio, una llamada a un cliente o una reunión de equipo.
                            </p>
                        </div>
                        <div className="space-y-4">
                            <h4 className="text-lg font-bold text-purple-700">Base de Clientes</h4>
                            <p className="text-sm text-slate-600">
                                Accede a la ficha de cada cliente. Podrás ver su historial de compras, sus datos de contacto y notas importantes sobre sus preferencias.
                            </p>
                        </div>
                        <div className="space-y-4">
                            <h4 className="text-lg font-bold text-purple-700">Soporte (Tickets)</h4>
                            <p className="text-sm text-slate-600">
                                Cuando un cliente tenga un problema, crea un "Ticket". Así podrás dar seguimiento a su caso hasta que esté resuelto, mejorando su satisfacción.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Módulo 3: IA */}
                <section className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
                    <div className="bg-indigo-600 p-6 text-white flex items-center gap-4">
                        <Bot size={32} />
                        <h3 className="text-2xl font-bold">3. Inteligencia Artificial (Tu Asistente Virtual)</h3>
                    </div>
                    <div className="p-8 space-y-6">
                        <p className="text-lg text-slate-700">
                            Este sistema cuenta con una IA avanzada que te ayuda a tomar decisiones. No es magia, es análisis de datos simplificado.
                        </p>

                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-100">
                                <h4 className="text-xl font-bold text-indigo-800 mb-3 flex items-center gap-2">
                                    <MessageSquare /> Generador de Reportes
                                </h4>
                                <p className="text-slate-700 mb-4">
                                    Olvídate de filtros complejos. Escribe lo que necesitas saber en lenguaje natural.
                                </p>
                                <div className="bg-white p-4 rounded-lg border border-indigo-200 shadow-sm">
                                    <p className="text-xs font-bold text-indigo-500 uppercase mb-2">Ejemplos de preguntas:</p>
                                    <ul className="space-y-2 text-sm text-slate-700">
                                        <li className="flex items-center gap-2"><ArrowRight size={14} className="text-indigo-400" /> "¿Cuáles fueron los 5 productos más vendidos en diciembre?"</li>
                                        <li className="flex items-center gap-2"><ArrowRight size={14} className="text-indigo-400" /> "Dime qué clientes compraron más de $1000 este mes."</li>
                                        <li className="flex items-center gap-2"><ArrowRight size={14} className="text-indigo-400" /> "Genera un reporte de ventas por categoría."</li>
                                    </ul>
                                </div>
                            </div>

                            <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-100">
                                <h4 className="text-xl font-bold text-indigo-800 mb-3 flex items-center gap-2">
                                    <TrendingUp /> Predicciones de Ventas
                                </h4>
                                <p className="text-slate-700 mb-4">
                                    El sistema analiza el pasado para predecir el futuro.
                                </p>
                                <ul className="space-y-3 text-sm text-slate-700">
                                    <li className="flex gap-3">
                                        <div className="bg-white p-1 rounded text-indigo-600"><TrendingUp size={16} /></div>
                                        <span><strong>Planificación:</strong> Si la IA predice un aumento en ventas, prepara más stock.</span>
                                    </li>
                                    <li className="flex gap-3">
                                        <div className="bg-white p-1 rounded text-indigo-600"><TrendingUp size={16} /></div>
                                        <span><strong>Tendencias:</strong> Identifica qué productos están perdiendo popularidad antes de que sea un problema.</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Módulo 4: Ventas y Operaciones */}
                <section className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
                    <div className="bg-orange-600 p-6 text-white flex items-center gap-4">
                        <ShoppingCart size={32} />
                        <h3 className="text-2xl font-bold">4. Ventas y Operaciones</h3>
                    </div>
                    <div className="p-8 grid md:grid-cols-2 gap-8">
                        <div>
                            <h4 className="text-lg font-bold text-orange-800 mb-2">Carritos Activos</h4>
                            <p className="text-slate-600">
                                Es como tener cámaras en tu tienda. Puedes ver en tiempo real qué están poniendo los clientes en sus carritos.
                                Si ves un carrito abandonado de alto valor, ¡contacta al cliente para cerrar la venta!
                            </p>
                        </div>
                        <div>
                            <h4 className="text-lg font-bold text-orange-800 mb-2">Preventa</h4>
                            <p className="text-slate-600">
                                Gestiona pedidos especiales o reservas de productos que aún no han llegado. Asegura la venta antes de tener el stock.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Módulo 5: Seguridad */}
                <section className="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden">
                    <div className="bg-slate-700 p-6 text-white flex items-center gap-4">
                        <Shield size={32} />
                        <h3 className="text-2xl font-bold">5. Seguridad y Usuarios</h3>
                    </div>
                    <div className="p-8">
                        <p className="text-slate-600 mb-4">
                            Como administrador, tienes el control total.
                        </p>
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="flex gap-4 items-start">
                                <div className="bg-slate-100 p-2 rounded-lg"><Users className="text-slate-600" /></div>
                                <div>
                                    <h5 className="font-bold text-slate-800">Gestión de Empleados</h5>
                                    <p className="text-sm text-slate-600">Crea cuentas para tu equipo. Asigna roles limitados para que solo vean lo que necesitan.</p>
                                </div>
                            </div>
                            <div className="flex gap-4 items-start">
                                <div className="bg-slate-100 p-2 rounded-lg"><Shield className="text-slate-600" /></div>
                                <div>
                                    <h5 className="font-bold text-slate-800">Bitácora de Auditoría</h5>
                                    <p className="text-sm text-slate-600">¿Alguien borró un producto por error? Revisa la bitácora para ver quién fue y cuándo ocurrió.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

            </div>

            {/* Footer Help */}
            <div className="bg-slate-50 p-8 rounded-2xl border border-slate-200 text-center">
                <h3 className="text-xl font-bold text-slate-800 mb-2">¿Tienes más preguntas?</h3>
                <p className="text-slate-600 mb-6">Nuestro equipo de soporte está disponible 24/7 para ayudarte con cualquier duda técnica.</p>
                <button className="px-8 py-3 bg-slate-800 text-white rounded-xl font-medium hover:bg-slate-900 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all">
                    Contactar Soporte Técnico
                </button>
            </div>

        </div>
    );
}
