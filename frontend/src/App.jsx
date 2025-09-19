import { useState, useEffect } from 'react';
import { 
  Menu, X, ShoppingBag, Users, BarChart3, Zap, Shield, Globe,
  Check, Star, ArrowRight, Sparkles, Mail, Lock, Smile, Rocket
} from 'lucide-react';

// --- Componentes Reutilizables para un código más limpio ---

const FeatureCard = ({ icon: Icon , title, desc }) => (
  <div className="group relative overflow-hidden rounded-2xl bg-white p-8 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 border border-slate-100">
    {/* MEJORA: Glow sutil en el fondo de la tarjeta al hacer hover */}
    <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
    <div className="relative">
      <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform duration-300">
        <Icon className="w-7 h-7 text-white" />
      </div>
      <h4 className="text-xl font-bold text-slate-800 mb-3">{title}</h4>
      <p className="text-slate-600">{desc}</p>
    </div>
  </div>
);

const TestimonialCard = ({ name, role, text }) => (
  <div className="p-8 bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col h-full">
    <div className="flex items-center mb-4">
      {[...Array(5)].map((_, star) => (<Star key={star} className="w-5 h-5 text-yellow-400 fill-current" />))}
    </div>
    <p className="text-slate-700 mb-6 flex-grow">"{text}"</p>
    <div className="flex items-center">
      {/* MEJORA: Avatar para un toque más humano */}
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-200 to-purple-200 flex items-center justify-center mr-4">
        <span className="text-xl font-bold text-blue-800">{name[0]}</span>
      </div>
      <div>
        <h5 className="font-bold text-slate-800">{name}</h5>
        <span className="text-slate-500 text-sm">{role}</span>
      </div>
    </div>
  </div>
);

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // --- Datos (sin cambios) ---
  const features = [
    { icon: ShoppingBag, title: "E-commerce Integrado", desc: "Gestiona tu tienda online sin complicaciones" },
    { icon: Users, title: "CRM Inteligente", desc: "Conoce a tus clientes y aumenta las ventas" },
    { icon: BarChart3, title: "Analytics Avanzado", desc: "Decisiones basadas en datos reales" },
    { icon: Zap, title: "Automatización", desc: "Ahorra tiempo con procesos automatizados" },
    { icon: Shield, title: "Seguridad Total", desc: "Tus datos protegidos 24/7" },
    { icon: Globe, title: "Multi-idioma", desc: "Vende en cualquier parte del mundo" }
  ];

  const plans = [
    {
      name: "Básico", price: "9", description: "Perfecto para empezar tu negocio",
      features: ["Hasta 100 clientes","1 usuario","Dashboard básico","Soporte por email","10GB almacenamiento"],
      buttonClass: "bg-slate-500 hover:bg-slate-600"
    },
    {
      name: "Plus", price: "29", description: "Ideal para negocios en crecimiento", popular: true,
      features: ["Clientes ilimitados","5 usuarios","Analytics avanzado","Soporte prioritario 24/7","100GB almacenamiento","Integraciones básicas","Automatizaciones"],
      buttonClass: "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
    },
    {
      name: "Pro", price: "59", description: "Máximo control para tu empresa",
      features: ["Todo en Plus","Usuarios ilimitados","API completa","Dashboard personalizado","1TB almacenamiento","IA predictiva","Account Manager"],
      buttonClass: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
    }
  ];

  const testimonials = [
    { name: "María García", role: "CEO de TechStore", text: "EvoCRM transformó completamente nuestra gestión de clientes. La interfaz es intuitiva y el soporte es de primera." },
    { name: "Carlos López", role: "Founder de EcoShop", text: "La mejor inversión para hacer crecer mi negocio online. Las automatizaciones nos han ahorrado horas de trabajo." },
    { name: "Ana Martínez", role: "Directora de Ventas", text: "Incrementamos nuestras ventas un 40% en 3 meses gracias a los insights del CRM. ¡Impresionante!" }
  ];
  
  const stats = [
    { icon: Users, value: "10K+", label: "Clientes Activos" },
    { icon: Smile, value: "98%", label: "Satisfacción" },
    { icon: Rocket, value: "40%", label: "Crecimiento Promedio" },
    { icon: Zap, value: "50+", label: "Integraciones" },
  ];

  return (
    // MEJORA: Paleta de colores más moderna con 'slate'
    <>
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased">

      {/* Header */}
      <header className={`fixed w-full z-50 transition-all duration-300 ${
        scrolled 
        // MEJORA: Header con borde sutil al hacer scroll
        ? 'bg-white/80 backdrop-blur-lg shadow-md py-4 border-b border-slate-200/80' 
        : 'bg-transparent py-6'
      }`}>
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              EvoCRM
            </h1>
          </div>

          <nav className="hidden md:flex items-center gap-8">
            {["features","plans","testimonials"].map((id) => (
              <a key={id} href={`#${id}`} className="font-medium text-slate-600 hover:text-blue-600 transition-colors duration-200 capitalize">
                {id === 'features' ? 'Características' : id === 'plans' ? 'Planes' : 'Testimonios'}
              </a>
            ))}
            <a href="#login" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-500/40 transition-all duration-300 transform hover:scale-105">
              Ingresar
            </a>
          </nav>

          <button className="md:hidden text-slate-700" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {isMenuOpen && (
          <nav className="md:hidden mt-4 mx-4 bg-white rounded-2xl shadow-xl p-4">
            <ul className="space-y-3">
              {["features","plans","testimonials"].map((id) => (
                <li key={id}><a href={`#${id}`} className="block py-2 text-slate-700 hover:text-blue-600 capitalize">{id}</a></li>
              ))}
              <li><a href="#login" className="block bg-gradient-to-r from-blue-600 to-purple-600 text-white text-center py-3 rounded-full font-semibold">Ingresar</a></li>
            </ul>
          </nav>
        )}
      </header>

      <main className="pt-24">

        {/* Hero */}
        <section className="relative overflow-hidden py-20 lg:py-32">
          {/* MEJORA: Patrón de puntos sutil para dar textura */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-100 to-slate-50" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4d4d8' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")" }}></div>
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-300/50 rounded-full blur-3xl opacity-60 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-300/50 rounded-full blur-3xl opacity-60 animate-pulse delay-75"></div>
          
          <div className="container mx-auto px-6 relative z-10 text-center max-w-4xl">
            <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm border border-slate-200/80 px-4 py-2 rounded-full mb-6 shadow-sm">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-semibold text-slate-700">Nueva versión 2.0 ya disponible</span>
            </div>
            <h2 className="text-5xl lg:text-7xl font-extrabold mb-6 leading-tight tracking-tighter">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Gestiona tu negocio</span>
              <br />
              <span className="text-slate-800">como nunca antes</span>
            </h2>
            <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
              La plataforma todo-en-uno que combina E-commerce y CRM para impulsar tu negocio al siguiente nivel.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="#plans" className="group bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:shadow-2xl hover:shadow-purple-500/40 transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2">
                Comenzar ahora
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </a>
              <a href="#" className="bg-white text-slate-700 px-8 py-4 rounded-full text-lg font-semibold border-2 border-slate-200 hover:border-purple-300 hover:shadow-lg transition-all duration-300 transform hover:scale-105">
                Ver demo
              </a>
            </div>
            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-slate-600">
              {["Sin tarjeta de crédito","14 días gratis","Cancela cuando quieras"].map((text,i)=>(
                <div key={i} className="flex items-center gap-2"><Check className="w-5 h-5 text-green-500" /><span>{text}</span></div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-20 bg-white">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Características Poderosas
              </h3>
              <p className="text-xl text-slate-600">Todo lo que necesitas para que tu negocio despegue.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => <FeatureCard key={index} {...feature} />)}
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-16 bg-gradient-to-r from-blue-700 to-purple-700">
          <div className="container mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            {stats.map(({ icon: Icon, value, label }, i) => (
              // MEJORA: Iconos para hacer la sección más visual
              <div key={i} className="flex flex-col items-center">
                <Icon className="w-10 h-10 mb-3 text-blue-200" />
                <div className="text-4xl font-bold">{value}</div>
                <div className="text-blue-100 font-medium">{label}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Plans */}
        <section id="plans" className="py-20 bg-slate-50">
          <div className="container mx-auto px-6 text-center mb-16 max-w-2xl mx-auto">
            <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Planes que se adaptan a ti
            </h3>
            <p className="text-xl text-slate-600">Elige el plan perfecto para tu negocio, sin complicaciones.</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto items-center">
            {plans.map((plan, index) => (
              <div key={index} className={`relative rounded-3xl p-8 transition-all duration-300 ${
                  plan.popular 
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-2xl shadow-purple-500/40 scale-105' 
                  : 'bg-white border border-slate-200 hover:border-blue-400'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-orange-400 text-white px-4 py-1.5 rounded-full text-sm font-bold shadow-lg">
                    ⭐ MÁS POPULAR
                  </div>
                )}
                <div className="text-center mb-8">
                  <h4 className={`text-2xl font-bold mb-3 ${plan.popular ? 'text-white' : 'text-slate-800'}`}>{plan.name}</h4>
                  <p className={`${plan.popular ? 'text-blue-100' : 'text-slate-600'}`}>{plan.description}</p>
                  <div className="mt-6">
                    <span className={`text-5xl font-bold ${plan.popular ? 'text-white' : 'text-slate-900'}`}>${plan.price}</span>
                    <span className={`${plan.popular ? 'text-blue-100' : 'text-slate-500'}`}>/mes</span>
                  </div>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <Check className={`w-5 h-5 mt-1 flex-shrink-0 ${plan.popular ? 'text-blue-200' : 'text-green-500'}`} />
                      <span className={`${plan.popular ? 'text-white' : 'text-slate-700'}`}>{f}</span>
                    </li>
                  ))}
                </ul>
                <a href="#login" className={`block w-full text-center px-6 py-3 rounded-full font-semibold transition-all duration-300 transform hover:scale-105 ${plan.buttonClass} text-white`}>
                  Elegir Plan
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" className="py-20 bg-white">
          <div className="container mx-auto px-6 text-center mb-16 max-w-2xl mx-auto">
            <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Lo que dicen nuestros clientes
            </h3>
            <p className="text-xl text-slate-600">Historias reales de negocios que crecieron con EvoCRM.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {testimonials.map((t, i) => <TestimonialCard key={i} {...t} />)}
          </div>
        </section>
        
        {/* Login Section */}
        <section id="login" className="py-20 bg-slate-50">
          <div className="container mx-auto px-6 max-w-md">
            <div className="bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
              <h3 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Accede a tu cuenta
              </h3>
              <form className="space-y-6">
                <div>
                  <label className="block text-slate-700 font-medium mb-2">Email</label>
                  {/* MEJORA: Transiciones y estilos de foco en inputs */}
                  <div className="relative group">
                    <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input type="email" placeholder="correo@ejemplo.com" className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-slate-700 font-medium mb-2">Contraseña</label>
                  <div className="relative group">
                    <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input type="password" placeholder="********" className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                  </div>
                </div>
                <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-500/40 transform hover:scale-105 transition-all duration-300">
                  Ingresar
                </button>
              </form>
              <p className="text-center text-slate-500 text-sm mt-6">
                ¿No tienes cuenta? <a href="#plans" className="font-semibold text-blue-600 hover:underline">Regístrate ahora</a>
              </p>
            </div>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-12">
        <div className="container mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h5 className="text-white font-bold text-lg mb-4">EvoCRM</h5>
            <p className="text-slate-400">La solución todo-en-uno para gestionar tu negocio y clientes con eficiencia.</p>
          </div>
          {['Empresa', 'Soporte'].map(title => (
            <div key={title}>
              <h5 className="text-white font-bold mb-4">{title}</h5>
              <ul className="space-y-2">
                {(title === 'Empresa' ? ['Acerca de', 'Blog', 'Carreras'] : ['Centro de ayuda', 'Contacto', 'Términos y privacidad']).map(link => (
                  <li key={link}><a href="#" className="text-slate-400 hover:text-blue-400 transition-colors">{link}</a></li>
                ))}
              </ul>
            </div>
          ))}
          <div>
            <h5 className="text-white font-bold mb-4">Newsletter</h5>
            <form className="flex flex-col gap-3">
              <input type="email" placeholder="tu@email.com" className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-white outline-none focus:ring-2 focus:ring-blue-500" />
              <button className="bg-blue-600 hover:bg-purple-600 text-white px-4 py-2 rounded-xl transition-colors font-semibold">Suscribirse</button>
            </form>
          </div>
        </div>
        <div className="text-center text-slate-500 mt-10 border-t border-slate-800 pt-8">
          &copy; {new Date().getFullYear()} EvoCRM. Todos los derechos reservados.
        </div>
      </footer>
    </div>
    </>
  );
}

export default App;
