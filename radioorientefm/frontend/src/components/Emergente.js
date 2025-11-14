import React, { useState, useEffect } from 'react';
import { Upload, Music, Users, Link, Send, X, Plus } from 'lucide-react';
import {
  FaSpotify,
  FaYoutube,
  FaInstagram,
  FaFacebook,
  FaSoundcloud,
  FaGlobe,
  FaLink
} from 'react-icons/fa';
import toast from 'react-hot-toast';
import './emergente.css';

const Emergente = () => {
    const [formData, setFormData] = useState({
        nombre_banda: '',
        integrantes: [],
        genero: '',
        pais: '',
        ciudad: '',
        comuna: '',
        email_contacto: '',
        telefono_contacto: '',
        mensaje: '',
        links: [],
        documento_presentacion: ''
    });

    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [errors, setErrors] = useState({});
    const [generos, setGeneros] = useState([]);
    const [paises, setPaises] = useState([]);
    const [ciudades, setCiudades] = useState([]);
    const [comunas, setComunas] = useState([]);
    const [isLoadingCiudades, setIsLoadingCiudades] = useState(false);
    const [isLoadingComunas, setIsLoadingComunas] = useState(false);
    const [newIntegrante, setNewIntegrante] = useState('');
    const [newLink, setNewLink] = useState({ tipo: '', url: '' });

    const token = localStorage.getItem('token');
    const isLoggedIn = Boolean(token);

    // Cargar países al iniciar
    useEffect(() => {
        const inicializarDatos = async () => {
            try {
                // Verificar si hay países
                const paisesResponse = await fetch('/api/ubicacion/paises/');
                if (!paisesResponse.ok) {
                    throw new Error('Error al cargar países');
                }
                const paisesData = await paisesResponse.json();

                // Los endpoints DRF devuelven objetos paginados con { results: [] }
                const paisesArray = paisesData.results || (Array.isArray(paisesData) ? paisesData : []);

                // Si no hay países o no está Chile, reiniciar datos desde API
                const chile = paisesArray.find(p => p.nombre === 'Chile');

                if (!chile) {
                    console.log('Chile no encontrado, cargando datos desde API...');
                    const loadingToast = toast.loading('Cargando regiones y comunas de Chile desde API oficial...');

                    try {
                        const response = await fetch('/api/ubicacion/paises/reiniciar_datos_chile/', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        if (response.ok) {
                            const data = await response.json();
                            toast.dismiss(loadingToast);
                            toast.success(`✅ ${data.message}\n📍 ${data.regiones_creadas} regiones\n🏘️ ${data.comunas_creadas} comunas`);

                            // Recargar países
                            const paisesActualizadosResponse = await fetch('/api/ubicacion/paises/');
                            if (paisesActualizadosResponse.ok) {
                                const paisesActualizados = await paisesActualizadosResponse.json();
                                const paisesActualizadosArray = paisesActualizados.results || (Array.isArray(paisesActualizados) ? paisesActualizados : []);
                                setPaises(paisesActualizadosArray);
                                // Seleccionar Chile por defecto si no hay país seleccionado
                                const chileNuevo = paisesActualizadosArray.find(p => p.nombre === 'Chile');
                                if (chileNuevo && !formData.pais) {
                                    setFormData(prev => ({ ...prev, pais: chileNuevo.id }));
                                }
                            }
                        } else {
                            throw new Error('Error al reiniciar datos');
                        }
                    } catch (apiError) {
                        toast.dismiss(loadingToast);
                        console.error('Error al cargar desde API:', apiError);
                        toast.error('No se pudieron cargar los datos desde la API');
                        setPaises([]);
                    }
                } else {
                    // Chile existe, verificar si tiene regiones
                    const ciudadesResponse = await fetch(`/api/ubicacion/ciudades/por_pais/?pais_id=${chile.id}`);
                    const ciudadesData = ciudadesResponse.ok ? await ciudadesResponse.json() : [];

                    // Si no hay regiones o hay muy pocas, recargar desde API
                    if (!ciudadesData || ciudadesData.length < 10) {
                        console.log('Pocas o ninguna región, recargando desde API...');
                        const loadingToast = toast.loading('Actualizando datos desde API oficial de Chile...');

                        try {
                            const response = await fetch('/api/ubicacion/paises/reiniciar_datos_chile/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            });
                            if (response.ok) {
                                const data = await response.json();
                                toast.dismiss(loadingToast);
                                toast.success(`Datos actualizados: ${data.regiones_creadas} regiones, ${data.comunas_creadas} comunas`);
                            }
                        } catch (apiError) {
                            toast.dismiss(loadingToast);
                            console.error('Error al actualizar desde API:', apiError);
                        }
                    }

                    setPaises(paisesArray);
                    // Seleccionar Chile por defecto si no hay país seleccionado
                    if (chile && !formData.pais) {
                        setFormData(prev => ({ ...prev, pais: chile.id }));
                    }
                }
            } catch (error) {
                console.error('Error al inicializar datos:', error);
                toast.error('Error al cargar la lista de países');
                setPaises([]);
            }
        };

        // Cargar géneros musicales
        const cargarGeneros = async () => {
            try {
                const response = await fetch('/api/radio/api/generos/');
                if (!response.ok) {
                    throw new Error('Error al cargar géneros');
                }
                const data = await response.json();
                // Los endpoints DRF devuelven objetos paginados con { results: [] }
                const generosArray = data.results || (Array.isArray(data) ? data : []);
                setGeneros(generosArray);
            } catch (error) {
                console.error('Error al cargar géneros musicales:', error);
                toast.error('Error al cargar la lista de géneros musicales');
                // Fallback con datos por defecto
                setGeneros([
                    { id: 1, nombre: 'Rock' },
                    { id: 2, nombre: 'Pop' },
                    { id: 3, nombre: 'Reggaeton' },
                    { id: 4, nombre: 'Cumbia' }
                ]);
            }
        };

        inicializarDatos();
        cargarGeneros();
    }, []);

    // Cargar ciudades cuando se selecciona un país
    useEffect(() => {
        const cargarCiudades = async () => {
            if (!formData.pais) {
                setCiudades([]);
                setComunas([]);
                setFormData(prev => ({
                    ...prev,
                    ciudad: '',
                    comuna: ''
                }));
                return;
            }

            setIsLoadingCiudades(true);
            try {
                console.log('Solicitando ciudades para país ID:', formData.pais);
                const response = await fetch(`/api/ubicacion/ciudades/por_pais/?pais_id=${formData.pais}`);

                if (!response.ok) {
                    throw new Error('Error al cargar ciudades');
                }

                const data = await response.json();
                console.log('Respuesta de ciudades:', data);

                // La respuesta ya debería ser un array
                const ciudadesData = Array.isArray(data) ? data : [];

                setCiudades(ciudadesData);

                // Resetear ciudad y comuna cuando cambia el país
                setFormData(prev => ({
                    ...prev,
                    ciudad: '',
                    comuna: ''
                }));
            } catch (error) {
                console.error('Error al cargar ciudades:', error);
                toast.error('Error al cargar las ciudades. Intenta nuevamente.');
                setCiudades([]);
                setComunas([]);
            } finally {
                setIsLoadingCiudades(false);
            }
        };

        cargarCiudades();
    }, [formData.pais]);

    // Cargar comunas cuando se selecciona una ciudad
    useEffect(() => {
        const cargarComunas = async () => {
            if (!formData.ciudad) {
                setComunas([]);
                setFormData(prev => ({
                    ...prev,
                    comuna: ''
                }));
                return;
            }

            setIsLoadingComunas(true);
            try {
                console.log('Solicitando comunas para ciudad ID:', formData.ciudad);
                const response = await fetch(`/api/ubicacion/comunas/por_ciudad/?ciudad_id=${formData.ciudad}`);

                if (!response.ok) {
                    throw new Error('Error al cargar comunas');
                }

                const data = await response.json();
                console.log('Respuesta de comunas:', data);

                // La respuesta ya debería ser un array
                const comunasData = Array.isArray(data) ? data : [];
                setComunas(comunasData);

                // Resetear comuna cuando cambia la ciudad
                setFormData(prev => ({
                    ...prev,
                    comuna: ''
                }));
            } catch (error) {
                console.error('Error al cargar comunas:', error);
                toast.error('Error al cargar las comunas. Intenta nuevamente.');
                setComunas([]);
            } finally {
                setIsLoadingComunas(false);
            }
        };

        cargarComunas();
    }, [formData.ciudad]);

    // Funciones para manejar integrantes
    const agregarIntegrante = () => {
        if (newIntegrante.trim()) {
            setFormData(prev => ({
                ...prev,
                integrantes: [...prev.integrantes, newIntegrante.trim()]
            }));
            setNewIntegrante('');
        }
    };

    const eliminarIntegrante = (index) => {
        setFormData(prev => ({
            ...prev,
            integrantes: prev.integrantes.filter((_, i) => i !== index)
        }));
    };

    // Funciones para manejar links
    const agregarLink = () => {
        if (newLink.tipo && newLink.url.trim()) {
            setFormData(prev => ({
                ...prev,
                links: [...prev.links, { ...newLink }]
            }));
            setNewLink({ tipo: '', url: '' });
        }
    };

    const eliminarLink = (index) => {
        setFormData(prev => ({
            ...prev,
            links: prev.links.filter((_, i) => i !== index)
        }));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleLinkChange = (e) => {
        const { name, value } = e.target;
        setNewLink(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.nombre_banda.trim()) newErrors.nombre_banda = 'El nombre de la banda es requerido';
        if (!formData.genero) newErrors.genero = 'El género musical es requerido';
        if (!formData.email_contacto.trim()) {
            newErrors.email_contacto = 'El correo electrónico es requerido';
        } else if (!/\S+@\S+\.\S+/.test(formData.email_contacto)) {
            newErrors.email_contacto = 'Por favor ingresa un correo electrónico válido';
        }
        if (!formData.mensaje.trim()) newErrors.mensaje = 'El mensaje es requerido';
        if (formData.integrantes.length === 0) newErrors.integrantes = 'Debes agregar al menos un integrante';
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('🚀 Iniciando envío del formulario...');
        console.log('📝 Datos del formulario:', formData);
        console.log('🔑 Token disponible:', !!token);
        console.log('👤 Usuario logueado:', isLoggedIn);

        // Limpiar errores previos
        setErrors({});

        if (!isLoggedIn) {
            const errorMsg = 'Debes iniciar sesión para enviar tu propuesta.';
            setErrors({ general: errorMsg });
            toast.error(errorMsg);
            return;
        }

        const newErrors = validateForm();
        if (Object.keys(newErrors).length > 0) {
            console.log('❌ Errores de validación:', newErrors);
            setErrors(newErrors);
            toast.error('Por favor corrige los errores en el formulario.');
            return;
        }

        setIsLoading(true);

        try {
            const dataToSend = {
                nombre_banda: formData.nombre_banda.trim(),
                email_contacto: formData.email_contacto.trim(),
                telefono_contacto: formData.telefono_contacto?.trim() || '',
                mensaje: formData.mensaje.trim(),
                documento_presentacion: formData.documento_presentacion?.trim() || '',
                genero: parseInt(formData.genero),
                comuna: formData.comuna ? parseInt(formData.comuna) : null,
                integrantes_data: formData.integrantes.filter(i => i.trim()),
                links_data: formData.links.filter(l => l.tipo && l.url.trim())
            };

            console.log('📤 Enviando datos:', dataToSend);

            const response = await fetch('/api/emergentes/api/bandas/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Respuesta exitosa:', data);
                toast.success('¡Propuesta enviada exitosamente! Te contactaremos pronto.');
                setSubmitted(true);

                // Limpiar formulario
                setFormData({
                    nombre_banda: '',
                    integrantes: [],
                    genero: '',
                    comuna: '',
                    email_contacto: '',
                    telefono_contacto: '',
                    mensaje: '',
                    links: [],
                    documento_presentacion: ''
                });
            } else {
                const errorData = await response.json();
                console.error('📄 Respuesta del servidor:', errorData);
                console.error('🔢 Código de estado:', response.status);

                let errorMessage = 'Error al enviar la propuesta. Inténtalo de nuevo.';

                if (errorData) {
                    console.log('📋 Datos del error:', errorData);

                    if (typeof errorData === 'object') {
                        // Mostrar errores específicos de campos
                        setErrors(errorData);

                        // Crear mensaje de error más específico
                        const firstError = Object.values(errorData)[0];
                        if (Array.isArray(firstError)) {
                            errorMessage = firstError[0];
                        } else if (typeof firstError === 'string') {
                            errorMessage = firstError;
                        }
                    } else {
                        errorMessage = errorData.toString();
                    }
                }

                toast.error(errorMessage);
                console.log('🚨 Error mostrado al usuario:', errorMessage);
            }
        } catch (error) {
            console.error('❌ Error completo:', error);
            toast.error('Error al enviar la propuesta. Inténtalo de nuevo.');
            console.log('🚨 Error mostrado al usuario:', error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const resetForm = () => {
        setSubmitted(false);
        setFormData({
            nombre_banda: '',
            integrantes: [],
            genero: '',
            comuna: '',
            email_contacto: '',
            telefono_contacto: '',
            mensaje: '',
            links: [],
            documento_presentacion: ''
        });
        setErrors({});
    };

    if (submitted) {
        return (
            <div className="success-container">
                <div className="card success-card">
                    <div className="success-icon">
                        <img 
                            src="/images/radiooriente.png" 
                            alt="Radio Oriente" 
                            style={{ width: '60px', height: '60px' }} 
                        />
                    </div>
                    <h2>¡Formulario Enviado Exitosamente!</h2>
                    <p>Gracias por enviar tu propuesta. Nuestro equipo revisará tu información y nos pondremos en contacto contigo pronto.</p>
                    <br />
                    <div className="buttons-container">
                        <button onClick={resetForm}>Enviar Otra Propuesta</button>
                        <button 
                            onClick={() => window.location.href = '/'} 
                            style={{ marginLeft: '10px' }}
                        >
                            Ir a Página Principal
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="emergente-container">
            <div className="emergente-wrapper">
                {/* Header */}
                <div className="emergente-header">
                    <div className="logo-title">
                        <div className="logo-circle">
                            <Music className="icon" />
                        </div>
                        <h1>Radio Oriente FM</h1>
                    </div>
                    <h2 className="gradient-text">Bandas Emergentes</h2>
                    <p>
                        ¿Eres parte de una banda emergente? ¡Queremos conocerte! Envíanos tu información 
                        y podrías ser parte de nuestra programación especial para artistas locales.
                    </p>
                </div>

                <div className="grid grid-cols-2">
                    {/* Información */}
                    <div className="info-section">
                        <div className="card">
                            <div className="card-header">
                                <Users className="icon" />
                                <h3>¿Por qué participar?</h3>
                            </div>
                            <ul className="benefits-list">
                                <li>Exposición en nuestra programación</li>
                                <li>Entrevistas en vivo</li>
                                <li>Promoción en redes sociales</li>
                                <li>Conexión con otros artistas</li>
                                <li>Apoyo al talento local</li>
                            </ul>
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <Link className="icon" />
                                <h3>Proceso de Selección</h3>
                            </div>
                            <div className="process-steps">
                                <div className="step"><span>1</span> Envías tu información</div>
                                <div className="step"><span>2</span> Revisamos tu material</div>
                                <div className="step"><span>3</span> Te contactamos</div>
                            </div>
                        </div>
                    </div>

                    {/* Formulario */}
                    <div className="form-section">
                        <div className="card">
                            <div className="card-content">
                                <div className="card-header">
                                    <h3 className="card-title">Envíanos tu Información</h3>
                                </div>

                                {errors.general && <div className="error-box">{errors.general}</div>}

                                <form onSubmit={handleSubmit}>
                                    {/* Nombre de la banda */}
                                    <div className="form-group">
                                        <label>Nombre de la Banda *</label>
                                        <input
                                            type="text"
                                            name="nombre_banda"
                                            value={formData.nombre_banda}
                                            onChange={handleChange}
                                            className={errors.nombre_banda ? 'error' : ''}
                                            placeholder="Ej: Los Prisioneros"
                                        />
                                        {errors.nombre_banda && <p className="error-text">{errors.nombre_banda}</p>}
                                    </div>

                                {/* Integrantes */}
                                <div className="form-group">
                                    <label>Integrantes *</label>
                                    <div className="integrantes-section">
                                        <div className="add-section">
                                            <input
                                                type="text"
                                                value={newIntegrante}
                                                onChange={(e) => setNewIntegrante(e.target.value)}
                                                placeholder="Nombre del integrante"
                                                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), agregarIntegrante())}
                                            />
                                            <button type="button" onClick={agregarIntegrante} className="btn btn-primary btn-small">
                                                <Plus size={16} />
                                                Agregar
                                            </button>
                                        </div>
                                        {formData.integrantes.length > 0 && (
                                            <div className="integrantes-list">
                                                {formData.integrantes.map((integrante, index) => (
                                                    <div key={index} className="integrante-item">
                                                        <span>{integrante}</span>
                                                        <button 
                                                            type="button" 
                                                            onClick={() => eliminarIntegrante(index)}
                                                            className="btn-remove"
                                                        >
                                                            <X size={14} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    {errors.integrantes && <p className="error-text">{errors.integrantes}</p>}
                                </div>

                                <div className="form-row">
                                    {/* Género Musical */}
                                    <div className="form-group">
                                        <label>Género Musical *</label>
                                        <select
                                            name="genero"
                                            value={formData.genero}
                                            onChange={handleChange}
                                            className={errors.genero ? 'error' : ''}
                                        >
                                            <option value="">Selecciona un género</option>
                                            {generos.map((genero) => (
                                                <option key={genero.id} value={genero.id}>
                                                    {genero.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.genero && <p className="error-text">{errors.genero}</p>}
                                    </div>
                                </div>

                                {/* Ubicación */}
                                <div className="form-row location-row">
                                    <div className="form-group">
                                        <label htmlFor="pais">País *</label>
                                        <select
                                            id="pais"
                                            name="pais"
                                            value={formData.pais}
                                            onChange={handleChange}
                                            className={errors.pais ? 'error' : ''}
                                            disabled={isLoading}
                                        >
                                            <option value="">Selecciona un país</option>
                                            {paises.map(pais => (
                                                <option key={pais.id} value={pais.id}>
                                                    {pais.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.pais && <p className="error-text">{errors.pais}</p>}
                                    </div>

                                    <div className={`form-group ${isLoadingCiudades ? 'loading' : ''}`}>
                                        <label htmlFor="ciudad">Región *</label>
                                        <select
                                            id="ciudad"
                                            name="ciudad"
                                            value={formData.ciudad}
                                            onChange={handleChange}
                                            className={errors.ciudad ? 'error' : ''}
                                            disabled={!formData.pais || isLoadingCiudades}
                                        >
                                            <option value="">
                                                {isLoadingCiudades ? 'Cargando regiones...' : 'Selecciona una región'}
                                            </option>
                                            {ciudades.map(ciudad => (
                                                <option key={ciudad.id} value={ciudad.id}>
                                                    {ciudad.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.ciudad && <p className="error-text">{errors.ciudad}</p>}
                                    </div>

                                    <div className={`form-group ${isLoadingComunas ? 'loading' : ''}`}>
                                        <label htmlFor="comuna">Comuna *</label>
                                        <select
                                            id="comuna"
                                            name="comuna"
                                            value={formData.comuna}
                                            onChange={handleChange}
                                            className={errors.comuna ? 'error' : ''}
                                            disabled={!formData.ciudad || isLoadingComunas}
                                        >
                                            <option value="">
                                                {isLoadingComunas ? 'Cargando comunas...' : 'Selecciona una comuna'}
                                            </option>
                                            {comunas.map(comuna => (
                                                <option key={comuna.id} value={comuna.id}>
                                                    {comuna.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.comuna && <p className="error-text">{errors.comuna}</p>}
                                    </div>
                                </div>

                                {/* Contacto */}
                                <div className="form-row">
                                    {/* Email */}
                                    <div className="form-group">
                                        <label>Correo Electrónico *</label>
                                        <input
                                            type="email"
                                            name="email_contacto"
                                            value={formData.email_contacto}
                                            onChange={handleChange}
                                            className={errors.email_contacto ? 'error' : ''}
                                            placeholder="banda@ejemplo.com"
                                        />
                                        {errors.email_contacto && <p className="error-text">{errors.email_contacto}</p>}
                                    </div>

                                    {/* Teléfono */}
                                    <div className="form-group">
                                        <label>Teléfono</label>
                                        <input
                                            type="tel"
                                            name="telefono_contacto"
                                            value={formData.telefono_contacto}
                                            onChange={handleChange}
                                            placeholder="+56 9 1234 5678"
                                        />
                                    </div>
                                </div>

                                {/* Links */}
                                <div className="form-group">
                                    <label>Links (Redes Sociales, Música, etc.)</label>
                                    <div className="links-section">
                                        <div className="add-link-container">
                                            <div className="select-with-icon">
                                                <select
                                                    name="tipo"
                                                    value={newLink.tipo}
                                                    onChange={handleLinkChange}
                                                    className="link-type-select"
                                                >
                                                    <option value="">Tipo de link</option>
                                                    <option value="spotify">Spotify</option>
                                                    <option value="youtube">YouTube</option>
                                                    <option value="instagram">Instagram</option>
                                                    <option value="facebook">Facebook</option>
                                                    <option value="soundcloud">SoundCloud</option>
                                                    <option value="website">Sitio Web</option>
                                                    <option value="otro">Otro</option>
                                                </select>
                                                {newLink.tipo && (
                                                    <span className="select-icon">
                                                        {newLink.tipo === 'spotify' && <FaSpotify data-icon="FaSpotify" />}
                                                        {newLink.tipo === 'youtube' && <FaYoutube data-icon="FaYoutube" />}
                                                        {newLink.tipo === 'instagram' && <FaInstagram data-icon="FaInstagram" />}
                                                        {newLink.tipo === 'facebook' && <FaFacebook data-icon="FaFacebook" />}
                                                        {newLink.tipo === 'soundcloud' && <FaSoundcloud data-icon="FaSoundcloud" />}
                                                        {newLink.tipo === 'website' && <FaGlobe data-icon="FaGlobe" />}
                                                        {newLink.tipo === 'otro' && <FaLink data-icon="FaLink" />}
                                                    </span>
                                                )}
                                            </div>
                                            <input
                                                type="url"
                                                name="url"
                                                value={newLink.url}
                                                onChange={handleLinkChange}
                                                placeholder="https://..."
                                                className="link-url-input"
                                            />
                                            <button 
                                                type="button" 
                                                onClick={agregarLink} 
                                                className="btn btn-primary btn-small"
                                                disabled={!newLink.tipo || !newLink.url}
                                            >
                                                <Plus size={16} />
                                                Agregar
                                            </button>
                                        </div>
                                        {formData.links.length > 0 && (
                                            <div className="links-list">
                                                {formData.links.map((link, index) => (
                                                    <div key={index} className="link-item">
                                                        <div className="link-info">
                                                            <span className="link-type-badge">{link.tipo}</span>
                                                            <span className="link-url">{link.url}</span>
                                                        </div>
                                                        <button 
                                                            type="button" 
                                                            onClick={() => eliminarLink(index)}
                                                            className="btn-remove"
                                                            title="Eliminar link"
                                                        >
                                                            <X size={16} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Documento de presentación */}
                                <div className="form-group">
                                    <label>Documento de Presentación (URL)</label>
                                    <input
                                        type="url"
                                        name="documento_presentacion"
                                        value={formData.documento_presentacion}
                                        onChange={handleChange}
                                        placeholder="https://drive.google.com/... o enlace a tu EPK"
                                    />
                                    <small>Enlace a tu EPK, portfolio o material promocional</small>
                                </div>

                                {/* Mensaje */}
                                <div className="form-group">
                                    <label>Mensaje *</label>
                                    <textarea
                                        name="mensaje"
                                        value={formData.mensaje}
                                        onChange={handleChange}
                                        className={errors.mensaje ? 'error' : ''}
                                        rows="4"
                                        placeholder="Cuéntanos sobre tu banda, tu música y por qué quieres participar..."
                                    />
                                    {errors.mensaje && <p className="error-text">{errors.mensaje}</p>}
                                </div>

                                <button 
                                    type="submit" 
                                    className="btn btn-primary" 
                                    disabled={isLoading}
                                >
                                    <Send size={16} />
                                    {isLoading ? 'Enviando...' : 'Enviar Propuesta'}
                                </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Emergente;
