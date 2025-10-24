import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../modulos/usuarios/clientes/components/Sidebar';
import Header from '../modulos/usuarios/clientes/components/Header';
import logocrm from '../assets/logoCRM.png';

export default function Layout() {
    return (
        <div className="flex h-screen bg-gray-100 font-sans text-gray-800">
            <aside
                className="w-20 md:w-56 bg-[#2e7e8b] text-white flex flex-col items-center md:items-stretch py-6 shadow-lg transition-all duration-300"
                aria-label="Menú lateral principal"
            >
                {/* Logo */}
                <div className="flex items-center justify-center md:justify-start gap-3 px-4 mb-6">
                    <a href="/" className="flex items-center gap-3">
                        <img src={logocrm} alt="Logo" className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain" />
                        <span className="hidden md:inline-block font-bold text-xl">MiApp</span>
                    </a>
                </div>

                {/* Sidebar */}
                <Sidebar />
            </aside>

            <div className="flex-1 flex flex-col">
                {/* Header */}
                <Header />

                {/* Main content */}
                <main id="main-content" className="p-6 lg:p-8 flex-1 overflow-y-auto bg-gray-100" tabIndex={-1}>
                    <Outlet />
                </main>
            </div>
        </div>
    );
}