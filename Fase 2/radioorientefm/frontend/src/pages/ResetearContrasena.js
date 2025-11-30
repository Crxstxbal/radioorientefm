import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Lock, Eye, EyeOff, CheckCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './Auth.css';

const ResetearContrasena = () => {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    new_password: '',
    new_password_confirm: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.new_password !== formData.new_password_confirm) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (formData.new_password.length < 8) {
      toast.error('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/auth/password-reset-confirm/', {
        uid: uid,
        token: token,
        new_password: formData.new_password,
        new_password_confirm: formData.new_password_confirm
      });

      toast.success(response.data.message || 'Contraseña actualizada exitosamente');
      setSuccess(true);

      // Redirigir al login después de 3 segundos
      setTimeout(() => {
        navigate('/iniciar-sesion');
      }, 3000);
    } catch (error) {
      const errorMessage = error.response?.data?.token?.[0] ||
                          error.response?.data?.uid?.[0] ||
                          error.response?.data?.new_password?.[0] ||
                          error.response?.data?.error ||
                          'Error al restablecer la contraseña. El enlace puede haber expirado.';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-page">
        <div className="container">
          <div className="auth-container">
            <div className="auth-card">
              <div className="auth-header">
                <CheckCircle className="auth-icon" style={{ color: '#10b981' }} />
                <h1 className="auth-title">Contraseña Restablecida</h1>
                <p className="auth-subtitle">
                  Tu contraseña ha sido actualizada exitosamente.
                  Serás redirigido al inicio de sesión en unos segundos...
                </p>
              </div>

              <div className="auth-footer">
                <Link to="/iniciar-sesion" className="btn btn-primary" style={{ width: '100%' }}>
                  Ir al Inicio de Sesión
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
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-header">
              <Lock className="auth-icon" />
              <h1 className="auth-title">Restablecer Contraseña</h1>
              <p className="auth-subtitle">
                Ingresa tu nueva contraseña
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="new_password" className="form-label">
                  Nueva Contraseña
                </label>
                <div className="password-input">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="new_password"
                    name="new_password"
                    value={formData.new_password}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Mínimo 8 caracteres"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="new_password_confirm" className="form-label">
                  Confirmar Nueva Contraseña
                </label>
                <div className="password-input">
                  <input
                    type={showPasswordConfirm ? 'text' : 'password'}
                    id="new_password_confirm"
                    name="new_password_confirm"
                    value={formData.new_password_confirm}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Repite tu contraseña"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                  >
                    {showPasswordConfirm ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary auth-submit"
                disabled={loading}
              >
                {loading ? 'Restableciendo...' : 'Restablecer Contraseña'}
              </button>
            </form>

            <div className="auth-footer">
              <p>
                ¿Recordaste tu contraseña?{' '}
                <Link to="/iniciar-sesion" className="auth-link">
                  Volver al inicio de sesión
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetearContrasena;
