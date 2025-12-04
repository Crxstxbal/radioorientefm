import axios from 'axios';

//configuracion base de axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

//interceptor para agregar token automáticamente
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

//interceptor para manejar respuestas y errores (instancia api)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    //manejar errores de servidor
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

//funciones de api específicas
export const contactAPI = {
  //tipos de asunto
  getTiposAsunto: () => api.get('/api/contact/tipos-asunto/'),
  
  //contactos
  createContacto: (data) => api.post('/api/contact/contactos/', data),
  
  //suscripciones
  createSuscripcion: (data) => api.post('/api/contact/suscripciones/', data),
};

export const radioAPI = {
  //estaciones
  getEstaciones: () => api.get('/api/radio/api/estaciones/'),
  
  //géneros
  getGeneros: () => api.get('/api/radio/api/generos/'),
  
  //programas
  getProgramas: () => api.get('/api/radio/api/programas/'),
  
  //horarios
  getHorarios: () => api.get('/api/radio/api/horarios/'),
  
  //conductores
  getConductores: () => api.get('/api/radio/api/conductores/'),
  
  //endpoints de compatibilidad
  getStation: () => api.get('/api/radio/station/'),
  getPrograms: () => api.get('/api/radio/programs/'),
};

export const blogAPI = {
  //artículos
  getArticulos: (params) => api.get('/api/blog/articulos/', { params }),
  getArticulo: (id) => api.get(`/api/blog/articulos/${id}/`),
  
  //categorías
  getCategorias: () => api.get('/api/blog/categorias/'),
};

export const emergenteAPI = {
  //bandas emergentes
  createBanda: (data) => api.post('/api/emergente/bandas/', data),
  getBandas: (params) => api.get('/api/emergente/bandas/', { params }),
};

export const ubicacionAPI = {
  //países
  getPaises: () => api.get('/api/ubicacion/paises/'),
  
  //ciudades
  getCiudades: (params) => api.get('/api/ubicacion/ciudades/', { params }),
  
  //comunas
  getComunas: (params) => api.get('/api/ubicacion/comunas/', { params }),
};

export const authAPI = {
  //autenticacion
  login: (data) => api.post('/api/auth/login/', data),
  register: (data) => api.post('/api/auth/register/', data),
  logout: () => api.post('/api/auth/logout/'),
  
  //perfil
  getProfile: () => api.get('/api/auth/profile/'),
  updateProfile: (data) => api.put('/api/auth/profile/update/', data),
};

//exportar instancia de axios configurada
export default api;
