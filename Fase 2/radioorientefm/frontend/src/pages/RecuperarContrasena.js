import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import './Auth.css';

const RecuperarContrasena = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post('/api/auth/password-reset/', {
        email: email
      });

      toast.success(response.data.message || 'Correo enviado exitosamente');
      setEmailSent(true);
    } catch (error) {
      const errorMessage = error.response?.data?.email?.[0] ||
                          error.response?.data?.error ||
                          'Error al enviar el correo. Verifica tu email.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="auth-page">
        <div className="container">
          <div className="auth-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <div className="auth-card">
              <div className="auth-header">
                <CheckCircle className="auth-icon" style={{ color: '#10b981' }} />
                <h1 className="auth-title">Correo Enviado</h1>
                <p className="auth-subtitle">
                  Hemos enviado un enlace de recuperación a tu correo electrónico.
                  Por favor, revisa tu bandeja de entrada y sigue las instrucciones.
                </p>
              </div>

              <div className="auth-footer">
                <Link to="/iniciar-sesion" className="btn btn-secondary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                  <ArrowLeft size={20} />
                  Volver al inicio de sesión
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-container" style={{ width: '500px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div className="auth-card">
            <div className="auth-header">
              <Mail className="auth-icon" />
              <h1 className="auth-title">Recuperar Contraseña</h1>
              <p className="auth-subtitle">
                Ingresa tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="email" className="form-label">
                  Correo Electrónico
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="form-input"
                  placeholder="tu-email@ejemplo.com"
                  required
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary auth-submit"
                disabled={loading}
              >
                {loading ? 'Enviando...' : 'Enviar Enlace de Recuperación'}
              </button>
            </form>

            <div className="auth-footer">
              <Link to="/iniciar-sesion" className="auth-link" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <ArrowLeft size={16} />
                Volver al inicio de sesión
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecuperarContrasena;
