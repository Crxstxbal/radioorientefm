import axios from 'axios';

// Configuración base de axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores (instancia api)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Manejar errores de servidor
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

// Funciones de API específicas
export const contactAPI = {
  // Tipos de asunto
  getTiposAsunto: () => api.get('/api/contact/tipos-asunto/'),
  
  // Contactos
  createContacto: (data) => api.post('/api/contact/contactos/', data),
  
  // Suscripciones
  createSuscripcion: (data) => api.post('/api/contact/suscripciones/', data),
};

export const radioAPI = {
  // Estaciones
  getEstaciones: () => api.get('/api/radio/api/estaciones/'),
  
  // Géneros
  getGeneros: () => api.get('/api/radio/api/generos/'),
  
  // Programas
  getProgramas: () => api.get('/api/radio/api/programas/'),
  
  // Horarios
  getHorarios: () => api.get('/api/radio/api/horarios/'),
  
  // Conductores
  getConductores: () => api.get('/api/radio/api/conductores/'),
  
  // Endpoints de compatibilidad
  getStation: () => api.get('/api/radio/station/'),
  getPrograms: () => api.get('/api/radio/programs/'),
};

export const blogAPI = {
  // Artículos
  getArticulos: (params) => api.get('/api/blog/articulos/', { params }),
  getArticulo: (id) => api.get(`/api/blog/articulos/${id}/`),
  
  // Categorías
  getCategorias: () => api.get('/api/blog/categorias/'),
};

export const emergenteAPI = {
  // Bandas emergentes
  createBanda: (data) => api.post('/api/emergente/bandas/', data),
  getBandas: (params) => api.get('/api/emergente/bandas/', { params }),
};

export const ubicacionAPI = {
  // Países
  getPaises: () => api.get('/api/ubicacion/paises/'),
  
  // Ciudades
  getCiudades: (params) => api.get('/api/ubicacion/ciudades/', { params }),
  
  // Comunas
  getComunas: (params) => api.get('/api/ubicacion/comunas/', { params }),
};

export const authAPI = {
  // Autenticación
  login: (data) => api.post('/api/auth/login/', data),
  register: (data) => api.post('/api/auth/register/', data),
  logout: () => api.post('/api/auth/logout/'),
  
  // Perfil
  getProfile: () => api.get('/api/auth/profile/'),
  updateProfile: (data) => api.put('/api/auth/profile/update/', data),
};

// Exportar instancia de axios configurada
export default api;
