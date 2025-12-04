import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Music, Users, Link, Send, X, Plus, CheckCircle, User, MapPin, Mail, Phone, Globe, Radio, Home, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';
import {
  FaSpotify,
  FaYoutube,
  FaInstagram,
  FaFacebook,
  FaTiktok,
  FaSoundcloud,
  FaLink,
  FaTwitter,
  FaBandcamp,
  FaApple
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

    const [currentStep, setCurrentStep] = useState(0);
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
    const [direction, setDirection] = useState(1);

    const token = localStorage.getItem('token');
    const isLoggedIn = Boolean(token);

    const steps = [
        { id: 0, title: 'Banda', icon: Music, description: 'Información básica' },
        { id: 1, title: 'Integrantes', icon: Users, description: 'Miembros del grupo' },
        { id: 2, title: 'Ubicación', icon: MapPin, description: 'De dónde son' },
        { id: 3, title: 'Contacto', icon: Mail, description: 'Cómo contactarlos' },
        { id: 4, title: 'Links', icon: Link, description: 'Redes y música' },
    ];

    //cargar países al iniciar
    useEffect(() => {
        const inicializarDatos = async () => {
            try {
                const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const paisesResponse = await fetch(`${base}/api/ubicacion/paises/`);
                if (!paisesResponse.ok) {
                    throw new Error('Error al cargar países');
                }
                const paisesData = await paisesResponse.json();
                const paisesArray = paisesData.results || (Array.isArray(paisesData) ? paisesData : []);
                const chile = paisesArray.find(p => p.nombre === 'Chile');

                if (!chile) {
                    console.log('Chile no encontrado, cargando datos desde API...');
                    const loadingToast = toast.loading('Cargando regiones y comunas de Chile desde API oficial...');

                    try {
                        const response = await fetch(`${base}/api/ubicacion/paises/reiniciar_datos_chile/`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        if (response.ok) {
                            const data = await response.json();
                            toast.dismiss(loadingToast);
                            toast.success(`${data.message}\n${data.regiones_creadas} regiones\n${data.comunas_creadas} comunas`);

                            const paisesActualizadosResponse = await fetch(`${base}/api/ubicacion/paises/`);
                            if (paisesActualizadosResponse.ok) {
                                const paisesActualizados = await paisesActualizadosResponse.json();
                                const paisesActualizadosArray = paisesActualizados.results || (Array.isArray(paisesActualizados) ? paisesActualizados : []);
                                setPaises(paisesActualizadosArray);
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
                    const ciudadesResponse = await fetch(`${base}/api/ubicacion/ciudades/por_pais/?pais_id=${chile.id}`);
                    const ciudadesData = ciudadesResponse.ok ? await ciudadesResponse.json() : [];

                    if (!ciudadesData || ciudadesData.length < 10) {
                        console.log('Pocas o ninguna región, recargando desde API...');
                        const loadingToast = toast.loading('Actualizando datos desde API oficial de Chile...');

                        try {
                            const response = await fetch(`${base}/api/ubicacion/paises/reiniciar_datos_chile/`, {
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

        const cargarGeneros = async () => {
            try {
                const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${base}/api/radio/api/generos/`);
                if (!response.ok) {
                    throw new Error('Error al cargar géneros');
                }
                const data = await response.json();
                const generosArray = data.results || (Array.isArray(data) ? data : []);
                setGeneros(generosArray);
            } catch (error) {
                console.error('Error al cargar géneros musicales:', error);
                toast.error('Error al cargar la lista de géneros musicales');
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

    //cargar ciudades cuando se selecciona un país
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
                const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${base}/api/ubicacion/ciudades/por_pais/?pais_id=${formData.pais}`);
                if (!response.ok) {
                    throw new Error('Error al cargar ciudades');
                }
                const data = await response.json();
                const ciudadesData = Array.isArray(data) ? data : [];
                setCiudades(ciudadesData);
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

    //cargar comunas cuando se selecciona una ciudad
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
                const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const response = await fetch(`${base}/api/ubicacion/comunas/por_ciudad/?ciudad_id=${formData.ciudad}`);
                if (!response.ok) {
                    throw new Error('Error al cargar comunas');
                }
                const data = await response.json();
                const comunasData = Array.isArray(data) ? data : [];
                setComunas(comunasData);
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

    const handlePhoneChange = (e) => {
        const { value } = e.target;
        //solo permitir +, -, espacios y números
        const sanitizedValue = value.replace(/[^0-9+\-\s]/g, '');
        setFormData(prev => ({
            ...prev,
            telefono_contacto: sanitizedValue
        }));

        if (errors.telefono_contacto) {
            setErrors(prev => ({
                ...prev,
                telefono_contacto: ''
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

    const validateStep = (step) => {
        const newErrors = {};

        switch(step) {
            case 0:
                if (!formData.nombre_banda.trim()) newErrors.nombre_banda = 'El nombre de la banda es requerido';
                if (!formData.genero) newErrors.genero = 'El género musical es requerido';
                break;
            case 1:
                if (formData.integrantes.length === 0) newErrors.integrantes = 'Debes agregar al menos un integrante';
                break;
            case 2:
                //ubicación es obligatoria
                if (!formData.pais) newErrors.pais = 'El país es requerido';
                if (!formData.ciudad) newErrors.ciudad = 'La región es requerida';
                if (!formData.comuna) newErrors.comuna = 'La comuna es requerida';
                break;
            case 3:
                if (!formData.email_contacto.trim()) {
                    newErrors.email_contacto = 'El correo electrónico es requerido';
                } else if (!/\S+@\S+\.\S+/.test(formData.email_contacto)) {
                    newErrors.email_contacto = 'Por favor ingresa un correo electrónico válido';
                }
                //teléfono es obligatorio
                if (!formData.telefono_contacto.trim()) {
                    newErrors.telefono_contacto = 'El teléfono es requerido';
                } else {
                    const phoneRegex = /^[+\-\s0-9]+$/;
                    if (!phoneRegex.test(formData.telefono_contacto)) {
                        newErrors.telefono_contacto = 'Solo se permiten números, +, - y espacios';
                    }
                }
                if (!formData.mensaje.trim()) newErrors.mensaje = 'El mensaje es requerido';
                break;
            case 4:
                //al menos un link es obligatorio
                if (formData.links.length === 0) newErrors.links = 'Debes agregar al menos un link de tu música o redes';
                break;
            default:
                break;
        }

        return newErrors;
    };

    const nextStep = () => {
        const stepErrors = validateStep(currentStep);
        if (Object.keys(stepErrors).length > 0) {
            setErrors(stepErrors);
            toast.error('Por favor completa los campos requeridos');
            return;
        }
        setErrors({});
        setDirection(1);
        setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    };

    const prevStep = () => {
        setDirection(-1);
        setCurrentStep(prev => Math.max(prev - 1, 0));
    };

    const goToStep = (step) => {
        //validar pasos anteriores antes de saltar
        for (let i = 0; i < step; i++) {
            const stepErrors = validateStep(i);
            if (Object.keys(stepErrors).length > 0) {
                setErrors(stepErrors);
                setCurrentStep(i);
                toast.error('Por favor completa los campos requeridos');
                return;
            }
        }
        setDirection(step > currentStep ? 1 : -1);
        setCurrentStep(step);
    };

    const handleSubmit = async () => {
        //validar todos los pasos
        for (let i = 0; i <= currentStep; i++) {
            const stepErrors = validateStep(i);
            if (Object.keys(stepErrors).length > 0) {
                setErrors(stepErrors);
                setCurrentStep(i);
                toast.error('Por favor completa los campos requeridos');
                return;
            }
        }

        if (!isLoggedIn) {
            toast.error('Debes iniciar sesión para enviar tu propuesta.');
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
            const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${base}/api/emergentes/api/bandas/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                toast.success('¡Propuesta enviada exitosamente!');
                setSubmitted(true);
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
                let errorMessage = 'Error al enviar la propuesta. Inténtalo de nuevo.';
                if (errorData) {
                    setErrors(errorData);
                    const firstError = Object.values(errorData)[0];
                    if (Array.isArray(firstError)) {
                        errorMessage = firstError[0];
                    } else if (typeof firstError === 'string') {
                        errorMessage = firstError;
                    }
                }
                toast.error(errorMessage);
            }
        } catch (error) {
            console.error('Error:', error);
            toast.error('Error al enviar la propuesta. Inténtalo de nuevo.');
        } finally {
            setIsLoading(false);
        }
    };

    const resetForm = () => {
        setSubmitted(false);
        setCurrentStep(0);
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

    const getSocialIcon = (tipo) => {
        switch(tipo.toLowerCase()) {
            case 'spotify': return <FaSpotify className="social-icon spotify" />;
            case 'youtube': return <FaYoutube className="social-icon youtube" />;
            case 'instagram': return <FaInstagram className="social-icon instagram" />;
            case 'facebook': return <FaFacebook className="social-icon facebook" />;
            case 'tiktok': return <FaTiktok className="social-icon tiktok" />;
            case 'soundcloud': return <FaSoundcloud className="social-icon soundcloud" />;
            case 'twitter': return <FaTwitter className="social-icon twitter" />;
            case 'bandcamp': return <FaBandcamp className="social-icon bandcamp" />;
            case 'apple music': return <FaApple className="social-icon apple" />;
            case 'sitio web': return <Globe className="social-icon website" />;
            default: return <FaLink className="social-icon default" />;
        }
    };

    const slideVariants = {
        enter: (direction) => ({
            x: direction > 0 ? 300 : -300,
            opacity: 0
        }),
        center: {
            x: 0,
            opacity: 1
        },
        exit: (direction) => ({
            x: direction < 0 ? 300 : -300,
            opacity: 0
        })
    };

    if (submitted) {
        return (
            <div className="success-container">
                <motion.div
                    className="success-card"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ type: "spring", duration: 0.6 }}
                >
                    <div className="success-animation">
                        <motion.div
                            className="success-icon-wrapper"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                        >
                            <CheckCircle className="success-icon" size={80} />
                        </motion.div>
                        <div className="success-waves">
                            <div className="wave wave-1"></div>
                            <div className="wave wave-2"></div>
                            <div className="wave wave-3"></div>
                        </div>
                    </div>

                    <motion.div
                        className="success-content"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.4 }}
                    >
                        <h2 className="success-title">¡Propuesta Enviada!</h2>
                        <p className="success-message">
                            Tu banda ha sido registrada. Nuestro equipo revisará tu propuesta y te contactaremos pronto.
                        </p>

                        <div className="success-info">
                            <motion.div
                                className="info-item"
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.5 }}
                            >
                                <Music className="info-icon" />
                                <span>Revisión en 3-5 días hábiles</span>
                            </motion.div>
                            <motion.div
                                className="info-item"
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.6 }}
                            >
                                <Mail className="info-icon" />
                                <span>Te contactaremos por email</span>
                            </motion.div>
                            <motion.div
                                className="info-item"
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.7 }}
                            >
                                <Radio className="info-icon" />
                                <span>Posible emisión los domingos</span>
                            </motion.div>
                        </div>
                    </motion.div>

                    <motion.div
                        className="success-actions"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.8 }}
                    >
                        <button onClick={resetForm} className="btn btn-primary success-btn">
                            <Plus size={20} />
                            Enviar Otra Propuesta
                        </button>
                        <button
                            onClick={() => window.location.href = '/'}
                            className="btn btn-outline success-btn"
                        >
                            <Home size={20} />
                            Ir al Inicio
                        </button>
                    </motion.div>
                </motion.div>
            </div>
        );
    }

    const renderStepContent = () => {
        switch(currentStep) {
            case 0:
                return (
                    <div className="step-content">
                        <div className="step-header">
                            <Sparkles className="step-header-icon" />
                            <div>
                                <h3>Información de tu Banda</h3>
                                <p>Cuéntanos sobre tu proyecto musical</p>
                            </div>
                        </div>

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
                );

            case 1:
                return (
                    <div className="step-content">
                        <div className="step-header">
                            <Users className="step-header-icon" />
                            <div>
                                <h3>Integrantes</h3>
                                <p>¿Quiénes conforman tu banda?</p>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Agregar Integrante *</label>
                            <div className="add-section">
                                <input
                                    type="text"
                                    value={newIntegrante}
                                    onChange={(e) => setNewIntegrante(e.target.value)}
                                    placeholder="Nombre del integrante"
                                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), agregarIntegrante())}
                                />
                                <motion.button
                                    type="button"
                                    onClick={agregarIntegrante}
                                    className="btn btn-primary btn-small"
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    <Plus size={16} />
                                    Agregar
                                </motion.button>
                            </div>
                            {errors.integrantes && <p className="error-text">{errors.integrantes}</p>}
                        </div>

                        <AnimatePresence>
                            {formData.integrantes.length > 0 && (
                                <motion.div
                                    className="integrantes-list"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                >
                                    {formData.integrantes.map((integrante, index) => (
                                        <motion.div
                                            key={index}
                                            className="integrante-item"
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: 20 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <div className="integrante-info">
                                                <User className="integrante-icon" size={18} />
                                                <span className="integrante-nombre">{integrante}</span>
                                            </div>
                                            <motion.button
                                                type="button"
                                                onClick={() => eliminarIntegrante(index)}
                                                className="btn-remove"
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                            >
                                                <X size={14} />
                                            </motion.button>
                                        </motion.div>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                );

            case 2:
                return (
                    <div className="step-content">
                        <div className="step-header">
                            <MapPin className="step-header-icon" />
                            <div>
                                <h3>Ubicación</h3>
                                <p>¿De dónde son?</p>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>País *</label>
                            <select
                                name="pais"
                                value={formData.pais}
                                onChange={handleChange}
                                disabled={isLoading}
                                className={errors.pais ? 'error' : ''}
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

                        <div className="form-row">
                            <div className={`form-group ${isLoadingCiudades ? 'loading' : ''}`}>
                                <label>Región *</label>
                                <select
                                    name="ciudad"
                                    value={formData.ciudad}
                                    onChange={handleChange}
                                    disabled={!formData.pais || isLoadingCiudades}
                                    className={errors.ciudad ? 'error' : ''}
                                >
                                    <option value="">
                                        {isLoadingCiudades ? 'Cargando...' : 'Selecciona una región'}
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
                                <label>Comuna *</label>
                                <select
                                    name="comuna"
                                    value={formData.comuna}
                                    className={errors.comuna ? 'error' : ''}
                                    onChange={handleChange}
                                    disabled={!formData.ciudad || isLoadingComunas}
                                >
                                    <option value="">
                                        {isLoadingComunas ? 'Cargando...' : 'Selecciona una comuna'}
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
                    </div>
                );

            case 3:
                return (
                    <div className="step-content">
                        <div className="step-header">
                            <Mail className="step-header-icon" />
                            <div>
                                <h3>Contacto</h3>
                                <p>¿Cómo podemos contactarte?</p>
                            </div>
                        </div>

                        <div className="form-row">
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

                            <div className="form-group">
                                <label>Teléfono *</label>
                                <input
                                    type="tel"
                                    name="telefono_contacto"
                                    value={formData.telefono_contacto}
                                    onChange={handlePhoneChange}
                                    placeholder="+56 9 1234 5678"
                                    className={errors.telefono_contacto ? 'error' : ''}
                                />
                                {errors.telefono_contacto && <p className="error-text">{errors.telefono_contacto}</p>}
                            </div>
                        </div>

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
                    </div>
                );

            case 4:
                return (
                    <div className="step-content">
                        <div className="step-header">
                            <Link className="step-header-icon" />
                            <div>
                                <h3>Links y Redes</h3>
                                <p>Comparte tu música y redes sociales</p>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Agregar Link *</label>
                            {errors.links && <p className="error-text" style={{ marginBottom: '0.5rem' }}>{errors.links}</p>}
                            <div className="add-link-container">
                                <div className="select-with-icon">
                                    <select
                                        name="tipo"
                                        value={newLink.tipo}
                                        onChange={handleLinkChange}
                                        className="link-type-select"
                                    >
                                        <option value="">Tipo</option>
                                        <option value="spotify">Spotify</option>
                                        <option value="youtube">YouTube</option>
                                        <option value="instagram">Instagram</option>
                                        <option value="facebook">Facebook</option>
                                        <option value="soundcloud">SoundCloud</option>
                                        <option value="website">Sitio Web</option>
                                        <option value="otro">Otro</option>
                                    </select>
                                    {newLink.tipo && (
                                        <span className={`select-icon ${newLink.tipo}`}>
                                            {newLink.tipo === 'spotify' && <FaSpotify size={18} />}
                                            {newLink.tipo === 'youtube' && <FaYoutube size={18} />}
                                            {newLink.tipo === 'instagram' && <FaInstagram size={18} />}
                                            {newLink.tipo === 'facebook' && <FaFacebook size={18} />}
                                            {newLink.tipo === 'soundcloud' && <FaSoundcloud size={18} />}
                                            {newLink.tipo === 'website' && <Globe size={18} />}
                                            {newLink.tipo === 'otro' && <FaLink size={18} />}
                                        </span>
                                    )}
                                </div>
                                <input
                                    type="url"
                                    name="url"
                                    value={newLink.url}
                                    onChange={handleLinkChange}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            e.preventDefault();
                                            if (newLink.tipo && newLink.url) {
                                                agregarLink();
                                            }
                                        }
                                    }}
                                    placeholder="https://..."
                                    className="link-url-input"
                                />
                                <motion.button
                                    type="button"
                                    onClick={agregarLink}
                                    className="btn btn-primary btn-small"
                                    disabled={!newLink.tipo || !newLink.url}
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    <Plus size={16} />
                                </motion.button>
                            </div>
                        </div>

                        <AnimatePresence>
                            {formData.links.length > 0 && (
                                <motion.div
                                    className="links-list"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                >
                                    {formData.links.map((link, index) => (
                                        <motion.div
                                            key={index}
                                            className="link-item"
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: 10 }}
                                        >
                                            <div className="link-info">
                                                <div className="link-icon-wrapper">
                                                    {getSocialIcon(link.tipo)}
                                                </div>
                                                <div className="link-details">
                                                    <span className="link-type">{link.tipo}</span>
                                                    <span className="link-url">{link.url}</span>
                                                </div>
                                            </div>
                                            <motion.button
                                                type="button"
                                                onClick={() => eliminarLink(index)}
                                                className="btn-remove"
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                            >
                                                <X size={16} />
                                            </motion.button>
                                        </motion.div>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="form-group" style={{ marginTop: '1.5rem' }}>
                            <label>Documento de Presentación (URL)</label>
                            <input
                                type="url"
                                name="documento_presentacion"
                                value={formData.documento_presentacion}
                                onChange={handleChange}
                                onKeyDown={(e) => e.key === 'Enter' && e.preventDefault()}
                                placeholder="https://drive.google.com/... o enlace a tu EPK"
                            />
                            <small>Enlace a tu EPK, portfolio o material promocional</small>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="emergente-container">
            <div className="container">
                <motion.div
                    className="page-header"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Music className="page-icon" />
                    <div>
                        <h1 className="page-title">Bandas Emergentes</h1>
                        <p className="page-subtitle">
                            ¿Eres parte de una banda emergente? ¡Queremos conocerte!
                        </p>
                    </div>
                </motion.div>

                <div className="emergente-wizard">
                    {/*stepper*/}
                    <motion.div
                        className="stepper"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        {steps.map((step, index) => {
                            const StepIcon = step.icon;
                            const isActive = currentStep === index;
                            const isCompleted = currentStep > index;

                            return (
                                <React.Fragment key={step.id}>
                                    <motion.div
                                        className={`step-indicator ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                                        onClick={() => goToStep(index)}
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                    >
                                        <div className="step-circle">
                                            {isCompleted ? (
                                                <CheckCircle size={20} />
                                            ) : (
                                                <StepIcon size={20} />
                                            )}
                                        </div>
                                        <div className="step-label">
                                            <span className="step-title">{step.title}</span>
                                            <span className="step-desc">{step.description}</span>
                                        </div>
                                    </motion.div>
                                    {index < steps.length - 1 && (
                                        <div className={`step-connector ${isCompleted ? 'completed' : ''}`} />
                                    )}
                                </React.Fragment>
                            );
                        })}
                    </motion.div>

                    {/*form card*/}
                    <motion.div
                        className="wizard-card"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        {errors.general && (
                            <motion.div
                                className="error-box"
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                            >
                                {errors.general}
                            </motion.div>
                        )}

                        <form onSubmit={(e) => {
                            e.preventDefault();
                            //solo enviar si estamos en el último paso y se hizo clic explícito
                        }}>
                            <AnimatePresence mode="wait" custom={direction}>
                                <motion.div
                                    key={currentStep}
                                    custom={direction}
                                    variants={slideVariants}
                                    initial="enter"
                                    animate="center"
                                    exit="exit"
                                    transition={{ type: "tween", duration: 0.3 }}
                                >
                                    {renderStepContent()}
                                </motion.div>
                            </AnimatePresence>

                            {/*navigation*/}
                            <div className="wizard-navigation">
                                <motion.button
                                    type="button"
                                    onClick={prevStep}
                                    className="btn btn-secondary"
                                    disabled={currentStep === 0}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <ChevronLeft size={20} />
                                    Anterior
                                </motion.button>

                                <div className="step-counter">
                                    {currentStep + 1} / {steps.length}
                                </div>

                                {currentStep < steps.length - 1 ? (
                                    <motion.button
                                        type="button"
                                        onClick={nextStep}
                                        className="btn btn-primary"
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        Siguiente
                                        <ChevronRight size={20} />
                                    </motion.button>
                                ) : (
                                    <motion.button
                                        type="button"
                                        onClick={handleSubmit}
                                        className="btn btn-primary btn-submit"
                                        disabled={isLoading}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <Send size={18} />
                                        {isLoading ? 'Enviando...' : 'Enviar Propuesta'}
                                    </motion.button>
                                )}
                            </div>
                        </form>
                    </motion.div>

                    {/*info cards*/}
                    <motion.div
                        className="info-cards"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                    >
                        <div className="info-card">
                            <div className="info-card-icon">
                                <Radio />
                            </div>
                            <h4>Espacio Dominical</h4>
                            <p>Tu música puede sonar en nuestro espacio de 12:00 a 15:00 hrs los domingos.</p>
                        </div>
                        <div className="info-card">
                            <div className="info-card-icon">
                                <Users />
                            </div>
                            <h4>Entrevistas en Vivo</h4>
                            <p>Posibilidad de entrevistas y conversación sobre tu proyecto.</p>
                        </div>
                        <div className="info-card">
                            <div className="info-card-icon">
                                <Globe />
                            </div>
                            <h4>Difusión</h4>
                            <p>Difusión en Radio Oriente FM y nuestras redes sociales.</p>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default Emergente;
