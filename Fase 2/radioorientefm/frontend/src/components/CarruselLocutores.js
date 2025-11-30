// frontend/src/components/CarruselLocutores.jsx

import React, { useState, useEffect } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import axios from 'axios'; // <-- 1. Importamos axios

// Importa los estilos de Swiper
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

import './CarruselLocutores.css'; 

const API_URL = '/api/radio/locutores/activos/';

const CarruselLocutores = () => {
  // El estado inicial DEBE ser un array vacío
  const [locutores, setLocutores] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLocutores = async () => {
      try {
        console.log('Fetching locutores from:', API_URL);
        const response = await axios.get(API_URL);
        const data = response.data;
        console.log('API Response:', data);

        // ---- ESTA ES LA SOLUCIÓN MEJORADA ----
        let locutoresData = [];
        
        if (data && Array.isArray(data.results)) {
          // 1. Si es una respuesta paginada, usamos .results
          locutoresData = data.results;
        } else if (data && Array.isArray(data)) {
          // 2. Si es una respuesta de array simple, la usamos
          locutoresData = data;
        } else {
          // 3. Si es cualquier otra cosa (null, objeto, etc.), dejamos un array vacío
          console.error("La API no devolvió un array de locutores:", data);
        }

        // Log de depuración para las URLs de las imágenes
        console.log('Locutores con sus fotos:', locutoresData.map(l => ({
          id: l.id,
          nombre: l.nombre,
          foto_url: l.foto_url,
          foto_completa: l.foto_url ? new URL(l.foto_url, window.location.origin).href : 'No tiene foto'
        })));

        setLocutores(locutoresData);
        // -------------------------------------

      } catch (error) {
        console.error("Error al cargar locutores:", error);
        // 4. Si la API falla (404, 500), también dejamos un array vacío
        setLocutores([]); // <-- Garantiza que sea un array
      } finally {
        setLoading(false);
      }
    };

    fetchLocutores();
  }, []); // Array de dependencias vacío, se ejecuta 1 vez

  if (loading) {
    return (
      <div className="locutores-carrusel-container">
        <h2>Nuestros Locutores</h2>
        <div style={{ textAlign: 'center', padding: '20px', color: '#fff' }}>
          Cargando locutores...
        </div>
      </div>
    );
  }

  // Si no hay locutores, mostramos un mensaje
  if (locutores.length === 0) {
    return (
      <div className="locutores-carrusel-container">
        <h2>Nuestros Locutores</h2>
        <div style={{ textAlign: 'center', padding: '20px', color: '#fff' }}>
          No hay locutores disponibles en este momento.
        </div>
      </div>
    );
  }

  return (
    <div className="locutores-carrusel-container">
      <div className="title-container">
        <h2>Nuestros Locutores</h2>
      </div>
      <Swiper
        modules={[Navigation, Pagination, Autoplay]}
        spaceBetween={30}
        slidesPerView={1}
        navigation={true}
        pagination={{ clickable: true }}
        loop={true}
        autoplay={{
          delay: 4000,
          disableOnInteraction: false,
          pauseOnMouseEnter: false,
        }}
        speed={1200}
        grabCursor={true}
        breakpoints={{
          320: { slidesPerView: 1, spaceBetween: 10 },
          768: { slidesPerView: 2, spaceBetween: 20 },
          1024: { slidesPerView: 3, spaceBetween: 30 },
          1280: { slidesPerView: 4, spaceBetween: 30 },
        }}
      >
        {/* LÍNEA 74 (ahora): 
          'locutores' está GARANTIZADO que es un array, 
          por lo que .map() NUNCA fallará.
        */}
        {locutores.map(locutor => (
          <SwiperSlide key={locutor.id} className="locutor-slide">
            <div className="avatar-wrap">
              <div className="avatar-ring">
                <div className="avatar-inner">
                  <img
                    src={locutor.foto_url}
                    alt={`${locutor.nombre} ${locutor.apellido}`}
                    onError={(e) => {
                      console.error('Error al cargar la imagen:', locutor.foto_url);
                      e.target.style.display = 'none';
                      e.target.nextElementSibling.style.display = 'flex';
                    }}
                    style={{ display: locutor.foto_url ? 'block' : 'none' }}
                  />
                  <div className="placeholder-avatar" style={{ display: locutor.foto_url ? 'none' : 'flex' }}>
                    {locutor.nombre?.charAt(0)}{locutor.apellido?.charAt(0) || ''}
                  </div>
                </div>
                {/* Iconos flotantes de redes sociales */}
                <div className="social-icons">
                  <a href="#" className="social-icon social-icon-1" aria-label="Facebook">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </a>
                  <a href="#" className="social-icon social-icon-2" aria-label="Instagram">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </a>
                  <a href="#" className="social-icon social-icon-3" aria-label="X (Twitter)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  </a>
                  <a href="#" className="social-icon social-icon-4" aria-label="TikTok">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
            <h3 className="locutor-nombre">{locutor.apodo || `${locutor.nombre}`}</h3>
            <p className="locutor-rol">{locutor.nombre} {locutor.apellido}</p>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default CarruselLocutores;