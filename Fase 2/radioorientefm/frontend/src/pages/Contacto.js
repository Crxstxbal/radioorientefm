import React, { useState, useEffect } from 'react';
import { Mail, Phone, MapPin, Send, User, MessageSquare, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import './Pages.css';
import './Contacto.css';

const Contacto = () => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    tipo_asunto: '',
    mensaje: ''
  });
  const [loading, setLoading] = useState(false);
  const [tiposAsunto, setTiposAsunto] = useState([]);
  const [estacionInfo, setEstacionInfo] = useState(null);
  const [focusedField, setFocusedField] = useState(null);
  const [errors, setErrors] = useState({});

  //cargar tipos de asunto y informacion de la estación
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        //usar obtener en lugar de axios para evitar problemas con headers globales
        const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const tiposResponse = await fetch(`${base}/api/contact/api/tipos-asunto/`);
        if (!tiposResponse.ok) {
          throw new Error('Error al cargar tipos de asunto');
        }
        const tiposData = await tiposResponse.json();
        //los endpoints drf devuelven objetos paginados con { results: [] }
        const tiposArray = tiposData.results || (Array.isArray(tiposData) ? tiposData : []);
        setTiposAsunto(tiposArray);

        //cargar informacion de la estación
        const estacionResponse = await fetch(`${base}/api/radio/api/estaciones/`);
        if (estacionResponse.ok) {
          const estacionData = await estacionResponse.json();
          //los endpoints drf devuelven objetos paginados con { results: [] }
          const estacionArray = estacionData.results || (Array.isArray(estacionData) ? estacionData : []);
          if (estacionArray.length > 0) {
            setEstacionInfo(estacionArray[0]);
          }
        }
      } catch (error) {
        console.error('Error al cargar datos:', error);
        //fallback con tipos de asunto por defecto
        setTiposAsunto([
          { id: 1, nombre: 'Consulta General' },
          { id: 2, nombre: 'Publicidad' },
          { id: 3, nombre: 'Programación' },
          { id: 4, nombre: 'Técnico' }
        ]);
      }
    };

    cargarDatos();
  }, []);

  const validatePhone = (phone) => {
    //permitir solo números, espacios, guiones y paréntesis
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) || phone === '';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    //validacion especial para teléfono
    if (name === 'telefono') {
      //permitir solo números y algunos caracteres especiales
      if (value && !validatePhone(value)) {
        setErrors({
          ...errors,
          telefono: 'Solo se permiten números y caracteres + - ( )'
        });
        return; // No actualizar si no es válido
      } else {
        //limpiar error si es válido
        const newErrors = { ...errors };
        delete newErrors.telefono;
        setErrors(newErrors);
      }
    }

    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      //usar obtener para enviar sin autenticacion (formulario público)
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${base}/api/contact/api/contactos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast.success('Mensaje enviado exitosamente. Te contactaremos pronto.');
        setFormData({
          nombre: '',
          email: '',
          telefono: '',
          tipo_asunto: '',
          mensaje: ''
        });
      } else {
        toast.error('Error al enviar el mensaje. Inténtalo de nuevo.');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error al enviar el mensaje. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contact-page">
      <div className="container">
        <div className="page-header">
          <Mail className="page-icon" />
          <div>
            <h1 className="page-title">Contacto</h1>
            <p className="page-subtitle">
              Estamos aquí para escucharte. Envíanos tu mensaje y te responderemos pronto.
            </p>
          </div>
        </div>

        <div className="contact-content">
          <div className="contact-info">
            <h2 className="section-title">Información de Contacto</h2>
            
            <div className="contact-item">
              <Phone className="contact-icon" />
              <div>
                <h3>Teléfono</h3>
                <p>{estacionInfo?.telefono || '+56 2 2345 6789'}</p>
              </div>
            </div>

            <div className="contact-item">
              <Mail className="contact-icon" />
              <div>
                <h3>Correo</h3>
                <p>{estacionInfo?.email || 'contacto@radiooriente.com'}</p>
              </div>
            </div>

            <div className="contact-item">
              <MapPin className="contact-icon" />
              <div>
                <h3>Dirección</h3>
                <p>{estacionInfo?.direccion || 'Av. Ictinos 858, Peñalolen, Santiago, Chile'}</p>
              </div>
            </div>

            <div className="business-hours">
              <h3>Horarios de Atención</h3>
              <div className="hours-grid">
                <div className="hours-item">
                  <span className="day">Lunes - Viernes</span>
                  <span className="time">8:00 AM - 6:00 PM</span>
                </div>
                <div className="hours-item">
                  <span className="day">Sábados</span>
                  <span className="time">9:00 AM - 2:00 PM</span>
                </div>
                <div className="hours-item">
                  <span className="day">Domingos</span>
                  <span className="time">Cerrado para atención</span>
                </div>
              </div>
            </div>
          </div>

          <motion.div
            className="contact-form-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h2 className="section-title">Envíanos un Mensaje</h2>
            <p className="form-description">Completa el formulario y nos pondremos en contacto contigo pronto</p>

            <form onSubmit={handleSubmit} className="contact-form-modern">
              <div className="form-row">
                <motion.div
                  className={`form-field ${focusedField === 'nombre' ? 'focused' : ''} ${formData.nombre ? 'filled' : ''}`}
                  whileTap={{ scale: 0.98 }}
                >
                  <label htmlFor="nombre" className="floating-label">
                    <User size={18} />
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    id="nombre"
                    name="nombre"
                    value={formData.nombre}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('nombre')}
                    onBlur={() => setFocusedField(null)}
                    className="modern-input"
                    required
                  />
                  <div className="input-border"></div>
                </motion.div>

                <motion.div
                  className={`form-field ${focusedField === 'email' ? 'focused' : ''} ${formData.email ? 'filled' : ''}`}
                  whileTap={{ scale: 0.98 }}
                >
                  <label htmlFor="email" className="floating-label">
                    <Mail size={18} />
                    Correo Electrónico *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    className="modern-input"
                    required
                  />
                  <div className="input-border"></div>
                </motion.div>
              </div>

              <div className="form-row">
                <motion.div
                  className={`form-field ${focusedField === 'telefono' ? 'focused' : ''} ${formData.telefono ? 'filled' : ''} ${errors.telefono ? 'error' : ''}`}
                  whileTap={{ scale: 0.98 }}
                >
                  <label htmlFor="telefono" className="floating-label">
                    <Phone size={18} />
                    Teléfono *
                  </label>
                  <input
                    type="tel"
                    id="telefono"
                    name="telefono"
                    value={formData.telefono}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('telefono')}
                    onBlur={() => setFocusedField(null)}
                    className="modern-input"
                    placeholder="+56 9 1234 5678"
                    required
                  />
                  <div className="input-border"></div>
                  {errors.telefono && (
                    <motion.div
                      className="error-message"
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <AlertCircle size={14} />
                      {errors.telefono}
                    </motion.div>
                  )}
                </motion.div>

                <motion.div
                  className={`form-field ${focusedField === 'tipo_asunto' ? 'focused' : ''} ${formData.tipo_asunto ? 'filled' : ''}`}
                  whileTap={{ scale: 0.98 }}
                >
                  <label htmlFor="tipo_asunto" className="floating-label">
                    <MessageSquare size={18} />
                    Tipo de Asunto *
                  </label>
                  <select
                    id="tipo_asunto"
                    name="tipo_asunto"
                    value={formData.tipo_asunto}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('tipo_asunto')}
                    onBlur={() => setFocusedField(null)}
                    className="modern-select"
                    required
                  >
                    <option value="">Selecciona un tipo</option>
                    {tiposAsunto.map((tipo) => (
                      <option key={tipo.id} value={tipo.id}>
                        {tipo.nombre}
                      </option>
                    ))}
                  </select>
                  <div className="input-border"></div>
                </motion.div>
              </div>

              <motion.div
                className={`form-field full-width ${focusedField === 'mensaje' ? 'focused' : ''} ${formData.mensaje ? 'filled' : ''}`}
                whileTap={{ scale: 0.98 }}
              >
                <label htmlFor="mensaje" className="floating-label">
                  <MessageSquare size={18} />
                  Mensaje *
                </label>
                <textarea
                  id="mensaje"
                  name="mensaje"
                  value={formData.mensaje}
                  onChange={handleChange}
                  onFocus={() => setFocusedField('mensaje')}
                  onBlur={() => setFocusedField(null)}
                  className="modern-textarea"
                  rows="6"
                  required
                ></textarea>
                <div className="input-border"></div>
              </motion.div>

              <motion.button
                type="submit"
                className="btn btn-primary submit-btn-modern"
                disabled={loading || Object.keys(errors).length > 0}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Send size={20} />
                {loading ? 'Enviando...' : 'Enviar Mensaje'}
              </motion.button>
            </form>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Contacto;
