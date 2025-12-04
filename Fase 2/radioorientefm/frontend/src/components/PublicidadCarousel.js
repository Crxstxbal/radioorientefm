import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import ColorThief from 'colorthief';
import './PublicidadCarousel.css';

function parseDims(dimStr) {
  if (!dimStr) return null;
  const m = String(dimStr).match(/(\d+)\s*x\s*(\d+)/i);
  if (!m) return null;
  return { w: parseInt(m[1], 10), h: parseInt(m[2], 10) };
}

//variantes de animacion para los paneles
const panelVariants = {
  hidden: (position) => ({
    opacity: 0,
    x: position === 'left-fixed' ? -80 : 80,
    transition: { duration: 0.4, ease: 'easeInOut' }
  }),
  visible: { 
    opacity: 1,
    x: 0,
    transition: { 
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
      delay: 0.1
    }
  }
};

export default function PublicidadCarousel({ 
  dimensiones, 
  query, 
  position = 'inline', 
  autoPlayMs = 5000,
  debug = true,
  reopenHours = 0.1667 //10 minutos cerrado, luego de eso vuelve a aparecer
}) {
  const [isVisible, setIsVisible] = useState(false);
  const location = useLocation();
  const isHomePage = location.pathname === '/';
  const panelRef = useRef(null);
  const [items, setItems] = useState([]);
  const [index, setIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dominantColor, setDominantColor] = useState('#4f46e5');
  const [dismissed, setDismissed] = useState(false);
  const colorThief = useRef(new ColorThief());
  const timerRef = useRef(null);
  const dims = useMemo(() => parseDims(dimensiones), [dimensiones]);
  const handleDismiss = () => {
    try {
      const key = `adPanelDismissed:${position}`;
      localStorage.setItem(key, String(Date.now()));
    } catch (_) {}
    setDismissed(true);
  };

  //persistencia de cierre con reapertura automática
  useEffect(() => {
    if (position !== 'left-fixed' && position !== 'right-fixed' && position !== 'bottom') return;
    try {
      const key = `adPanelDismissed:${position}`;
      const ts = Number(localStorage.getItem(key) || 0);
      const ttl = Math.max(1, Number(reopenHours)) * 60 * 60 * 1000; // horas -> ms
      if (ts && Date.now() - ts < ttl) {
        setDismissed(true);
      } else if (ts) {
        localStorage.removeItem(key);
        setDismissed(false);
      }
    } catch (_) {}
  }, [position]);

  //reapertura automática en footer sin recargar la página
  useEffect(() => {
    if (position !== 'bottom') return;
    let timeoutId;
    try {
      const key = `adPanelDismissed:${position}`;
      const ts = Number(localStorage.getItem(key) || 0);
      const ttl = Math.max(1, Number(reopenHours)) * 60 * 60 * 1000; // horas -> ms
      if (ts) {
        const remaining = ttl - (Date.now() - ts);
        if (remaining > 0) {
          timeoutId = setTimeout(() => {
            try { localStorage.removeItem(key); } catch (_) {}
            setDismissed(false);
          }, remaining);
        } else {
          localStorage.removeItem(key);
          setDismissed(false);
        }
      }
    } catch (_) {}
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [position, reopenHours, dismissed]);

  //obtener datos de publicidad
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);


    async function load() {
      try {
        const params = new URLSearchParams();
        if (dimensiones) params.set('dimensiones', dimensiones);
        if (query) params.set('q', query);
        params.set('limit', '100');
        
        const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const url = `${base}/dashboard/api/publicidad/activas/?${params.toString()}`;

        const startTime = performance.now();
        const resp = await fetch(url);
        const data = await resp.json();
        const endTime = performance.now();

        if (!cancelled) {
          if (data?.success && Array.isArray(data.items)) {
            setItems(data.items);
            setIndex(0);
            if (data.items.length === 0 && debug && import.meta.env.DEV) {
              console.warn(`[PublicidadCarousel] No ads found for position=${position}`);
            }
          } else {
            setError(data?.message || 'Error al cargar publicidad');
            console.error('[PublicidadCarousel] API error:', data);
          }
        }
      } catch (e) {
        console.error('[PublicidadCarousel] Error fetching ads:', e);
        if (!cancelled) {
          setError('Error de conexión');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [dimensiones, query, position, debug]);

  const throttle = useCallback((func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }, []);

  const impressedOnceRef = useRef(new Set());

  const trackImpression = async (campaignId) => {
    try {
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      await fetch(`${base}/dashboard/api/publicidad/campanias/${campaignId}/impresion/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (e) {
    }
  };

  const trackClick = async (campaignId) => {
    try {
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${base}/dashboard/api/publicidad/campanias/${campaignId}/click/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      return await res.json().catch(() => ({}));
    } catch (e) {
      if (debug && import.meta.env.DEV) console.warn('[PublicidadCarousel] Error tracking click', e);
      return {};
    }
  };

  const lastScrollY = useRef(0);
  
  useEffect(() => {
    if (!isHomePage || (position !== 'left-fixed' && position !== 'right-fixed')) {
      return;
    }

    const handleScroll = () => {
      //para que aparezca la animacion de la publicidad cuando se llega a la seccion de ultimos articulos
      const sections = document.querySelectorAll('section');
      let articlesSection = null;
      
      for (const section of sections) {
        const h2 = section.querySelector('h2.section-title');
        if (h2 && h2.textContent.includes('Últimos Artículos')) {
          articlesSection = section;
          break;
        }
      }
      
      if (!articlesSection) {
        return;
      }
      
      const sectionRect = articlesSection.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      const currentScrollY = window.scrollY;
      const isScrollingUp = currentScrollY < lastScrollY.current;
      lastScrollY.current = currentScrollY;
      
      if (isScrollingUp) {
        const triggerPoint = windowHeight * 0.3;
        setIsVisible(sectionRect.top <= triggerPoint);
      } else {
        const triggerPoint = windowHeight * 0.7;
        setIsVisible(sectionRect.top <= triggerPoint);
      }
    };

    const throttledScroll = throttle(handleScroll, 100);
    window.addEventListener('scroll', throttledScroll, { passive: true });
    
    handleScroll();
    
    return () => {
      window.removeEventListener('scroll', throttledScroll);
    };
  }, [position, isHomePage, debug]);

  //avance automático
  useEffect(() => {
    if (!items.length || autoPlayMs <= 0) return;

    timerRef.current = setInterval(() => {
      setIndex((i) => (i + 1) % items.length);
    }, autoPlayMs);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [items, autoPlayMs, items.length]); // Added items.length to dependencies

  //tracking de impresiones: cada vez que cambia el slide activo
  useEffect(() => {
    const item = items[index];
    if (!item?.id) return;
    if (impressedOnceRef.current.has(item.id)) return;
    impressedOnceRef.current.add(item.id);
    trackImpression(item.id);
  }, [index, items]);

  //memoizar cálculo de dimensiones
  const calculateDimensions = useCallback((width, height, maxWidth = '100%') => {
    if (!width || !height) return { width: '100%', height: 'auto' };
    
    const aspectRatio = height / width;
    let maxW = maxWidth === '100%' ? '100%' : Math.min(Number(maxWidth), width);
    if (typeof maxW === 'number') {
      maxW = `${maxW}px`;
    }
    
    return {
      width: maxW,
      height: 'auto',
      aspectRatio: `${width}/${height}`,
      maxWidth: '100%',
      margin: '0 auto'
    };
  }, []);

  //contenido base con estilo
  const baseContainerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
    overflow: 'hidden',
    position: 'relative',
    padding: 0,
    margin: '5px auto',
    maxWidth: '100%',
    width: 'fit-content',
    boxSizing: 'content-box',
    height: 'auto'
  };

  //no mostrar en rutas de autenticacion
  const authRoutes = ['/login', '/register', '/auth', '/iniciar-sesion', '/registro'];
  const isAuthRoute = authRoutes.some(route => location.pathname.startsWith(route));
  
  //no renderizarizar en móvil, si fue cerrado o en rutas de autenticacion
  if ((position === 'left-fixed' || position === 'right-fixed') && 
      (window.innerWidth < 1024 || dismissed || isAuthRoute)) {
    return null;
  }
  
  //no mostrar banner inferior en móvil, si fue cerrado o en rutas de autenticacion
  if (position === 'bottom' && (window.innerWidth < 768 || dismissed || isAuthRoute)) {
    return null;
  }

  //estilos específicos de posición
  const positionStyles = {
    'top': {
      ...baseContainerStyle,
      display: 'flex',
      margin: '20px auto',
      padding: '0',
      maxWidth: '850px',
      width: '92%',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'transparent',
      boxShadow: 'none',
      borderRadius: '0',
      border: 'none',
      height: 'auto',
      aspectRatio: '16/9',
      overflow: 'visible',
    },
    'left-fixed': {
      ...baseContainerStyle,
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : 'auto',
      maxHeight: '450px',
      minHeight: 'auto',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      borderRadius: '6px',
      overflow: 'hidden',
      backgroundColor: '#fff',
      transition: 'all 0.3s ease'
    },
    'right-fixed': {
      ...baseContainerStyle,
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : 'auto',
      maxHeight: '450px',
      minHeight: 'auto',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      borderRadius: '6px',
      overflow: 'hidden',
      backgroundColor: '#fff',
      transition: 'all 0.3s ease'
    },
    'inline': {
      ...baseContainerStyle,
      display: 'flex',
      margin: '5px auto',
      justifyContent: 'center',
      alignItems: 'center'
    },
    'bottom': {
      ...baseContainerStyle,
      display: 'flex',
      margin: '10px auto 20px',
      padding: '0',
      width: '100%',
      maxWidth: '1200px',
      height: '200px',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'transparent',
      boxShadow: 'none',
      borderRadius: '0',
      border: 'none',
      overflow: 'hidden',
    }
  };

  const containerStyle = {
    ...positionStyles[position] || positionStyles.inline,
    ...(position.includes('fixed') && {
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
    }),
    //validar
    aspectRatio: dims ? `${dims.w}/${dims.h}` : '16/9',
    minHeight: position === 'bottom' ? '200px' : (position === 'top' ? '200px' : '300px'),
    overflow: 'visible', // Cambiado a visible para que el efecto de neón no se recorte
    position: 'relative',
    backgroundColor: 'transparent', // Fondo transparente para el contenedor externo
    borderRadius: '12px',
    padding: '0', // Eliminamos el padding del contenedor externo
    zIndex: 1 // Aseguramos que esté por encima de otros elementos
  };

  //contenedor con estilo de tarjeta moderna
  const neonWrapperStyle = {
    display: 'block',
    borderRadius: '8px',
    padding: '0',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box',
    transition: 'all 0.2s ease',
    background: '#ffffff',
    position: 'relative',
    overflow: 'hidden',
    border: '1px solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)'
  };

  const imageStyle = {
    display: 'block',
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    objectPosition: 'center',
    padding: '0',
    margin: '0',
    borderRadius: '8px',
    backgroundColor: '#f9fafb',
    boxSizing: 'border-box',
    transition: 'transform 0.2s ease',
    ':hover': {
      transform: 'scale(1.02)'
    }
  };

  //estilo para el skeleton loader - debe mantener exactamente las mismas dimensiones que el contenido final
  const skeletonStyle = {
    ...containerStyle, // Aplicar primero los estilos del contenedor
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: '8px',
    overflow: 'hidden',
    //asegurar dimensiones específicas según posición
    ...(position === 'top' && {
      width: '100%',
      maxWidth: dims ? `${dims.w}px` : '1920px',
      height: dims ? `${dims.h}px` : '200px',
      aspectRatio: dims ? `${dims.w}/${dims.h}` : '1920/200'
    }),
    ...(position === 'bottom' && {
      width: '100%',
      maxWidth: '1200px',
      height: '200px',
      aspectRatio: '1200/200'
    }),
    ...(position === 'left-fixed' && {
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : '300px',
      maxHeight: '450px'
    }),
    ...(position === 'right-fixed' && {
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : '300px',
      maxHeight: '450px'
    }),
    ...(position === 'inline' && {
      width: '100%',
      height: dims ? `${dims.h}px` : '300px',
      aspectRatio: dims ? `${dims.w}/${dims.h}` : '16/9'
    })
  };

  //mientras carga - no renderizarizar nada para evitar diseño shift
  if (isLoading) {
    return null;
  }

  //en estado de error - no renderizarizar nada para evitar diseño shift
  if (error) {
    return null;
  }

  //no renderizarizar si no hay items
  if (items.length === 0) {
    return null;
  }

  //item actual para construir enlaces y manejadors
  const currentItem = items[index];

  //click manejador (debe estar antes de usarlo en el bloque bottom)
  const handleAdClick = async (e) => {
    if (!currentItem?.url_destino) {
      e.preventDefault();
      return;
    }
    try {
      e.preventDefault();
      const data = await trackClick(currentItem?.id);
      const dest = (data && data.redirect_url) ? data.redirect_url : currentItem?.url_destino;
      window.open(dest, '_blank', 'noopener,noreferrer');
    } catch (err) {
      window.open(currentItem?.url_destino, '_blank', 'noopener,noreferrer');
    }
  };

  


  

  //funcion para manejar los colores extraídos
  const handleColors = (colors) => {
    if (colors && colors.length > 0) {
      setDominantColor(colors[0]);
    }
  };

  //manejador para cargar el color dominante con efecto neón mejorado
  const handleImageLoad = (e) => {
    try {
      const img = e.target;
      
      if (img.complete) {
        //extraer el color dominante de la imagen
        const color = colorThief.current.getColor(img);
        
        //funcion para ajustar el brillo del color
        const adjustBrightness = (r, g, b, percent) => {
          const adjust = (value) => Math.min(255, Math.floor(value + (255 - value) * (percent / 100)));
          return {
            r: adjust(r),
            g: adjust(g),
            b: adjust(b)
          };
        };
        
        //ajustar el color para el efecto neón
        const neonColor = adjustBrightness(color[0], color[1], color[2], 40);
        const colorHex = `#${neonColor.r.toString(16).padStart(2, '0')}${neonColor.g.toString(16).padStart(2, '0')}${neonColor.b.toString(16).padStart(2, '0')}`;
        
        //actualizar el estado con el nuevo color dominante
        setDominantColor(colorHex);
        
        const wrapper = img.closest('.publicidad-wrapper');
        if (wrapper) {
          //crear y aplicar la animación de neón mejorada
          const style = document.createElement('style');
          style.id = 'neonGlowStyle';
          style.textContent = `
            @keyframes neonGlow {
              from {
                box-shadow: 
                  0 0 1px #fff,
                  0 0 2px #fff,
                  0 0 3px #fff,
                  0 0 4px ${colorHex},
                  0 0 7px ${colorHex},
                  0 0 8px ${colorHex},
                  0 0 10px ${colorHex},
                  0 0 15px ${colorHex};
                border-color: ${colorHex}99;
              }
              to {
                box-shadow: 
                  0 0 1px #fff,
                  0 0 3px #fff,
                  0 0 5px #fff,
                  0 0 10px ${colorHex},
                  0 0 15px ${colorHex},
                  0 0 20px ${colorHex},
                  0 0 25px ${colorHex};
                border-color: ${colorHex}cc;
              }
            }
          `;
          
          //limpiar estilos anteriores
          const existingStyle = document.getElementById('neonGlowStyle');
          if (existingStyle) {
            document.head.removeChild(existingStyle);
          }
          
          document.head.appendChild(style);
          
          //aplicar estilos directamente al wrapper
          wrapper.style.border = '1px solid #e5e7eb';
          wrapper.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)';
          wrapper.style.borderRadius = '8px';
          
          //forzar el repintado para asegurar que la animación se aplique
          wrapper.style.animation = 'none';
          wrapper.offsetHeight; // Trigger reflow
          wrapper.style.animation = 'neonGlow 2s ease-in-out infinite alternate';
        }
      }
    } catch (error) {
      console.error('Error al extraer el color:', error);
      //usar un color azul neón por defecto que combine mejor con el diseño
      setDominantColor('#00f7ff');
    }
  };

  //animation variants for image transitions
  const fadeVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        duration: 0.5,
        ease: 'easeInOut'
      }
    },
    exit: { 
      opacity: 0,
      transition: { 
        duration: 0.3,
        ease: 'easeInOut' 
      }
    }
  };

  //contenido para el carrusel
  const content = (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <div className="publicidad-wrapper" style={neonWrapperStyle}>
        <AnimatePresence mode='wait'>
          <motion.div
            key={currentItem?.id || 'default'}
            initial="hidden"
            animate="visible"
            exit="exit"
            variants={fadeVariants}
            style={{ width: '100%', height: '100%', position: 'relative' }}
          >
            <img
              src={currentItem?.media_url}
              alt={currentItem?.nombre || 'Publicidad'}
              style={imageStyle}
              crossOrigin="anonymous"
              onLoad={handleImageLoad}
            />
          </motion.div>
        </AnimatePresence>
        {items.length > 1 && (
          <div style={{
            position: 'absolute',
            bottom: '10px',
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: '5px',
            zIndex: 10
          }}>
            {items.map((_, i) => (
              <button
                key={i}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setIndex(i);
                }}
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  border: 'none',
                  padding: 0,
                  backgroundColor: i === index ? '#007bff' : 'rgba(0,0,0,0.2)',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  transform: i === index ? 'scale(1.3)' : 'scale(1)'
                }}
                aria-label={`Ir al slide ${i + 1}`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );

  //para paneles fijos (izquierda y derecha)
  if (position === 'left-fixed' || position === 'right-fixed') {
    const isArticlesPage = location.pathname.includes('/articulos');
    const isProgramacionPage = location.pathname.includes('/programacion');
    const isStaticContentPage = isArticlesPage || isProgramacionPage; // Páginas donde debe mostrarse igual que en artículos
    const shouldAnimate = isHomePage && !isStaticContentPage; // Solo animar en la página de inicio
    
    //estilo del panel
    const panelStyle = {
      position: 'fixed',
      [position === 'left-fixed' ? 'left' : 'right']: '16px',
      top: '30%', // Misma posición que en el home (30% desde arriba)
      zIndex: 1000,
      overflow: 'visible',
      pointerEvents: 'auto'
    };

    //en artículos y programación con animación de entrada
    if (isStaticContentPage) {
      return (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={panelStyle}
        >
          <div 
          className={`pub-carousel pos-${position} ${position === 'top' ? 'publicidad-container-top' : position === 'bottom' ? 'publicidad-container-bottom' : ''}`} 
          style={{
            ...containerStyle,
            position: 'relative',
            overflow: 'visible',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
          }} 
          title={currentItem?.ubicacion?.nombre || 'Publicidad'}
          >
            <button
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDismiss(); }}
              aria-label="Cerrar publicidad"
              title="Cerrar"
              style={{
                position: 'absolute',
                top: '6px',
                right: '6px',
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                border: 'none',
                background: 'rgba(0,0,0,0.6)',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 20
              }}
            >
              ×
            </button>
            <motion.a 
              href={currentItem?.url_destino || '#'} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ 
                display: 'block', 
                width: '100%',
                height: '100%',
                textDecoration: 'none',
                color: 'inherit'
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              onClick={handleAdClick}
            >
              {content}
            </motion.a>
          </div>
        </motion.div>
      );
    }
    
    //en home con animacion
    return (
      <motion.div
        initial="hidden"
        animate={isVisible ? "visible" : "hidden"}
        variants={panelVariants}
        custom={position}
        style={panelStyle}
      >
        <div 
          className={`pub-carousel pos-${position} ${position === 'top' ? 'publicidad-container-top' : position === 'bottom' ? 'publicidad-container-bottom' : ''}`} 
          style={{
            ...containerStyle,
            overflow: 'visible'
          }}
          title={currentItem?.ubicacion?.nombre || 'Publicidad'}
        >
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDismiss(); }}
            aria-label="Cerrar publicidad"
            title="Cerrar"
            style={{ 
              position: 'absolute',
              top: '6px',
              right: '6px',
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              border: 'none',
              background: 'rgba(0,0,0,0.6)',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 20
            }}
          >
            ×
          </button>
          <a 
            href={currentItem?.url_destino || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ 
              display: 'block', 
              width: '100%', 
              height: '100%',
              textDecoration: 'none',
              color: 'inherit'
            }}
            onClick={handleAdClick}
          >
            {content}
          </a>
        </div>
      </motion.div>
    );
  } else {
    //for bottom banner, add close button
    if (position === 'bottom') {
      return (
        <div 
          className="publicidad-banner-bottom"
          style={{
            overflow: 'visible',
            margin: '20px auto 40px',
            padding: '0'
          }}
          title={currentItem?.ubicacion?.nombre || 'Publicidad'}
        >
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDismiss(); }}
            aria-label="Cerrar publicidad"
            title="Cerrar"
            style={{
              position: 'absolute',
              top: '5px',
              right: '5px',
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              border: 'none',
              background: 'rgba(0,0,0,0.6)',
              color: '#fff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 20,
              fontSize: '16px',
              lineHeight: '1',
              padding: 0
            }}
          >
            ×
          </button>
          <a 
            href={currentItem?.url_destino || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ 
              display: 'block', 
              width: '100%', 
              height: '100%',
              textDecoration: 'none',
              color: 'inherit'
            }}
            onClick={handleAdClick}
          >
            {content}
          </a>
        </div>
      );
    }
    
    //default for other positions (inline, etc.)
    return (
      <div 
        className={`pub-carousel pos-${position} ${position === 'top' ? 'publicidad-container-top' : position === 'bottom' ? 'publicidad-container-bottom' : ''}`} 
        style={containerStyle}
        title={currentItem?.ubicacion?.nombre || 'Publicidad'}
      >
        <a 
          href={currentItem?.url_destino || '#'} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{ 
            display: 'block', 
            width: '100%', 
            height: '100%',
            textDecoration: 'none',
            color: 'inherit'
          }}
          onClick={handleAdClick}
        >
          {content}
        </a>
      </div>
    );
  }
}
