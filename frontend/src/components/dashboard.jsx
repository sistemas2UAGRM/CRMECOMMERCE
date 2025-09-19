import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom"; // Asumiendo que usas react-router-dom
import {
  ShoppingBag,
  Users,
  BarChart3,
  Zap,
  Shield,
  Globe,
  ArrowRight,
  Smile,
  Rocket,
  Check,
} from "lucide-react";

// Componentes auxiliares que podrías tener en otros archivos
const FeatureCard = ({ icon: Icon, title, desc }) => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
    <div className="bg-[#2e7e8b]/10 w-12 h-12 rounded-full flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-[#2e7e8b]" />
    </div>
    <h4 className="text-xl font-bold mb-2 text-slate-900">{title}</h4>
    <p className="text-slate-600">{desc}</p>
  </div>
);

const TestimonialCard = ({ name, role, text }) => (
  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200">
    <p className="text-slate-700 italic mb-4">"{text}"</p>
    <div>
      <p className="font-bold text-slate-900">{name}</p>
      <p className="text-sm text-[#2e7e8b] font-medium">{role}</p>
    </div>
  </div>
);


function Dashboard() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // --- Datos ---
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
      description: "Perfecto para empezar tu negocio",
      features: ["Hasta 100 clientes", "1 usuario", "Dashboard básico", "Soporte por email", "10GB almacenamiento"],
      buttonClass: "bg-slate-500 hover:bg-slate-600",
    },
    {
      name: "Plus",
      price: "29",
      description: "Ideal para negocios en crecimiento",
      popular: true,
      features: [
        "Clientes ilimitados",
        "5 usuarios",
        "Analytics avanzado",
        "Soporte prioritario 24/7",
        "100GB almacenamiento",
        "Integraciones básicas",
        "Automatizaciones",
      ],
      buttonClass: "bg-[#f0a831] hover:bg-[#d9942b]",
    },
    {
      name: "Pro",
      price: "59",
      description: "Máximo control para tu empresa",
      features: [
        "Todo en Plus",
        "Usuarios ilimitados",
        "API completa",
        "Dashboard personalizado",
        "1TB almacenamiento",
        "IA predictiva",
        "Account Manager",
      ],
      buttonClass: "bg-slate-800 hover:bg-slate-900",
    },
  ];

  const testimonials = [
    { name: "María García", role: "CEO de TechStore", text: "ChambaSoft transformó completamente nuestra gestión de clientes. La interfaz es intuitiva y el soporte es de primera." },
    { name: "Carlos López", role: "Founder de EcoShop", text: "La mejor inversión para hacer crecer mi negocio online. Las automatizaciones nos han ahorrado horas de trabajo." },
    { name: "Ana Martínez", role: "Directora de Ventas", text: "Incrementamos nuestras ventas un 40% en 3 meses gracias a los insights del CRM. ¡Impresionante!" },
  ];

  const stats = [
    { icon: Users, value: "10K+", label: "Clientes Activos" },
    { icon: Smile, value: "98%", label: "Satisfacción" },
    { icon: Rocket, value: "40%", label: "Crecimiento Promedio" },
    { icon: Zap, value: "50+", label: "Integraciones" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased">
      {/* Header */}
      <header
        className={`fixed w-full z-50 transition-all duration-300 ${
          scrolled
            ? "bg-white/80 backdrop-blur-lg shadow-md py-4 border-b border-slate-200/80"
            : "bg-transparent py-6"
        }`}
      >
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer">
            <img src="/logoCRM.png" alt="Logo ChambaSOFT" className="w-20 h-20 object-contain rounded-lg shadow-md" />
          </div>

          <nav className="hidden md:flex items-center gap-8">
            {["features", "plans", "testimonials"].map((id) => (
              <a
                key={id}
                href={`#${id}`}
                className="font-medium text-slate-600 hover:text-[#2e7e8b] transition-colors duration-200 capitalize"
              >
                {id === "features" ? "Características" : id === "plans" ? "Planes" : "Testimonios"}
              </a>
            ))}
            <Link
              to="/login"
              className="bg-[#f0a831] text-white px-6 py-2.5 rounded-full font-semibold hover:shadow-lg hover:shadow-[#f0a831]/40 transition-all duration-300 transform hover:scale-105"
            >
              Iniciar sesión
            </Link>
          </nav>
        </div>
      </header>

      {/* MAIN */}
      <main className="pt-24">
        {/* Hero */}
        <section className="relative overflow-hidden py-20 lg:py-32">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-[#2e7e8b]/20 rounded-full blur-3xl opacity-60 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-[#f0a831]/20 rounded-full blur-3xl opacity-60 animate-pulse delay-75"></div>

          <div className="container mx-auto px-6 relative z-10 text-center max-w-4xl">
            <h2 className="text-5xl lg:text-7xl font-extrabold mb-6 leading-tight tracking-tighter">
              <span className="bg-gradient-to-r from-[#2e7e8b] to-[#4ea5b3] bg-clip-text text-transparent">
                Gestiona tu negocio
              </span>
              <br />
              <span className="text-slate-800">como nunca antes</span>
            </h2>
            <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
              La plataforma todo-en-uno que combina E-commerce y CRM para impulsar tu negocio al siguiente nivel.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="#plans"
                className="group bg-[#2e7e8b] text-white px-8 py-4 rounded-full text-lg font-semibold hover:shadow-2xl hover:shadow-[#2e7e8b]/40 transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
              >
                Comenzar ahora
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </a>
              <a
                href="#"
                className="bg-white text-slate-700 px-8 py-4 rounded-full text-lg font-semibold border-2 border-slate-200 hover:border-[#f0a831] hover:shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Ver demo
              </a>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-20 bg-white">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-[#2e7e8b] to-[#4ea5b3] bg-clip-text text-transparent">
                Características Poderosas
              </h3>
              <p className="text-xl text-slate-600">Todo lo que necesitas para que tu negocio despegue.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <FeatureCard key={index} {...feature} />
              ))}
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-16 bg-[#2e7e8b]">
          <div className="container mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            {stats.map(({ icon: Icon, value, label }, i) => (
              <div key={i} className="flex flex-col items-center">
                <Icon className="w-10 h-10 mb-3 text-[#f0a831]" />
                <div className="text-4xl font-bold">{value}</div>
                <div className="text-white/80 font-medium">{label}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Plans */}
        <section id="plans" className="py-20 bg-slate-50">
          <div className="container mx-auto px-6 text-center mb-16 max-w-2xl mx-auto">
            <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-[#2e7e8b] to-[#4ea5b3] bg-clip-text text-transparent">
              Planes que se adaptan a ti
            </h3>
            <p className="text-xl text-slate-600">Elige el plan perfecto para tu negocio, sin complicaciones.</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto items-center">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-3xl p-8 transition-all duration-300 ${
                  plan.popular
                    ? "bg-[#2e7e8b] text-white shadow-2xl shadow-[#2e7e8b]/40 scale-105"
                    : "bg-white border border-slate-200 hover:border-[#2e7e8b]"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-[#f0a831] text-white px-4 py-1.5 rounded-full text-sm font-bold shadow-lg">
                    ⭐ MÁS POPULAR
                  </div>
                )}
                <div className="text-center mb-8">
                  <h4
                    className={`text-2xl font-bold mb-3 ${plan.popular ? "text-white" : "text-slate-800"}`}
                  >
                    {plan.name}
                  </h4>
                  <p className={`${plan.popular ? "text-white/80" : "text-slate-600"}`}>{plan.description}</p>
                  <div className="mt-6">
                    <span className={`text-5xl font-bold ${plan.popular ? "text-white" : "text-slate-900"}`}>
                      ${plan.price}
                    </span>
                    <span className={`${plan.popular ? "text-white/80" : "text-slate-500"}`}>/mes</span>
                  </div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check
                        className={`w-5 h-5 mt-1 flex-shrink-0 ${
                          plan.popular ? "text-[#f0a831]" : "text-[#2e7e8b]"
                        }`}
                      />
                      <span className={`${plan.popular ? "text-white" : "text-slate-700"}`}>{f}</span>
                    </li>
                  ))}
                </ul>
                <a
                  href="#login"
                  className={`block w-full text-center px-6 py-3 rounded-full font-semibold transition-all duration-300 transform hover:scale-105 ${plan.buttonClass} text-white`}
                >
                  Elegir Plan
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-20 bg-white">
          <div className="container mx-auto px-6 text-center mb-16 max-w-2xl mx-auto">
            <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-[#2e7e8b] to-[#4ea5b3] bg-clip-text text-transparent">
              Lo que dicen nuestros clientes
            </h3>
            <p className="text-xl text-slate-600">Historias reales de negocios que crecieron con EvoCRM.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {testimonials.map((t, i) => (
              <TestimonialCard key={i} {...t} />
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-12">
        <div className="container mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h5 className="text-white font-bold text-lg mb-4">EvoCRM</h5>
            <p className="text-slate-400">
              La solución todo-en-uno para gestionar tu negocio y clientes con eficiencia.
            </p>
          </div>
          {["Empresa", "Soporte"].map((title) => (
            <div key={title}>
              <h5 className="text-white font-bold mb-4">{title}</h5>
              <ul className="space-y-2">
                {(title === "Empresa"
                  ? ["Acerca de", "Blog", "Carreras"]
                  : ["Centro de ayuda", "Contacto", "Términos y privacidad"]
                ).map((link) => (
                  <li key={link}>
                    <a href="#" className="text-slate-400 hover:text-[#f0a831] transition-colors">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          <div>
            <h5 className="text-white font-bold mb-4">Newsletter</h5>
            <form className="flex flex-col gap-3">
              <input
                type="email"
                placeholder="tu@email.com"
                className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-white outline-none focus:ring-2 focus:ring-[#f0a831]"
              />
              <button className="bg-[#f0a831] hover:bg-[#d9942b] text-white px-4 py-2 rounded-xl transition-colors font-semibold">
                Suscribirse
              </button>
            </form>
          </div>
        </div>
        <div className="text-center text-slate-500 mt-10 border-t border-slate-800 pt-8">
          &copy; {new Date().getFullYear()} EvoCRM. Todos los derechos reservados.
        </div>
      </footer>
    </div>
  );
}

export default Dashboard;
