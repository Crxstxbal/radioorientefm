import React, { useState } from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './Pages.css';

const Contacto = () => {
  const [formData, setFormData] = useState({
    nombre: '',
    correo: '',
    telefono: '',
    asunto: 'general',
    mensaje: ''
  });
  const [loading, setLoading] = useState(false);

  const opcionesAsunto = [
    { value: 'general', label: 'Consulta General' },
    { value: 'programacion', label: 'Programación' },
    { value: 'publicidad', label: 'Publicidad' },
    { value: 'soporte', label: 'Soporte Técnico' },
    { value: 'otro', label: 'Otro' }
  ];

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
      await axios.post('/api/contact/message/', formData);
      toast.success('Mensaje enviado exitosamente. Te contactaremos pronto.');
      setFormData({
        nombre: '',
        correo: '',
        telefono: '',
        asunto: 'general',
        mensaje: ''
      });
    } catch (error) {
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
                <h3>Teléfonos</h3>
                <p>+58 414-123-4567</p>
                <p>+58 212-987-6543</p>
              </div>
            </div>

            <div className="contact-item">
              <Mail className="contact-icon" />
              <div>
                <h3>Correos</h3>
                <p>info@radioorientefm.com</p>
                <p>programacion@radioorientefm.com</p>
              </div>
            </div>

            <div className="contact-item">
              <MapPin className="contact-icon" />
              <div>
                <h3>Dirección</h3>
                <p>Av. Principal, Centro Comercial Oriente</p>
                <p>Piso 3, Local 301</p>
                <p>Barcelona, Estado Anzoátegui</p>
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
                  <span className="time">Cerrado</span>
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
                  <label htmlFor="correo" className="form-label">
                    Correo Electrónico *
                  </label>
                  <input
                    type="email"
                    id="correo"
                    name="correo"
                    value={formData.correo}
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
                  <label htmlFor="asunto" className="form-label">
                    Asunto *
                  </label>
                  <select
                    id="asunto"
                    name="asunto"
                    value={formData.asunto}
                    onChange={handleChange}
                    className="form-select"
                    required
                  >
                    {opcionesAsunto.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
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
