import React, { useState, useEffect } from 'react';
import { Newspaper, Calendar, User, Eye } from 'lucide-react';
import api from '../utils/api';
import './Pages.css';

const News = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNews, setSelectedNews] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await api.get('/api/radio/news/');
        setNews(response.data.results || response.data);
      } catch (error) {
        console.error('Error fetching news:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleNewsClick = (newsItem) => {
    setSelectedNews(newsItem);
  };

  const closeModal = () => {
    setSelectedNews(null);
  };

  return (
    <div className="news-page">
      <div className="container">
        <div className="page-header">
          <Newspaper className="page-icon" />
          <div>
            <h1 className="page-title">Noticias</h1>
            <p className="page-subtitle">
              Mantente informado con las últimas noticias de la región oriental
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando noticias...</p>
          </div>
        ) : (
          <div className="news-container">
            {/*featured news*/}
            {news.filter(item => item.is_featured).length > 0 && (
              <section className="featured-section">
                <h2 className="section-title">Noticias Destacadas</h2>
                <div className="featured-news-grid">
                  {news.filter(item => item.is_featured).slice(0, 2).map((newsItem) => (
                    <article 
                      key={newsItem.id} 
                      className="featured-news-card"
                      onClick={() => handleNewsClick(newsItem)}
                    >
                      {newsItem.image && (
                        <img 
                          src={newsItem.image} 
                          alt={newsItem.title}
                          className="featured-news-image"
                        />
                      )}
                      <div className="featured-news-content">
                        <h3 className="featured-news-title">{newsItem.title}</h3>
                        <p className="featured-news-excerpt">
                          {newsItem.content.substring(0, 200)}...
                        </p>
                        <div className="news-meta">
                          <div className="meta-item">
                            <User size={16} />
                            <span>{newsItem.author_name}</span>
                          </div>
                          <div className="meta-item">
                            <Calendar size={16} />
                            <span>{formatDate(newsItem.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            )}

            {/*all news*/}
            <section className="all-news-section">
              <h2 className="section-title">Todas las Noticias</h2>
              <div className="news-grid">
                {news.map((newsItem) => (
                  <article 
                    key={newsItem.id} 
                    className="news-card"
                    onClick={() => handleNewsClick(newsItem)}
                  >
                    {newsItem.image && (
                      <img 
                        src={newsItem.image} 
                        alt={newsItem.title}
                        className="news-image"
                      />
                    )}
                    <div className="news-content">
                      <h3 className="news-title">{newsItem.title}</h3>
                      <p className="news-excerpt">
                        {newsItem.content.substring(0, 120)}...
                      </p>
                      <div className="news-meta">
                        <div className="meta-item">
                          <User size={14} />
                          <span>{newsItem.author_name}</span>
                        </div>
                        <div className="meta-item">
                          <Calendar size={14} />
                          <span>{formatDate(newsItem.created_at)}</span>
                        </div>
                      </div>
                      <button className="read-more-btn">
                        <Eye size={16} />
                        Leer más
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        )}

        {/*news modal*/}
        {selectedNews && (
          <div className="news-modal-overlay" onClick={closeModal}>
            <div className="news-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={closeModal}>×</button>
              {selectedNews.image && (
                <img 
                  src={selectedNews.image} 
                  alt={selectedNews.title}
                  className="modal-image"
                />
              )}
              <div className="modal-content">
                <h2 className="modal-title">{selectedNews.title}</h2>
                <div className="modal-meta">
                  <div className="meta-item">
                    <User size={16} />
                    <span>{selectedNews.author_name}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{formatDate(selectedNews.created_at)}</span>
                  </div>
                </div>
                <div className="modal-text">
                  {selectedNews.content.split('\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default News;
