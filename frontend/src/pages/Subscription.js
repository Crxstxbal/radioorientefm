import React, { useState } from 'react';
import { Mail, Bell, CheckCircle, Gift } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './Pages.css';

const Subscription = () => {
  const [formData, setFormData] = useState({
    email: '',
    name: ''
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
      const response = await axios.post('/api/contact/subscribe/', formData);
      toast.success(response.data.message);
      setIsSubscribed(true);
      setFormData({ email: '', name: '' });
    } catch (error) {
      const message = error.response?.data?.message || 'Error al suscribirse';
      toast.error(message);
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
        <div className="page-header">
          <Mail className="page-icon" />
          <div>
            <h1 className="page-title">Suscripción</h1>
            <p className="page-subtitle">
              Mantente conectado con Radio Oriente FM
            </p>
          </div>
        </div>

        <div className="subscription-content">
          <div className="subscription-info">
            <h2 className="section-title">¿Por qué suscribirse?</h2>
            <div className="benefits-grid">
              {benefits.map((benefit, index) => (
                <div key={index} className="benefit-card">
                  {benefit.icon}
                  <h3 className="benefit-title">{benefit.title}</h3>
                  <p className="benefit-description">{benefit.description}</p>
                </div>
              ))}
            </div>

            <div className="stats-section">
              <h3 className="stats-title">Únete a nuestra comunidad</h3>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">5,000+</div>
                  <div className="stat-label">Suscriptores</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">Weekly</div>
                  <div className="stat-label">Boletines</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">100%</div>
                  <div className="stat-label">Gratis</div>
                </div>
              </div>
            </div>
          </div>

          <div className="subscription-form-container">
            {isSubscribed ? (
              <div className="success-message">
                <CheckCircle className="success-icon" />
                <h3>¡Suscripción Exitosa!</h3>
                <p>
                  Gracias por suscribirte a Radio Oriente FM. 
                  Pronto recibirás nuestro primer boletín.
                </p>
                <button 
                  className="btn btn-outline"
                  onClick={() => setIsSubscribed(false)}
                >
                  Suscribir otro email
                </button>
              </div>
            ) : (
              <>
                <h2 className="form-title">Suscríbete Ahora</h2>
                <p className="form-description">
                  Recibe las últimas noticias y actualizaciones directamente en tu email
                </p>

                <form onSubmit={handleSubmit} className="subscription-form">
                  <div className="form-group">
                    <label htmlFor="name" className="form-label">
                      Nombre (Opcional)
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Tu nombre completo"
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
                      placeholder="tu@email.com"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary subscribe-btn"
                    disabled={loading}
                  >
                    <Mail size={20} />
                    {loading ? 'Suscribiendo...' : 'Suscribirse Gratis'}
                  </button>

                  <p className="privacy-note">
                    Al suscribirte, aceptas recibir emails de Radio Oriente FM. 
                    Puedes cancelar tu suscripción en cualquier momento.
                  </p>
                </form>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
