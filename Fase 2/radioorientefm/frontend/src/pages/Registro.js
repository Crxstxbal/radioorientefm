import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserPlus, Eye, EyeOff, Mail, Lock, User, Radio } from 'lucide-react';
import { motion } from 'framer-motion';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState([]);
  const { register } = useAuth();
  const navigate = useNavigate();

  //validacion de contraseña
  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push('Mínimo 8 caracteres');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Al menos una mayúscula');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('Al menos un número');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Al menos un carácter especial');
    }
    return errors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    //validar contraseña en tiempo real
    if (name === 'password') {
      setPasswordErrors(validatePassword(value));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    //validar contraseña antes de enviar
    const errors = validatePassword(formData.password);
    if (errors.length > 0) {
      setPasswordErrors(errors);
      return;
    }

    setLoading(true);
    setShowSuccess(false);

    try {
      const result = await register(formData);

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
              Únete a nuestra comunidad y forma parte de la familia Radio Oriente.
            </p>
            <div className="auth-branding-features">
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                ✓ Perfil personalizado
              </motion.div>
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                ✓ Contenido exclusivo
              </motion.div>
              <motion.div
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                ✓ Comunidad activa
              </motion.div>
            </div>
          </motion.div>

          {/*right side - register form*/}
          <motion.div
            className="auth-card auth-card-register"
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
                <UserPlus className="auth-icon" />
              </motion.div>
              <h1 className="auth-title">Crear Cuenta</h1>
              <p className="auth-subtitle">
                Completa el formulario para registrarte
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-row-modern">
                <motion.div
                  className="form-group-modern"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <label htmlFor="first_name" className="form-label-modern">
                    <User size={18} />
                    Nombre
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="form-input-auth"
                    placeholder="Juan"
                    required
                  />
                </motion.div>

                <motion.div
                  className="form-group-modern"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <label htmlFor="last_name" className="form-label-modern">
                    <User size={18} />
                    Apellido
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="form-input-auth"
                    placeholder="Pérez"
                    required
                  />
                </motion.div>
              </div>

              <motion.div
                className="form-group-modern"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <label htmlFor="username" className="form-label-modern">
                  <User size={18} />
                  Nombre de Usuario
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="form-input-auth"
                  placeholder="juanperez"
                  required
                />
              </motion.div>

              <motion.div
                className="form-group-modern"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 }}
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
                transition={{ delay: 0.8 }}
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
                {passwordErrors.length > 0 && (
                  <div className="password-requirements">
                    {passwordErrors.map((error, index) => (
                      <div key={index} className="password-error">
                        ✗ {error}
                      </div>
                    ))}
                  </div>
                )}
                {formData.password && passwordErrors.length === 0 && (
                  <div className="password-success">
                    ✓ Contraseña válida
                  </div>
                )}
              </motion.div>

              <motion.div
                className="form-group-modern"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9 }}
              >
                <label htmlFor="password_confirm" className="form-label-modern">
                  <Lock size={18} />
                  Confirmar Contraseña
                </label>
                <div className="password-input-modern">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="password_confirm"
                    name="password_confirm"
                    value={formData.password_confirm}
                    onChange={handleChange}
                    className="form-input-auth"
                    placeholder="••••••••"
                    required
                  />
                  <motion.button
                    type="button"
                    className="password-toggle-modern"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </motion.button>
                </div>
              </motion.div>

              <motion.button
                type="submit"
                className={`auth-submit-modern ${showSuccess ? 'success' : ''}`}
                disabled={loading || showSuccess}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 }}
              >
                <span className="button-text">
                  <UserPlus size={20} />
                  {showSuccess ? 'Gracias por tu registro' : (loading ? 'Creando Cuenta...' : 'Crear Cuenta')}
                </span>
                <span className="check-box">
                  <svg className="check-svg" viewBox="0 0 24 24">
                    <path d="M6 12l4 4L18 8" />
                  </svg>
                </span>
              </motion.button>
            </form>

            <motion.div
              className="auth-footer"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1 }}
            >
              <p>
                ¿Ya tienes una cuenta?{' '}
                <Link to="/login" className="auth-link">
                  Inicia sesión aquí
                </Link>
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Register;
