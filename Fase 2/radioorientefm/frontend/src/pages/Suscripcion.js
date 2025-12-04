import React, { useState, useEffect, useRef } from 'react';
import { Mail, Bell, CheckCircle, Gift, Users, Calendar, Star } from 'lucide-react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import './Pages.css';
import './Suscripcion.css';

//componentee de contador animado
const AnimatedCounter = ({ end, duration = 2000, suffix = '', prefix = '' }) => {
  const [count, setCount] = useState(0);
  const countRef = useRef(null);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !hasAnimated) {
          setHasAnimated(true);
          let startTime = null;
          const startValue = 0;

          const animate = (currentTime) => {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);

            //ease out animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentCount = Math.floor(easeOutQuart * (end - startValue) + startValue);

            setCount(currentCount);

            if (progress < 1) {
              requestAnimationFrame(animate);
            } else {
              setCount(end);
            }
          };

          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.5 }
    );

    if (countRef.current) {
      observer.observe(countRef.current);
    }

    return () => {
      if (countRef.current) {
        observer.unobserve(countRef.current);
      }
    };
  }, [end, duration, hasAnimated]);

  return (
    <span ref={countRef}>
      {prefix}{count.toLocaleString()}{suffix}
    </span>
  );
};

const Subscription = () => {
  const [formData, setFormData] = useState({
    email: '',
    nombre: ''
  });
  const [loading, setLoading] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      //obtener token de autenticacion si existe
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Token ${token}` } : {};

      const response = await api.post('/api/contact/api/suscripciones/', formData, { headers });

      //manejar respuesta de éxito
      if (response.data.reactivada) {
        toast.success('¡Bienvenido de vuelta! Tu suscripción ha sido reactivada exitosamente.', {
          duration: 5000,
          icon: '🎉'
        });
      } else {
        toast.success(response.data.message || 'Suscripción exitosa. ¡Gracias por unirte!', {
          duration: 5000,
          icon: '✅'
        });
      }

      setIsSubscribed(true);
      setFormData({ email: '', nombre: '' });
    } catch (error) {
      //manejar diferentes tipos de errores
      if (error.response) {
        const { status, data } = error.response;

        if (status === 400) {
          //email ya suscrito
          const errorMsg = data.message || 'Ya estás suscrito a nuestro newsletter. ¡Gracias por tu interés!';
          toast.error(errorMsg, {
            duration: 5000,
            icon: '📧'
          });
        } else if (status === 500) {
          //error del servidor
          toast.error(data.message || 'Error en el servidor. Por favor, intenta más tarde.', {
            duration: 5000,
            icon: '⚠️'
          });
        } else {
          //otros errores
          toast.error(data.message || 'Error al procesar la suscripción', {
            duration: 5000
          });
        }
      } else if (error.request) {
        //error de red
        toast.error('No se pudo conectar al servidor. Verifica tu conexión a internet.', {
          duration: 5000,
          icon: '🌐'
        });
      } else {
        //otros errores
        toast.error('Ocurrió un error inesperado. Por favor, intenta nuevamente.', {
          duration: 5000
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const benefits = [
    {
      icon: <Bell className="benefit-icon" />,
      title: 'Noticias Exclusivas',
      description: 'Recibe las noticias más importantes antes que nadie'
    },
    {
      icon: <Mail className="benefit-icon" />,
      title: 'Boletín Semanal',
      description: 'Resumen semanal de los eventos más destacados'
    },
    {
      icon: <Gift className="benefit-icon" />,
      title: 'Contenido Especial',
      description: 'Acceso a contenido exclusivo y promociones especiales'
    },
    {
      icon: <CheckCircle className="benefit-icon" />,
      title: 'Sin Spam',
      description: 'Solo contenido relevante, puedes cancelar cuando quieras'
    }
  ];

  return (
    <div className="subscription-page">
      <div className="container">
        <motion.div
          className="page-header-subscription"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Mail className="page-icon-subscription" />
          <h1 className="page-title-subscription">Únete a Nuestra Comunidad</h1>
          <p className="page-subtitle-subscription">
            Mantente conectado con Radio Oriente FM y recibe contenido exclusivo
          </p>
        </motion.div>

        {/*sección de métricas - ahora arriba*/}
        <motion.div
          className="stats-section-hero"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="stats-grid-modern">
            <motion.div
              className="stat-card-modern"
              whileHover={{ scale: 1.05, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-icon">
                <Users size={40} />
              </div>
              <div className="stat-number-modern">
                <AnimatedCounter end={500} suffix="+" duration={2500} />
              </div>
              <div className="stat-label-modern">Suscriptores Activos</div>
            </motion.div>

            <motion.div
              className="stat-card-modern"
              whileHover={{ scale: 1.05, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-icon">
                <Calendar size={40} />
              </div>
              <div className="stat-number-modern">
                <AnimatedCounter end={52} duration={2000} />
              </div>
              <div className="stat-label-modern">Boletines al Año</div>
            </motion.div>

            <motion.div
              className="stat-card-modern"
              whileHover={{ scale: 1.05, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-icon">
                <Star size={40} />
              </div>
              <div className="stat-number-modern">
                <AnimatedCounter end={100} suffix="%" duration={2000} />
              </div>
              <div className="stat-label-modern">Contenido Gratis</div>
            </motion.div>
          </div>
        </motion.div>

        <div className="subscription-content">
          <motion.div
            className="subscription-info"
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <h2 className="section-title-modern">¿Por qué suscribirse?</h2>
            <div className="benefits-grid-modern">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={index}
                  className="benefit-card-modern"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                  whileHover={{ y: -8, boxShadow: "0 12px 30px rgba(220, 38, 38, 0.2)" }}
                >
                  <div className="benefit-icon-wrapper">
                    {benefit.icon}
                  </div>
                  <h3 className="benefit-title-modern">{benefit.title}</h3>
                  <p className="benefit-description-modern">{benefit.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="subscription-form-container-modern"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {isSubscribed ? (
              <motion.div
                className="success-message-modern"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <div className="success-icon-wrapper">
                  <CheckCircle className="success-icon-modern" size={60} />
                </div>
                <h3 className="success-title">¡Suscripción Exitosa!</h3>
                <p className="success-text">
                  Gracias por suscribirte a Radio Oriente FM.
                  Pronto recibirás nuestro primer boletín.
                </p>
                <motion.button
                  className="btn btn-outline-modern"
                  onClick={() => setIsSubscribed(false)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Suscribir otro email
                </motion.button>
              </motion.div>
            ) : (
              <>
                <h2 className="form-title-modern">Suscríbete Ahora</h2>
                <p className="form-description-modern">
                  Recibe las últimas noticias y actualizaciones directamente en tu email
                </p>

                <form onSubmit={handleSubmit} className="subscription-form-modern">
                  <div className="form-group-modern">
                    <label htmlFor="nombre" className="form-label-modern">
                      Nombre (Opcional)
                    </label>
                    <input
                      type="text"
                      id="nombre"
                      name="nombre"
                      value={formData.nombre}
                      onChange={handleChange}
                      className="form-input-modern"
                      placeholder="Tu nombre completo"
                    />
                  </div>

                  <div className="form-group-modern">
                    <label htmlFor="email" className="form-label-modern">
                      Correo Electrónico *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="form-input-modern"
                      placeholder="tu@email.com"
                      required
                    />
                  </div>

                  <motion.button
                    type="submit"
                    className="btn btn-primary subscribe-btn-modern"
                    disabled={loading}
                    whileHover={{ scale: 1.02, boxShadow: "0 8px 30px rgba(220, 38, 38, 0.4)" }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Mail size={20} />
                    {loading ? 'Suscribiendo...' : 'Suscribirse Gratis'}
                  </motion.button>

                  <p className="privacy-note-modern">
                    Al suscribirte, aceptas recibir emails de Radio Oriente FM.
                    Puedes cancelar tu suscripción en cualquier momento.
                  </p>
                </form>
              </>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
