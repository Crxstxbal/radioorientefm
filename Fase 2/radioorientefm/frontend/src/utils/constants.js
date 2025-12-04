//endpoints de la api
export const API_ENDPOINTS = {
  //configuracion base
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  //autenticacion
  AUTH: {
    LOGIN: '/api/auth/login/',
    REGISTER: '/api/auth/register/',
    LOGOUT: '/api/auth/logout/',
    PROFILE: '/api/auth/profile/',
    UPDATE_PROFILE: '/api/auth/profile/update/',
  },
  
  //contacto
  CONTACT: {
    TIPOS_ASUNTO: '/api/contact/tipos-asunto/',
    CONTACTOS: '/api/contact/contactos/',
    SUSCRIPCIONES: '/api/contact/suscripciones/',
  },
  
  //radio
  RADIO: {
    ESTACIONES: '/api/radio/api/estaciones/',
    GENEROS: '/api/radio/api/generos/',
    PROGRAMAS: '/api/radio/api/programas/',
    HORARIOS: '/api/radio/api/horarios/',
    CONDUCTORES: '/api/radio/api/conductores/',
    //endpoints de compatibilidad
    STATION: '/api/radio/station/',
    PROGRAMS: '/api/radio/programs/',
  },
  
  //blog/artículos
  BLOG: {
    ARTICULOS: '/api/blog/articulos/',
    CATEGORIAS: '/api/blog/categorias/',
  },
  
  //bandas emergentes
  EMERGENTE: {
    BANDAS: '/api/emergente/bandas/',
  },
  
  //ubicación
  UBICACION: {
    PAISES: '/api/ubicacion/paises/',
    CIUDADES: '/api/ubicacion/ciudades/',
    COMUNAS: '/api/ubicacion/comunas/',
  },
};

//constantes de validacion de formularios
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^[\+]?[1-9][\d]{0,15}$/,
  URL_REGEX: /^https?:\/\/.+/,
  
  MIN_PASSWORD_LENGTH: 8,
  MAX_MESSAGE_LENGTH: 1000,
  MAX_NAME_LENGTH: 100,
};

//constantes de interfaz de usuario
export const UI = {
  TOAST_DURATION: 4000,
  LOADING_DELAY: 300,
  DEBOUNCE_DELAY: 500,
  
  BREAKPOINTS: {
    MOBILE: 768,
    TABLET: 1024,
    DESKTOP: 1200,
  },
};

//mapeo de días de la semana
export const DAYS_OF_WEEK = {
  0: 'Domingo',
  1: 'Lunes',
  2: 'Martes',
  3: 'Miércoles',
  4: 'Jueves',
  5: 'Viernes',
  6: 'Sábado',
};

//tipos de enlaces para bandas
export const LINK_TYPES = [
  { value: 'spotify', label: 'Spotify' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'soundcloud', label: 'SoundCloud' },
  { value: 'website', label: 'Sitio Web' },
  { value: 'otro', label: 'Otro' },
];

//datos predeterminados de respaldo
export const FALLBACK_DATA = {
  GENEROS: [
    { id: 1, nombre: 'Rock' },
    { id: 2, nombre: 'Pop' },
    { id: 3, nombre: 'Reggaeton' },
    { id: 4, nombre: 'Cumbia' },
    { id: 5, nombre: 'Baladas' },
    { id: 6, nombre: 'Electrónica' },
  ],
  
  TIPOS_ASUNTO: [
    { id: 1, nombre: 'Consulta General' },
    { id: 2, nombre: 'Publicidad' },
    { id: 3, nombre: 'Programación' },
    { id: 4, nombre: 'Técnico' },
    { id: 5, nombre: 'Reclamo' },
    { id: 6, nombre: 'Felicitaciones' },
  ],
  
  CATEGORIAS: [
    { id: 1, nombre: 'Noticias' },
    { id: 2, nombre: 'Entrevistas' },
    { id: 3, nombre: 'Música' },
    { id: 4, nombre: 'Eventos' },
    { id: 5, nombre: 'Cultura' },
    { id: 6, nombre: 'Tecnología' },
  ],
  
  STATION_INFO: {
    nombre: 'Radio Oriente FM',
    telefono: '+56 2 2345 6789',
    email: 'contacto@radiooriente.com',
    direccion: 'Av. Providencia 1234, Santiago, Chile',
    stream_url: 'https://sonic-us.fhost.cl/8126/stream',
  },
};

//mensajes de error
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifica tu internet e inténtalo de nuevo.',
  SERVER_ERROR: 'Error del servidor. Inténtalo más tarde.',
  VALIDATION_ERROR: 'Por favor revisa los datos ingresados.',
  AUTH_ERROR: 'Error de autenticación. Inicia sesión nuevamente.',
  NOT_FOUND: 'Recurso no encontrado.',
  PERMISSION_DENIED: 'No tienes permisos para realizar esta acción.',
};

//mensajes de éxito
export const SUCCESS_MESSAGES = {
  CONTACT_SENT: 'Mensaje enviado exitosamente. Te contactaremos pronto.',
  SUBSCRIPTION_SUCCESS: 'Suscripción exitosa. ¡Gracias por unirte!',
  BAND_SUBMITTED: '¡Propuesta enviada exitosamente! Te contactaremos pronto.',
  PROFILE_UPDATED: 'Perfil actualizado exitosamente.',
  LOGIN_SUCCESS: '¡Bienvenido de vuelta!',
  REGISTER_SUCCESS: '¡Cuenta creada exitosamente!',
  LOGOUT_SUCCESS: 'Sesión cerrada exitosamente.',
};

//claves para almacenamiento local
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  VOLUME: 'radioVolume',
  THEME: 'theme',
  LANGUAGE: 'language',
};
