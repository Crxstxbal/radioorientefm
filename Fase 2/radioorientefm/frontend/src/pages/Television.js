import React, { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';
import { Wifi } from 'lucide-react';
import './Pages.css';
import './Television.css';

//const hls_url = 'https://ntv1.akamaized.net/hls/live/2014075/nasa-ntv1-hd/master.m3u8'
const HLS_URL = 'https://ireplay.tv/test/blender.m3u8';

export default function Television() {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    //restaurar volumen guardado si existe
    try {
      const savedVolume = localStorage.getItem('tv_volume');
      if (savedVolume !== null) {
        const vol = parseFloat(savedVolume);
        if (!Number.isNaN(vol) && vol >= 0 && vol <= 1) {
          video.volume = vol;
        }
      }
    } catch (_) {}

    //bloquear la velocidad de reproduccion en 1x
    video.playbackRate = 1;

    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      //soporte nativo (safari / ios)
      try {
        video.src = HLS_URL;
        const p = video.play();
        if (p && typeof p.then === 'function') {
          p.catch(() => {});
        }
      } catch (e) {
        console.error('Error en reproducción nativa HLS:', e);
        setError('Error reproduciendo el stream.');
      }
      return;
    }

    if (!Hls.isSupported()) {
      console.error('HLS no soportado por este navegador.');
      setError('Tu navegador no soporta HLS.');
      return;
    }

    const hls = new Hls({
      //intentamos mantenernos cerca del "borde en vivo"
      liveSyncDuration: 2,
      liveMaxLatencyDuration: 10,
    });
    hlsRef.current = hls;

    console.log('Cargando stream HLS:', HLS_URL);
    hls.loadSource(HLS_URL);
    hls.attachMedia(video);

    hls.on(Hls.Events.ERROR, (event, data) => {
      console.error('HLS error:', data);
      if (data?.fatal) {
        setError('Error reproduciendo el stream.');
        try {
          hls.destroy();
        } catch (_) {}
        hlsRef.current = null;
      }
    });

    const handleTimeUpdate = () => {
      //en muchos streams en vivo con buffer dvr, si el usuario se queda muy atrás
      //lo acercamos de nuevo al final del buffer para que vaya casi en tiempo real
      const duration = video.duration;
      const currentTime = video.currentTime;

      if (!Number.isFinite(duration) || duration === 0) return;

      const diff = duration - currentTime;
      if (diff > 10) {
        //si está más de 10s atrasado, lo llevamos a ~2s del final
        video.currentTime = Math.max(duration - 2, 0);
      }
    };

    const handleVolumeChange = () => {
      try {
        localStorage.setItem('tv_volume', String(video.volume));
      } catch (_) {}
    };

    const handleRateChange = () => {
      if (video.playbackRate !== 1) {
        video.playbackRate = 1;
      }
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('volumechange', handleVolumeChange);
    video.addEventListener('ratechange', handleRateChange);

    return () => {
      try {
        video.removeEventListener('timeupdate', handleTimeUpdate);
        video.removeEventListener('volumechange', handleVolumeChange);
        video.removeEventListener('ratechange', handleRateChange);
        if (hlsRef.current) {
          hlsRef.current.destroy();
          hlsRef.current = null;
        }
        if (video) {
          video.pause();
          video.removeAttribute('src');
          video.load();
        }
      } catch (_) {}
    };
  }, []);

  return (
    <div className="live-page tv-page">
      <div className="container tv-container">
        <div className="page-header">
          <Wifi className="page-icon" style={{ color: 'var(--color-red)' }} />
          <div>
            <h1 className="page-title">Televisión en Vivo</h1>
            <p className="page-subtitle subtitle-primary">
              <strong>Señal audiovisual 24/7 de Radio Oriente FM</strong>
            </p>
            <p className="page-subtitle">
              Transmisión de video en tiempo real pensada para eventos y programación especial.
            </p>
          </div>
        </div>

        <div className="live-content">
          <div className="live-video-section">
            <div className="video-container-modern tv-player-card">
              <div className="video-wrapper-modern tv-player-wrapper">
                <video
                  ref={videoRef}
                  controls
                  autoPlay
                  playsInline
                  className="tv-video video-iframe-modern"
                />
                <div className="video-overlay">
                  <div className="video-controls-overlay">
                    <Wifi className="live-icon" size={24} />
                    <span className="overlay-text">Televisión en Vivo</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="stream-info-modern">
            <div className="stream-main-info">
              <div className="stream-title-section">
                <h2 className="stream-name">Canal TV Radio Oriente</h2>
                <p className="stream-description">
                  Espacio pensado para futuras transmisiones en video: conciertos, programas especiales,
                  entrevistas y contenido audiovisual exclusivo para la comunidad.
                </p>
              </div>
            </div>

            {error && (
              <div className="tv-error">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
