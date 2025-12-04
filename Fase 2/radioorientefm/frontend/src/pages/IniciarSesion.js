import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogIn, Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { motion } from 'framer-motion';
import GoogleAuth from '../components/GoogleAuth'; // <--- 1. IMPORTAMOS EL COMPONENTE
import './Auth.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setShowSuccess(false);

    try {
      const result = await login(formData.email, formData.password);

      if (result.success) {
        //pequeño delay para que se vea el estado de cargando
        setTimeout(() => {
          setShowSuccess(true);

          //esperar a que termine la animación antes de navegar
          setTimeout(() => {
            navigate('/');
          }, 1800);
        }, 500);
      } else {
        setLoading(false);
        setShowSuccess(false);
      }
    } catch (error) {
      setLoading(false);
      setShowSuccess(false);
    }
  };

  return (
    <div className="auth-page">
      {/*animated background particles*/}
      <div className="auth-particles">
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="auth-particle"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              scale: Math.random() * 0.5 + 0.5
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              rotate: 360
            }}
            transition={{
              duration: Math.random() * 20 + 10,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          />
        ))}
      </div>

      <div className="container">
        <div className="auth-container">
          {/*left side - branding*/}
          <motion.div
            className="auth-branding"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              className="auth-logo-wrapper"
              animate={{
                scale: [1, 1.08, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <img
                src="/images/radiooriente.png"
                alt="Radio Oriente FM"
                className="auth-logo-image"
              />
            </motion.div>
            <h2 className="auth-branding-title">Radio Oriente FM</h2>
            <p className="auth-branding-text">
              La voz de la zona oriente. Conectando comunidades a través de las ondas radiales.
            </p>
            <div className="auth-branding-features">
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                ✓ Acceso a contenido exclusivo
              </motion.div>
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                ✓ Notificaciones personalizadas
              </motion.div>
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                ✓ Interacción con locutores
              </motion.div>
            </div>
          </motion.div>

          {/*right side - login form*/}
          <motion.div
            className="auth-card"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="auth-header">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.4 }}
              >
                <LogIn className="auth-icon" />
              </motion.div>
              <h1 className="auth-title">Bienvenido de Nuevo</h1>
              <p className="auth-subtitle">
                Inicia sesión para continuar
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <motion.div
                className="form-group-modern"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
              >
                <label htmlFor="email" className="form-label-modern">
                  <Mail size={18} />
                  Correo Electrónico
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="form-input-auth"
                  placeholder="tu@email.com"
                  required
                />
              </motion.div>

              <motion.div
                className="form-group-modern"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <label htmlFor="password" className="form-label-modern">
                  <Lock size={18} />
                  Contraseña
                </label>
                <div className="password-input-modern">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="form-input-auth"
                    placeholder="••••••••"
                    required
                  />
                  <motion.button
                    type="button"
                    className="password-toggle-modern"
                    onClick={() => setShowPassword(!showPassword)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </motion.button>
                </div>
              </motion.div>

              <motion.div
                className="forgot-password-link"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                <Link to="/recuperar-contrasena" className="auth-link">
                  ¿Olvidaste tu contraseña?
                </Link>
              </motion.div>

              <motion.button
                type="submit"
                className={`auth-submit-modern ${showSuccess ? 'success' : ''}`}
                disabled={loading || showSuccess}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <span className="button-text">
                  <LogIn size={20} />
                  {showSuccess ? 'Iniciando sesión' : (loading ? 'Iniciando Sesión...' : 'Iniciar Sesión')}
                </span>
                <span className="check-box">
                  <svg className="check-svg" viewBox="0 0 24 24">
                    <path d="M6 12l4 4L18 8" />
                  </svg>
                </span>
              </motion.button>
            </form>

            {/* --- SECCIÓN NUEVA: LOGIN CON GOOGLE --- */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.85 }}
              style={{ margin: '1.5rem 0' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem', opacity: 0.6 }}>
                <div style={{ flex: 1, height: '1px', backgroundColor: '#ccc' }}></div>
                <span style={{ padding: '0 10px', fontSize: '0.85rem', color: '#666' }}>O inicia con</span>
                <div style={{ flex: 1, height: '1px', backgroundColor: '#ccc' }}></div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <GoogleAuth />
              </div>
            </motion.div>
            {/* -------------------------------------- */}

            <motion.div
              className="auth-footer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
            >
              <p>
                ¿No tienes una cuenta?{' '}
                <Link to="/registro" className="auth-link">
                  Regístrate aquí
                </Link>
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Login;