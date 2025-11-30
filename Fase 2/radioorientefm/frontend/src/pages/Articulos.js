import React, { useState, useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { BookOpen, Calendar, User, Eye, Tag, Filter, ArrowRight } from 'lucide-react';
import axios from 'axios';
import PaginacionFusion from '../components/PaginacionFusion';
import PublicidadCarousel from '../components/PublicidadCarousel';
import './Pages.css';

const Articles = () => {
  const location = useLocation();
  const { slug } = useParams(); // Capturar el slug de la URL
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Estados de paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(6); // Mostrar 6 artículos por página
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Construir params de paginación
        const params = {
          page: currentPage,
          page_size: pageSize
        };

        // Agregar filtro de categoría si está seleccionado
        let endpoint = '/api/articulos/api/articulos/';
        if (selectedCategory) {
          const category = categories.find(c => c.id === parseInt(selectedCategory));
          if (category) {
            endpoint = '/api/articulos/api/articulos/por_categoria/';
            params.categoria = category.slug;
          }
        }

        // Cargar artículos desde nueva API
        const articlesResponse = await axios.get(endpoint, { params });

        // Extraer datos de paginación
        const data = articlesResponse.data;
        if (data.results) {
          // Respuesta paginada
          setArticles(data.results);
          setTotalPages(data.total_pages || 1);
          setTotalItems(data.count || 0);
        } else {
          // Respuesta sin paginación (fallback)
          setArticles(data);
          setTotalPages(1);
          setTotalItems(data.length);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setArticles([]);
        setTotalPages(1);
        setTotalItems(0);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentPage, pageSize, selectedCategory]);

  // Cargar categorías (solo una vez)
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const categoriesResponse = await axios.get('/api/articulos/api/categorias/');
        setCategories(categoriesResponse.data.results || categoriesResponse.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setCategories([
          { id: 1, nombre: 'Noticias', slug: 'noticias' },
          { id: 2, nombre: 'Entrevistas', slug: 'entrevistas' },
          { id: 3, nombre: 'Música', slug: 'musica' },
          { id: 4, nombre: 'Eventos', slug: 'eventos' }
        ]);
      }
    };

    fetchCategories();
  }, []);

  // Abrir modal automáticamente si viene del Home
  useEffect(() => {
    if (location.state?.selectedArticleId && articles.length > 0) {
      const article = articles.find(a => a.id === location.state.selectedArticleId);
      if (article) {
        setSelectedArticle(article);
        // Limpiar el estado para evitar que se abra nuevamente
        window.history.replaceState({}, document.title);
      }
    }
  }, [location.state, articles]);

  // Cargar artículo si hay slug en la URL
  useEffect(() => {
    const loadArticleBySlug = async () => {
      if (slug) {
        try {
          const response = await axios.get(`/api/articulos/api/articulos/${slug}/`);
          setSelectedArticle(response.data);
        } catch (error) {
          console.error('Error loading article by slug:', error);
          // Si no se encuentra el artículo, no hacer nada (quedará en la lista)
        }
      }
    };

    loadArticleBySlug();
  }, [slug]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleArticleClick = async (article) => {
    // Hacer petición al backend para obtener el detalle (esto incrementa las vistas)
    try {
      const response = await axios.get(`/api/articulos/api/articulos/${article.slug}/`);
      setSelectedArticle(response.data);
    } catch (error) {
      console.error('Error loading article detail:', error);
      // Si falla, usar los datos que ya tenemos
      setSelectedArticle(article);
    }
  };

  const closeModal = () => {
    setSelectedArticle(null);
  };

  // Función auxiliar para obtener la imagen thumbnail (para tarjetas)
  const getArticleThumbnail = (article) => {
    // Priorizar thumbnail, luego imagen_url
    return article.imagen_thumbnail || article.imagen_url || article.imagen_portada;
  };

  // Función auxiliar para obtener la imagen banner (para modal)
  const getArticleBanner = (article) => {
    // Priorizar portada, luego imagen_url
    return article.imagen_portada || article.imagen_url;
  };

  // Filtrar artículos por búsqueda local (categoría se filtra en la API)
  const filteredArticles = articles.filter(article => {
    const matchesSearch = !searchTerm ||
      article.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (article.contenido && article.contenido.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  // Artículos destacados (mostrados aparte, sin paginación)
  const featuredArticles = filteredArticles.filter(article => article.destacado).slice(0, 3);
  
  // Artículos regulares con paginación
  const regularArticles = filteredArticles.filter(article => !article.destacado);
  
  // Calcular artículos a mostrar en la página actual
  const indexOfLastArticle = currentPage * pageSize;
  const indexOfFirstArticle = indexOfLastArticle - pageSize;
  const currentArticles = regularArticles.slice(0, pageSize); // Solo mostramos los artículos de la página actual
  
  // Mostrar mensaje de carga o sin resultados
  const showLoading = loading && articles.length === 0;
  const showNoResults = !loading && regularArticles.length === 0 && !searchTerm;
  const showNoSearchResults = !loading && regularArticles.length === 0 && searchTerm;

  // Handlers de paginación
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    // Scroll suave hacia arriba
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Resetear a página 1 cuando cambia la categoría
  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setCurrentPage(1);
  };

  return (
    <div className="news-page">
      <div className="container">
        <div className="page-header">
          <BookOpen className="page-icon" />
          <div>
            <h1 className="page-title">Artículos</h1>
            <p className="page-subtitle">
              Noticias, entrevistas, artículos y contenido especial de Radio Oriente FM
            </p>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="container">
          <div className="filters-section" style={{display: 'flex', gap: '2rem', marginBottom: '2rem', alignItems: 'center', flexWrap: 'wrap'}}>
            <div className="search-filter" style={{flex: '1', minWidth: '300px'}}>
              <input
                type="text"
                placeholder="Buscar artículos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input"
                style={{width: '100%'}}
              />
            </div>
            
            <div className="category-filter" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Filter size={20} />
              <select
                value={selectedCategory}
                onChange={handleCategoryChange}
                className="form-select"
              >
                <option value="">Todas las categorías</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Cargando artículos...</p>
            </div>
          ) : (
            <>
              {/* Artículos destacados */}
              {featuredArticles.length > 0 && (
                <section className="featured-section">
                  <h2 className="section-title">Artículos Destacados</h2>
                  <div className="featured-news-grid">
                    {featuredArticles.map(article => (
                      <article 
                        key={article.id} 
                        className="featured-news-card"
                        onClick={() => handleArticleClick(article)}
                      >
                        {getArticleThumbnail(article) && (
                          <img src={getArticleThumbnail(article)} alt={article.titulo} className="featured-news-image" />
                        )}
                        <div className="featured-news-content">
                          <div className="meta-item" style={{marginBottom: '1rem'}}>
                            <Tag size={14} />
                            <span>{article.categoria?.nombre || 'Sin categoría'}</span>
                          </div>
                          <h3 className="featured-news-title">{article.titulo}</h3>
                          <p className="featured-news-excerpt">
                            {article.resumen || article.contenido.substring(0, 150) + '...'}
                          </p>
                          <div className="news-meta">
                            <div className="meta-item">
                              <User size={14} />
                              <span>{article.autor_nombre || 'Radio Oriente'}</span>
                            </div>
                            <div className="meta-item">
                              <Calendar size={14} />
                              <span>{formatDate(article.fecha_publicacion || article.fecha_creacion)}</span>
                            </div>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}

              {/* Lista de artículos */}
              <section className="all-news-section">
                <h2 className="section-title">
                  {selectedCategory ? 
                    `${categories.find(c => c.id === parseInt(selectedCategory))?.nombre || 'Artículos'}` : 
                    'Todos los Artículos'
                  }
                </h2>
                
                <div className="articles-content">
                  {showLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <p>Cargando artículos...</p>
                    </div>
                  ) : showNoResults ? (
                    <div className="no-programs" style={{textAlign: 'center', padding: '3rem'}}>
                      <BookOpen size={48} style={{color: 'var(--color-gray-400)', marginBottom: '1rem'}} />
                      <h3>No hay artículos disponibles</h3>
                      <p>No se encontraron artículos en esta categoría.</p>
                    </div>
                  ) : showNoSearchResults ? (
                    <div className="no-programs" style={{textAlign: 'center', padding: '3rem'}}>
                      <BookOpen size={48} style={{color: 'var(--color-gray-400)', marginBottom: '1rem'}} />
                      <h3>No se encontraron resultados</h3>
                      <p>No hay artículos que coincidan con tu búsqueda: "{searchTerm}"</p>
                    </div>
                  ) : (
                    <div className="news-grid">
                      {currentArticles.map(article => (
                      <article 
                        key={article.id} 
                        className="news-card"
                        onClick={() => handleArticleClick(article)}
                      >
                        {getArticleThumbnail(article) && (
                          <img src={getArticleThumbnail(article)} alt={article.titulo} className="news-image" />
                        )}
                        <div className="news-content">
                          <div className="meta-item" style={{marginBottom: '1rem'}}>
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
                              <span>{formatDate(article.fecha_publicacion || article.fecha_creacion)}</span>
                            </div>
                          </div>
                          <div className="read-more-container">
                            <button className="read-more-btn">
                              <span>Leer más</span>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M5 12h14M12 5l7 7-7 7"></path>
                              </svg>
                            </button>
                          </div>
                        </div>
                      </article>
                      ))}
                    </div>
                  )}
                </div>

                {/* Paginación */}
                {totalPages > 0 && (
                  <PaginacionFusion
                    currentPage={currentPage}
                    totalPages={totalPages}
                    totalItems={totalItems}
                    itemsPerPage={pageSize}
                    onPageChange={handlePageChange}
                  />
                )}
              </section>
            </>
          )}
        </div>

        {/* Modal para artículo seleccionado */}
        {selectedArticle && (
          <div className="news-modal-overlay" onClick={closeModal}>
            <div className="news-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={closeModal}>×</button>
              
              {getArticleBanner(selectedArticle) && (
                <img src={getArticleBanner(selectedArticle)} alt={selectedArticle.titulo} className="modal-image" />
              )}
              
              <div className="modal-content">
                <div className="meta-item" style={{marginBottom: '1rem'}}>
                  <Tag size={16} />
                  <span>{selectedArticle.categoria?.nombre || 'Sin categoría'}</span>
                </div>
                
                <h1 className="modal-title">{selectedArticle.titulo}</h1>
                
                <div className="modal-meta">
                  <div className="meta-item">
                    <User size={16} />
                    <span>{selectedArticle.autor_nombre || 'Radio Oriente'}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{formatDate(selectedArticle.fecha_publicacion || selectedArticle.fecha_creacion)}</span>
                  </div>
                </div>
                
                {selectedArticle.resumen && (
                  <div style={{marginBottom: '2rem', padding: '1rem', backgroundColor: 'var(--color-gray-50)', borderRadius: '0.5rem'}}>
                    <p><strong>{selectedArticle.resumen}</strong></p>
                  </div>
                )}
                
                <div style={{display: 'flex', gap: '2rem', flexWrap: 'wrap', alignItems: 'flex-start'}}>
                  {/* Imagen thumbnail cuadrada */}
                  {getArticleThumbnail(selectedArticle) && (
                    <div style={{flex: '0 0 300px', maxWidth: '300px'}}>
                      <img 
                        src={getArticleThumbnail(selectedArticle)} 
                        alt={selectedArticle.titulo}
                        style={{
                          width: '100%',
                          aspectRatio: '1/1',
                          objectFit: 'cover',
                          borderRadius: '0.5rem',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                        }}
                      />
                      <p style={{
                        marginTop: '0.5rem',
                        fontSize: '0.875rem',
                        color: 'var(--color-gray-500)',
                        textAlign: 'center'
                      }}>
                        {selectedArticle.categoria?.nombre || 'Artículo'}
                      </p>
                    </div>
                  )}
                  
                  {/* Contenido del artículo */}
                  <div className="modal-text" style={{flex: '1', minWidth: '300px'}}>
                    <div dangerouslySetInnerHTML={{ __html: selectedArticle.contenido }} />
                  </div>
                </div>
                
                {/* Video embebido si existe */}
                {selectedArticle.video_url && (
                  <div style={{marginTop: '2rem'}}>
                    <h3 style={{marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600'}}>Video relacionado</h3>
                    <div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden'}}>
                      <iframe
                        src={selectedArticle.video_url.includes('youtube.com') || selectedArticle.video_url.includes('youtu.be') 
                          ? selectedArticle.video_url.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
                          : selectedArticle.video_url}
                        style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none', borderRadius: '0.5rem'}}
                        allowFullScreen
                        title="Video del artículo"
                      />
                    </div>
                  </div>
                )}
                
                {/* Archivo adjunto si existe */}
                {selectedArticle.archivo_adjunto && (
                  <div style={{marginTop: '2rem', padding: '1rem', backgroundColor: 'var(--color-gray-50)', borderRadius: '0.5rem'}}>
                    <h3 style={{marginBottom: '0.5rem', fontSize: '1.125rem', fontWeight: '600'}}>📎 Archivo adjunto</h3>
                    <a 
                      href={selectedArticle.archivo_adjunto}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{color: 'var(--color-red)', textDecoration: 'underline', display: 'inline-flex', alignItems: 'center', gap: '0.5rem'}}
                    >
                      <span>Descargar archivo</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Articles;
