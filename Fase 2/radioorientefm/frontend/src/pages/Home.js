import React, { useState, useEffect, useRef, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Radio, Users, Music, Newspaper, Calendar, User, Tag, ArrowRight } from "lucide-react";
import axios from "axios";
import "./Home.css";
import PublicidadCarousel from "../components/PublicidadCarousel";
import CarruselLocutores from '../components/CarruselLocutores';
import Typewriter from '../components/Typewriter';

// Componente para contador animado
const CounterCard = ({ icon, endValue, suffix = "", label, duration = 2000 }) => {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const counterRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !hasAnimated) {
          setHasAnimated(true);

          const startTime = Date.now();
          const startValue = 0;

          const animate = () => {
            const now = Date.now();
            const progress = Math.min((now - startTime) / duration, 1);

            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);

            setCount(currentValue);

            if (progress < 1) {
              requestAnimationFrame(animate);
            } else {
              setCount(endValue);
            }
          };

          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.5 }
    );

    if (counterRef.current) {
      observer.observe(counterRef.current);
    }

    return () => {
      if (counterRef.current) {
        observer.unobserve(counterRef.current);
      }
    };
  }, [endValue, duration, hasAnimated]);

  return (
    <div className="stat-item" ref={counterRef}>
      {icon}
      <div className="stat-number">
        {count.toLocaleString()}{suffix}
      </div>
      <div className="stat-label">{label}</div>
    </div>
  );
};

const calculateYearsSince = (startDate) => {
  const now = new Date();
  const start = new Date(startDate);

  let years = now.getFullYear() - start.getFullYear();
  const monthDiff = now.getMonth() - start.getMonth();
  const dayDiff = now.getDate() - start.getDate();

  if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
    years--;
  }

  return years;
};

const Home = () => {
  const navigate = useNavigate();
  const [featuredArticles, setFeaturedArticles] = useState([]);
  const [radioStation, setRadioStation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesResponse, stationResponse] = await Promise.all([
          axios.get("/api/articulos/api/articulos/"),
          axios.get("/api/radio/station/"),
        ]);

        const articles = articlesResponse.data.results || articlesResponse.data || [];
        const publishedArticles = articles.filter(article => article.publicado);

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const todayArticles = publishedArticles.filter(article => {
          const articleDate = new Date(article.fecha_publicacion || article.fecha_creacion);
          articleDate.setHours(0, 0, 0, 0);
          return articleDate.getTime() === today.getTime();
        });

        let articlesToShow;
        if (todayArticles.length >= 3) {
          articlesToShow = todayArticles.slice(0, 3);
        } else {
          articlesToShow = publishedArticles
            .sort((a, b) => {
              const dateA = new Date(a.fecha_publicacion || a.fecha_creacion);
              const dateB = new Date(b.fecha_publicacion || b.fecha_creacion);
              return dateB - dateA;
            })
            .slice(0, 3);
        }

        setFeaturedArticles(articlesToShow);
        setRadioStation(stationResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleArticleClick = (articleId) => {
    navigate('/articulos', { state: { selectedArticleId: articleId } });
  };


  const particleElements = useMemo(() => {
    const colors = [
      '#c62828',
      '#d32f2f',
      '#b71c1c',
      '#c62828',
      '#e53935'
    ];

    return [...Array(15)].map((_, i) => {
      const randomX = Math.random() * 100;
      const randomY = Math.random() * 100;
      const randomDelay = Math.random() * -40; // Delay negativo para que empiecen en diferentes puntos
      const randomDuration = 30 + Math.random() * 20; // 30-50 segundos (lento)
      const randomSize = 2 + Math.random() * 2; // 2-4px pequeñas
      const randomColor = colors[Math.floor(Math.random() * colors.length)];

      return (
        <div
          key={i}
          className="particle"
          style={{
            left: `${randomX}%`,
            top: `${randomY}%`,
            width: `${randomSize}px`,
            height: `${randomSize}px`,
            backgroundColor: randomColor,
            animationDelay: `${randomDelay}s`,
            animationDuration: `${randomDuration}s`,
            color: randomColor
          }}
        />
      );
    });
  }, []);

  return (
    <>
      <style>{`
        @keyframes radio-pulse {
          0% {
            transform: scale(0.8);
            opacity: 1;
          }
          100% {
            transform: scale(2.8);
            opacity: 0;
          }
        }

        @keyframes pulse-cursor {
          0% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.3;
            transform: scale(0.8);
          }
          100% {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>

      <div className="home-page">
        {/* Hero Section */}
        <section className="hero">
          {/* Partículas animadas */}
          <div className="floating-particles">
            {particleElements}
          </div>
          <div className="container">
            <div className="hero-content">
              <div className="hero-text">
                <h1 className="hero-title">
                  Bienvenidos a
                </h1>
                <h1 className="hero-title">
                  <Typewriter />
                </h1>

                <p className="hero-description">
                  La mejor música, noticias y entretenimiento de la Zona oriente
                  de santiago. Conectando comunidades a través de las ondas
                  radiales.
                </p>
                <div className="hero-buttons">
                  <Link to="/programacion" className="btn btn-primary">
                    Ver Programación
                  </Link>
                  <Link to="/contacto" className="btn btn-outline">
                    Contáctanos
                  </Link>
                </div>
              </div>
              <div className="hero-image">
                <div className="radio-graphic">
                  <img
                    src="/images/radiooriente.png"
                    alt="Radio Oriente FM"
                    className="hero-logo"
                  />
                  <div className="radio-waves">
                    <div className="wave wave-1" style={{
                      animation: 'radio-pulse 3s ease-out 0s infinite'
                    }}></div>
                    <div className="wave wave-2" style={{
                      animation: 'radio-pulse 3s ease-out 1s infinite'
                    }}></div>
                    <div className="wave wave-3" style={{
                      animation: 'radio-pulse 3s ease-out 2s infinite'
                    }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Secciones */}
        <section className="stats">
          <div className="container">
            <div className="stats-grid">
              <CounterCard
                icon={<Users className="stat-icon" />}
                endValue={parseInt((radioStation?.listeners_count || "1000").toString().replace(/,/g, '').replace(/\+/g, ''))}
                suffix="+"
                label="Oyentes Activos"
                duration={2000}
              />
              <div className="stat-item">
                <Music className="stat-icon" />
                <div className="stat-number">24/7</div>
                <div className="stat-label">Música en Vivo</div>
              </div>
              <div className="stat-item">
                <Newspaper className="stat-icon" />
                <div className="stat-number">Noticias</div>
                <div className="stat-label">Diarias</div>
              </div>
              <CounterCard
                icon={<Radio className="stat-icon" />}
                endValue={calculateYearsSince(new Date(2011, 8, 21))}
                label="Años al Aire"
                duration={2000}
              />
            </div>
          </div>
        </section>

        <CarruselLocutores />

        {/* Noticias */}
        <section className="featured-news">
          <div className="container">
            <h2 className="section-title">Últimos Artículos</h2>
            {loading ? (
              <div className="loading-container">
                <div className="spinner"></div>
                <p>Cargando artículos...</p>
              </div>
            ) : featuredArticles.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <Newspaper size={48} style={{ color: 'var(--color-gray-400)', marginBottom: '1rem' }} />
                <h3>No hay artículos disponibles</h3>
                <p>Pronto tendremos nuevas noticias para ti.</p>
              </div>
            ) : (
              <>
                <div className="news-grid">
                  {featuredArticles.map((article) => {
                    // Función para obtener thumbnail
                    const getThumbnail = (article) => {
                      return article.imagen_thumbnail || article.imagen_url || article.imagen_portada;
                    };

                    return (
                      <article
                        key={article.id}
                        className="news-card"
                        onClick={() => handleArticleClick(article.id)}
                        style={{ cursor: 'pointer' }}
                      >
                        {getThumbnail(article) && (
                          <img
                            src={getThumbnail(article)}
                            alt={article.titulo}
                            className="news-image"
                          />
                        )}
                        <div className="news-content">
                          <div className="meta-item" style={{ marginBottom: '1rem' }}>
                            <Tag size={14} />
                            <span>{article.categoria?.nombre || 'Sin categoría'}</span>
                          </div>
                          <h3 className="news-title">{article.titulo}</h3>
                          <p className="news-excerpt">
                            {article.resumen || article.contenido.substring(0, 120) + '...'}
                          </p>
                          <div className="news-meta">
                            <div className="meta-item">
                              <User size={14} />
                              <span>{article.autor_nombre || 'Radio Oriente'}</span>
                            </div>
                            <div className="meta-item">
                              <Calendar size={14} />
                              <span>
                                {new Date(article.fecha_publicacion || article.fecha_creacion).toLocaleDateString('es-ES', {
                                  year: 'numeric',
                                  month: 'long',
                                  day: 'numeric'
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>

                <div style={{ textAlign: 'center', marginTop: '3rem' }}>
                  <Link to="/articulos" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                    Ver más artículos
                    <ArrowRight size={20} />
                  </Link>
                </div>
              </>
            )}
          </div>
        </section>

        {/* Publicidad Home 1920x1080 debajo de Últimos Artículos */}
        <div className="container" style={{ margin: '24px auto' }}>
          <PublicidadCarousel dimensiones="1920x1080" position="top" autoPlayMs={8000} />
        </div>

        <section className="cards-section">
          <div className="card card-bandas">
            <div>
              <div className="icon mb-4">
                <Music className="icon-white" size={48} />
              </div>
              <h2 className="title mb-2 text-2xl font-bold">
                ¿Eres una banda o artista emergente?
              </h2>
              <p className="description mb-4 text-lg">
                ¡Queremos escucharte! Envía tu información y podrías aparecer en nuestra programación especial para artistas locales.
              </p>
            </div>
            <Link to="/emergente" className="btn-white mt-2">
              Postular Ahora
            </Link>
          </div>

          <div className="card card-noticias">
            <div>
              <div className="icon mb-4">
                <Newspaper className="icon-white" size={48} />
              </div>
              <h2 className="title mb-2 text-2xl font-bold">
                ¿Quieres estar al día?
              </h2>
              <p className="description mb-4 text-lg">
                Suscríbete a nuestro boletín y recibe las últimas noticias y actualizaciones directamente en tu correo.
              </p>
            </div>
            <Link to="/suscripcion" className="btn-white mt-2">
              Suscribirse ahora
            </Link>
          </div>

          <div className="card card-publicidad">
            <div>
              <div className="icon mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="icon-white">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="3" y1="9" x2="21" y2="9"></line>
                  <line x1="9" y1="21" x2="9" y2="9"></line>
                </svg>
              </div>
              <h2 className="title mb-2 text-2xl font-bold">
                Publicidad en Radio Oriente
              </h2>
              <p className="description mb-4 text-lg">
                Llega a miles de oyentes con nuestra publicidad radial. Paneles de publicidad personalizados para tu negocio o emprendimiento.
              </p>
            </div>
            <Link to="/publicidad" className="btn-white mt-2">
              Ver Oportunidades
            </Link>
          </div>
        </section>
      </div>
    </>
  );
};

export default Home;