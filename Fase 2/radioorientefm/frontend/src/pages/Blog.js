import React, { useState, useEffect } from 'react';
import { BookOpen, Calendar, User, MessageCircle, Eye } from 'lucide-react';
import api from '../utils/api';
import './Pages.css';

const Blog = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await api.get('/api/blog/posts/');
        setPosts(response.data.results || response.data);
      } catch (error) {
        console.error('Error fetching blog posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handlePostClick = (post) => {
    setSelectedPost(post);
  };

  const closeModal = () => {
    setSelectedPost(null);
  };

  return (
    <div className="blog-page">
      <div className="container">
        <div className="page-header">
          <BookOpen className="page-icon" />
          <div>
            <h1 className="page-title">Blog</h1>
            <p className="page-subtitle">
              Artículos, reflexiones y contenido especial de Radio Oriente FM
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando artículos...</p>
          </div>
        ) : (
          <div className="blog-container">
            {/*featured posts*/}
            {posts.filter(post => post.is_featured).length > 0 && (
              <section className="featured-section">
                <h2 className="section-title">Artículos Destacados</h2>
                <div className="featured-posts-grid">
                  {posts.filter(post => post.is_featured).slice(0, 2).map((post) => (
                    <article 
                      key={post.id} 
                      className="featured-post-card"
                      onClick={() => handlePostClick(post)}
                    >
                      {post.featured_image && (
                        <img 
                          src={post.featured_image} 
                          alt={post.title}
                          className="featured-post-image"
                        />
                      )}
                      <div className="featured-post-content">
                        <h3 className="featured-post-title">{post.title}</h3>
                        <p className="featured-post-excerpt">
                          {post.excerpt || post.content.substring(0, 200)}...
                        </p>
                        <div className="post-meta">
                          <div className="meta-item">
                            <User size={16} />
                            <span>{post.author_name}</span>
                          </div>
                          <div className="meta-item">
                            <Calendar size={16} />
                            <span>{formatDate(post.created_at)}</span>
                          </div>
                          <div className="meta-item">
                            <MessageCircle size={16} />
                            <span>{post.comments_count || 0} comentarios</span>
                          </div>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            )}

            {/*all posts*/}
            <section className="all-posts-section">
              <h2 className="section-title">Todos los Artículos</h2>
              <div className="posts-grid">
                {posts.map((post) => (
                  <article 
                    key={post.id} 
                    className="post-card"
                    onClick={() => handlePostClick(post)}
                  >
                    {post.featured_image && (
                      <img 
                        src={post.featured_image} 
                        alt={post.title}
                        className="post-image"
                      />
                    )}
                    <div className="post-content">
                      <h3 className="post-title">{post.title}</h3>
                      <p className="post-excerpt">
                        {post.excerpt || post.content.substring(0, 120)}...
                      </p>
                      <div className="post-meta">
                        <div className="meta-item">
                          <User size={14} />
                          <span>{post.author_name}</span>
                        </div>
                        <div className="meta-item">
                          <Calendar size={14} />
                          <span>{formatDate(post.created_at)}</span>
                        </div>
                        <div className="meta-item">
                          <MessageCircle size={14} />
                          <span>{post.comments_count || 0}</span>
                        </div>
                      </div>
                      <button className="read-more-btn">
                        <Eye size={16} />
                        Leer artículo
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </div>
        )}

        {/*post modal*/}
        {selectedPost && (
          <div className="post-modal-overlay" onClick={closeModal}>
            <div className="post-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={closeModal}>×</button>
              {selectedPost.featured_image && (
                <img 
                  src={selectedPost.featured_image} 
                  alt={selectedPost.title}
                  className="modal-image"
                />
              )}
              <div className="modal-content">
                <h2 className="modal-title">{selectedPost.title}</h2>
                <div className="modal-meta">
                  <div className="meta-item">
                    <User size={16} />
                    <span>{selectedPost.author_name}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{formatDate(selectedPost.created_at)}</span>
                  </div>
                  <div className="meta-item">
                    <MessageCircle size={16} />
                    <span>{selectedPost.comments_count || 0} comentarios</span>
                  </div>
                </div>
                <div className="modal-text">
                  {selectedPost.content.split('\n').map((paragraph, index) => (
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

export default Blog;