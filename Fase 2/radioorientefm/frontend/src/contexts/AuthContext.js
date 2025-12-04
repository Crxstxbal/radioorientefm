import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  //no configurar axios.defaults globalmente
  //esto causaba problemas en páginas públicas como /contacto y /emergente
  //useefecto(() => {
  //if (token) {
  //axios.defaults.headers.common['authorization'] = `token ${token}`
  //} else {
  //delete axios.defaults.headers.common['authorization']
  //}
  //}, [token])

  //check if user is logged in on montar
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await api.get('/api/auth/profile/', {
            headers: { Authorization: `Token ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login/', {
        email,
        password
      });
      
      const { user, token } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      toast.success('¡Bienvenido de vuelta!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.non_field_errors?.[0] || 'Error al iniciar sesión';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register/', userData);
      const { user, token } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      toast.success('¡Cuenta creada exitosamente!');
      return { success: true };
    } catch (error) {
      const errors = error.response?.data;
      let message = 'Error al registrar usuario';
      if (errors) {
        message = Object.values(errors).flat().join(', ');
      }
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post('/api/auth/logout/', {}, {
          headers: { Authorization: `Token ${token}` }
        });
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      toast.success('Sesión cerrada');
    }
  };

  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/api/auth/profile/update/', userData, {
        headers: token ? { Authorization: `Token ${token}` } : {}
      });
      setUser(response.data);
      toast.success('Perfil actualizado');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al actualizar perfil';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user,
    isAdmin: user?.is_staff || false  // Campo para verificar si es administrador
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
