// src/modulos/productos/Dashboard.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Menu, X, ShoppingBag, Users, BarChart3, Zap, Shield,
  Globe, ArrowRight, Smile, Rocket, Check,
} from "lucide-react";

import logocrm from "../assets/logoCRM.png";

/* ---------- Pequeños subcomponentes semánticos ---------- */
const FeatureCard = ({ icon: Icon, title, desc }) => (
  <article className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
    <div className="bg-[#2e7e8b]/10 w-12 h-12 rounded-full flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-[#2e7e8b]" aria-hidden />
    </div>
    <h4 className="text-lg sm:text-xl font-semibold mb-2 text-slate-900">{title}</h4>
    <p className="text-sm sm:text-base text-slate-600">{desc}</p>
  </article>
);

const TestimonialCard = ({ name, role, text }) => (
  <article className="bg-slate-50 p-6 rounded-2xl border border-slate-200">
    <p className="text-slate-700 italic mb-4">"{text}"</p>
    <footer>
      <p className="font-semibold text-slate-900">{name}</p>
      <p className="text-sm text-[#2e7e8b] font-medium">{role}</p>
    </footer>
  </article>
);

export default function Dashboard() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const features = [
    { icon: ShoppingBag, title: "E-commerce Integrado", desc: "Gestiona tu tienda online sin complicaciones" },
    { icon: Users, title: "CRM Inteligente", desc: "Conoce a tus clientes y aumenta las ventas" },
    { icon: BarChart3, title: "Analytics Avanzado", desc: "Decisiones basadas en datos reales" },
    { icon: Zap, title: "Automatización", desc: "Ahorra tiempo con procesos automatizados" },
    { icon: Shield, title: "Seguridad Total", desc: "Tus datos protegidos 24/7" },
    { icon: Globe, title: "Multi-idioma", desc: "Vende en cualquier parte del mundo" },
  ];

  const plans = [
    {
      name: "Básico",
      price: "9",
      description: "Perfecto para empezar",
      features: ["Hasta 100 clientes", "1 usuario", "Dashboard básico", "Soporte por email", "10GB almacenamiento"],
      accent: "bg-slate-500",
    },
    {
      name: "Plus",
      price: "29",
      description: "Ideal para crecer",
      popular: true,
      features: ["Clientes ilimitados", "5 usuarios", "Analytics avanzado", "Soporte 24/7", "100GB almacenamiento"],
      accent: "bg-[#f0a831]",
    },
    {
      name: "Pro",
      price: "59",
      description: "Para equipos grandes",
      features: ["Todo en Plus", "Usuarios ilimitados", "API completa", "Dashboard personalizado", "1TB almacenamiento"],
      accent: "bg-slate-800",
    },
  ];

  const testimonials = [
    { name: "María García", role: "CEO - TechStore", text: "ChambaSoft transformó nuestra gestión. Interfaz intuitiva y soporte excelente." },
    { name: "Carlos López", role: "Founder - EcoShop", text: "Automatizaciones que nos ahorraron horas. Muy recomendable." },
    { name: "Ana Martínez", role: "Directora de Ventas", text: "Incrementamos ventas 40% en 3 meses gracias a los insights." },
  ];

  const stats = [
    { icon: Users, value: "10K+", label: "Clientes Activos" },
    { icon: Smile, value: "98%", label: "Satisfacción" },
    { icon: Rocket, value: "40%", label: "Crecimiento Promedio" },
    { icon: Zap, value: "50+", label: "Integraciones" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased">
      {/* Skip link para accesibilidad */}
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-white px-3 py-2 rounded shadow">
        Ir al contenido
      </a>

      {/* Header / Nav */}
      <header
        className={`fixed inset-x-0 z-50 transition-all duration-300 ${
          scrolled ? "bg-white/90 backdrop-blur-md shadow-md border-b border-slate-200/80 py-3" : "bg-transparent py-4"
        }`}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-3">
              <img src={logocrm} alt="Logo ChamaSoft" className="w-12 h-12 object-contain rounded-md shadow-sm" />
              <span className="hidden sm:inline-block font-bold text-lg text-slate-800">ChambaSoft</span>
            </Link>
          </div>

          <nav aria-label="Main navigation" className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm font-medium text-slate-600 hover:text-[#2e7e8b]">Características</a>
            <a href="#plans" className="text-sm font-medium text-slate-600 hover:text-[#2e7e8b]">Planes</a>
            <a href="#testimonials" className="text-sm font-medium text-slate-600 hover:text-[#2e7e8b]">Testimonios</a>
            <Link to="/login" className="ml-4 inline-flex items-center gap-2 bg-[#f0a831] text-white px-4 py-2 rounded-full font-semibold hover:shadow-lg">
              Iniciar sesión <ArrowRight className="w-4 h-4" />
            </Link>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              aria-label={menuOpen ? "Cerrar menú" : "Abrir menú"}
              onClick={() => setMenuOpen((s) => !s)}
              className="p-2 rounded-md bg-white/70 backdrop-blur-sm shadow-sm"
            >
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu panel */}
        {menuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200">
            <div className="container mx-auto px-4 py-4 flex flex-col gap-3">
              <a href="#features" onClick={() => setMenuOpen(false)} className="py-2 font-medium text-slate-700">Características</a>
              <a href="#plans" onClick={() => setMenuOpen(false)} className="py-2 font-medium text-slate-700">Planes</a>
              <a href="#testimonials" onClick={() => setMenuOpen(false)} className="py-2 font-medium text-slate-700">Testimonios</a>
              <Link to="/login" onClick={() => setMenuOpen(false)} className="mt-2 inline-block bg-[#f0a831] text-white px-4 py-2 rounded-full text-center font-semibold">
                Iniciar sesión
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* MAIN */}
      <main id="main" className="pt-28">
        {/* Hero */}
        <section className="relative overflow-hidden py-14 lg:py-24">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center max-w-4xl">
            <h1 className="text-3xl sm:text-4xl lg:text-6xl font-extrabold mb-4 leading-tight">
              <span className="bg-gradient-to-r from-[#2e7e8b] to-[#4ea5b3] bg-clip-text text-transparent">
                Gestiona tu negocio
              </span>
              <br />
              <span className="text-slate-800">como nunca antes</span>
            </h1>
            <p className="text-sm sm:text-lg text-slate-600 mb-6">
              Plataforma todo-en-uno que combina e-commerce y CRM para impulsar ventas y automatizar procesos.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <a href="#plans" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-[#2e7e8b] text-white font-semibold hover:shadow-lg">
                Comenzar ahora <ArrowRight className="w-4 h-4" />
              </a>
              <a href="#testimonials" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-white border border-slate-200 text-slate-700 font-semibold">
                Ver demo
              </a>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-12 lg:py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <header className="text-center max-w-2xl mx-auto mb-10">
              <h2 className="text-2xl sm:text-3xl font-bold mb-2">Características Poderosas</h2>
              <p className="text-sm sm:text-base text-slate-600">Todo lo que necesitas para que tu negocio despegue.</p>
            </header>

            {/* Grid responsive: 1 col mobile, 2 sm, 3 lg */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((f, i) => (
                <FeatureCard key={i} {...f} />
              ))}
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-8 lg:py-12 bg-[#2e7e8b]">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <ul className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-white">
              {stats.map(({ icon: Icon, value, label }, i) => (
                <li key={i} className="flex flex-col items-center">
                  <Icon className="w-8 h-8 mb-2 text-[#f0a831]" aria-hidden />
                  <strong className="text-xl sm:text-2xl font-bold">{value}</strong>
                  <span className="text-sm sm:text-base text-white/90">{label}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* Plans */}
        <section id="plans" className="py-12 lg:py-20 bg-slate-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold mb-2">Planes que se adaptan a ti</h2>
            <p className="text-sm sm:text-base text-slate-600">Elige el plan perfecto para tu negocio, sin complicaciones.</p>
          </div>

          {/* Responsive: cards on mobile, 3-cols on lg */}
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {plans.map((plan, idx) => (
                <article
                  key={idx}
                  className={`relative rounded-2xl p-6 transition-shadow duration-300 border ${
                    plan.popular ? "bg-[#2e7e8b] text-white border-transparent shadow-2xl scale-102" : "bg-white border-slate-200"
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-[#f0a831] text-slate-900 px-3 py-1 rounded-full text-xs font-semibold shadow">
                      MÁS POPULAR
                    </div>
                  )}

                  <header className="mb-4 text-center">
                    <h3 className={`text-lg font-bold ${plan.popular ? "text-white" : "text-slate-900"}`}>{plan.name}</h3>
                    <p className={`text-sm ${plan.popular ? "text-white/80" : "text-slate-600"}`}>{plan.description}</p>
                    <div className="mt-4 text-3xl font-extrabold">
                      <span className={`${plan.popular ? "text-white" : "text-slate-900"}`}>${plan.price}</span>
                      <span className={`ml-2 text-sm ${plan.popular ? "text-white/80" : "text-slate-500"}`}>/mes</span>
                    </div>
                  </header>

                  <ul className="mb-5 space-y-3">
                    {plan.features.map((f, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <Check className={`w-5 h-5 mt-1 flex-shrink-0 ${plan.popular ? "text-[#f0a831]" : "text-[#2e7e8b]"}`} />
                        <span className={plan.popular ? "text-white" : "text-slate-700"}>{f}</span>
                      </li>
                    ))}
                  </ul>

                  <div>
                    <a
                      href="#login"
                      className={`block w-full text-center px-4 py-2 rounded-full font-semibold ${plan.popular ? "bg-white text-[#2e7e8b]" : "bg-[#2e7e8b] text-white"} hover:opacity-95`}
                    >
                      Elegir Plan
                    </a>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-12 lg:py-20 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold mb-2">Lo que dicen nuestros clientes</h2>
            <p className="text-sm sm:text-base text-slate-600">Historias reales de negocios que crecieron con EvoCRM.</p>
          </div>

          <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-6xl">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {testimonials.map((t, i) => (
                <TestimonialCard key={i} {...t} />
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h4 className="text-white font-bold text-lg mb-2">EvoCRM</h4>
            <p className="text-slate-400 text-sm">Solución todo-en-uno para gestionar tu negocio y clientes con eficiencia.</p>
          </div>

          <nav aria-label="Enlaces empresa" className="text-sm">
            <h5 className="text-white font-semibold mb-2">Empresa</h5>
            <ul className="space-y-2 text-slate-400">
              <li><a href="#" className="hover:text-[#f0a831]">Acerca de</a></li>
              <li><a href="#" className="hover:text-[#f0a831]">Blog</a></li>
              <li><a href="#" className="hover:text-[#f0a831]">Carreras</a></li>
            </ul>
          </nav>

          <nav aria-label="Soporte" className="text-sm">
            <h5 className="text-white font-semibold mb-2">Soporte</h5>
            <ul className="space-y-2 text-slate-400">
              <li><a href="#" className="hover:text-[#f0a831]">Centro de ayuda</a></li>
              <li><a href="#" className="hover:text-[#f0a831]">Contacto</a></li>
              <li><a href="#" className="hover:text-[#f0a831]">Términos y privacidad</a></li>
            </ul>
          </nav>

          <div>
            <h5 className="text-white font-semibold mb-2">Newsletter</h5>
            <form className="flex flex-col gap-3" onSubmit={(e) => e.preventDefault()}>
              <label htmlFor="email" className="sr-only">Tu correo</label>
              <input
                id="email"
                type="email"
                placeholder="tu@email.com"
                className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-white outline-none focus:ring-2 focus:ring-[#f0a831]"
              />
              <button className="bg-[#f0a831] hover:bg-[#d9942b] text-white px-4 py-2 rounded-xl font-semibold">Suscribirse</button>
            </form>
          </div>
        </div>

        <div className="text-center text-slate-500 mt-8 border-t border-slate-800 pt-6 text-sm">
          &copy; {new Date().getFullYear()} EvoCRM. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  );
}
