import { 
  Search, Bell, HelpCircle, Settings, User,  
  Users, UserCheck, FileText, Shield, Package, ShoppingCart, 
  CreditCard, Handshake, BarChart2, Bot 
} from "lucide-react";
import { useState } from "react";

const sidebarItems = [
  { name: "Usuarios", icon: <Users size={22} /> },
  { name: "Empleados", icon: <UserCheck size={22} /> },
  { name: "Bitácora", icon: <FileText size={22} /> },
  { name: "Perfiles", icon: <Shield size={22} /> },
  { name: "Productos", icon: <Package size={22} /> },
  { name: "Carritos Activos", icon: <ShoppingCart size={22} /> },
  { name: "Pedidos", icon: <FileText size={22} /> }, // podrías usar ClipboardList
  { name: "Pagos", icon: <CreditCard size={22} /> },
  { name: "CRM", icon: <Handshake size={22} /> },
  { name: "Reportes", icon: <BarChart2 size={22} /> },
  { name: "IA", icon: <Bot size={22} /> },
];

export default function DashAdmin() {
  const [activeModule, setActiveModule] = useState("Usuarios");

  return (
    <div className="h-screen flex bg-gray-100">
      {/* Sidebar */}
      <aside 
        className="w-20 bg-[#2e7e8b] text-white flex flex-col items-center py-6 shadow-lg overflow-y-auto"
        aria-label="Menú lateral"
      >
        <nav className="flex flex-col gap-6">
          {sidebarItems.map((item) => (
            <button
              key={item.name}
              className={`flex flex-col items-center text-xs transition focus:outline-none ${
                activeModule === item.name 
                  ? "text-[#f0a831]" 
                  : "text-white hover:text-[#f0a831]"
              }`}
              onClick={() => setActiveModule(item.name)}
              aria-current={activeModule === item.name ? "page" : undefined}
            >
              <div className="p-2">{item.icon}</div>
              <span className="hidden md:block mt-1">{item.name}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="w-full border-b bg-white shadow-sm">
          {/* Primera fila */}
          <div className="flex items-center justify-between px-6 py-3">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <img
                src="/logo.png"
                alt="Logo"
                className="h-8 w-8"
              />
              <span className="font-bold text-lg text-[#2e7e8b]">MiApp</span>
            </div>

            {/* Barra de búsqueda */}
            <div className="flex-1 mx-10 max-w-lg">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Buscar..."
                  className="w-full rounded-full border px-4 py-2 pl-10 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
                />
                <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </div>

            {/* Iconos de usuario */}
            <div className="flex items-center space-x-5 text-gray-600">
              <HelpCircle className="h-5 w-5 cursor-pointer hover:text-[#2e7e8b]" />
              <Settings className="h-5 w-5 cursor-pointer hover:text-[#2e7e8b]" />
              <Bell className="h-5 w-5 cursor-pointer hover:text-[#2e7e8b]" />
              <User className="h-6 w-6 cursor-pointer hover:text-[#2e7e8b]" />
            </div>
          </div>

          {/* Menú horizontal */}
          <nav 
            className="flex items-center space-x-6 px-6 py-2 border-t bg-[#2e7e8b] text-sm font-medium text-white"
            aria-label="Menú superior"
          >
            {[
              "Candidatos", "Contactos", "Cuentas", "Oportunidades", 
              "Productos", "Listas de precios", "Calendario", "Archivo"
            ].map((menu, index) => (
              <a
                key={index}
                href="#"
                className={`pb-1 transition ${
                  index === 0 
                    ? "border-b-2 border-[#f0a831] text-[#f0a831]" 
                    : "hover:text-[#f0a831]"
                }`}
              >
                {menu}
              </a>
            ))}
          </nav>
        </header>

        {/* Área de trabajo */}
        <main className="p-6" role="main">
          <h1 className="text-xl font-semibold text-[#2e7e8b]">
            {activeModule}
          </h1>
          <p className="mt-2 text-gray-600">
            Aquí se mostrará el contenido del módulo <span className="font-semibold">{activeModule}</span>.
          </p>
        </main>
      </div>
    </div>
  );
}
