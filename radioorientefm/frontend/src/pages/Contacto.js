import React, { useState, useEffect } from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import toast from 'react-hot-toast';
import './Pages.css';

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

  // Cargar tipos de asunto y información de la estación
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        // Usar fetch en lugar de axios para evitar problemas con headers globales
        const tiposResponse = await fetch('/api/contact/api/tipos-asunto/');
        if (!tiposResponse.ok) {
          throw new Error('Error al cargar tipos de asunto');
        }
        const tiposData = await tiposResponse.json();
        // Los endpoints DRF devuelven objetos paginados con { results: [] }
        const tiposArray = tiposData.results || (Array.isArray(tiposData) ? tiposData : []);
        setTiposAsunto(tiposArray);

        // Cargar información de la estación
        const estacionResponse = await fetch('/api/radio/api/estaciones/');
        if (estacionResponse.ok) {
          const estacionData = await estacionResponse.json();
          // Los endpoints DRF devuelven objetos paginados con { results: [] }
          const estacionArray = estacionData.results || (Array.isArray(estacionData) ? estacionData : []);
          if (estacionArray.length > 0) {
            setEstacionInfo(estacionArray[0]);
          }
        }
      } catch (error) {
        console.error('Error al cargar datos:', error);
        // Fallback con tipos de asunto por defecto
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
      // Usar fetch para enviar sin autenticación (formulario público)
      const response = await fetch('/api/contact/api/contactos/', {
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

          <div className="contact-form-container">
            <h2 className="section-title">Envíanos un Mensaje</h2>
            
            <form onSubmit={handleSubmit} className="contact-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="nombre" className="form-label">
                    Nombre Completo *
                  </label>
                  <input
                    type="text"
                    id="nombre"
                    name="nombre"
                    value={formData.nombre}
                    onChange={handleChange}
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email" className="form-label">
                    Correo Electrónico *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="telefono" className="form-label">
                    Teléfono
                  </label>
                  <input
                    type="tel"
                    id="telefono"
                    name="telefono"
                    value={formData.telefono}
                    onChange={handleChange}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="tipo_asunto" className="form-label">
                    Tipo de Asunto *
                  </label>
                  <select
                    id="tipo_asunto"
                    name="tipo_asunto"
                    value={formData.tipo_asunto}
                    onChange={handleChange}
                    className="form-select"
                    required
                  >
                    <option value="">Selecciona un tipo de asunto</option>
                    {tiposAsunto.map((tipo) => (
                      <option key={tipo.id} value={tipo.id}>
                        {tipo.nombre}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="mensaje" className="form-label">
                  Mensaje *
                </label>
                <textarea
                  id="mensaje"
                  name="mensaje"
                  value={formData.mensaje}
                  onChange={handleChange}
                  className="form-textarea"
                  rows="6"
                  required
                ></textarea>
              </div>

              <button
                type="submit"
                className="btn btn-primary submit-btn"
                disabled={loading}
              >
                <Send size={20} />
                {loading ? 'Enviando...' : 'Enviar Mensaje'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contacto;
