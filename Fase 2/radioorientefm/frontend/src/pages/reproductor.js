import React, { useContext, useEffect, useState, useRef } from "react";
import { Play, Pause, Volume2, VolumeX, ArrowLeft } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { AudioContextGlobal } from "../contexts/AudioContext";
import FondoParticulas from "../components/fondoparticulas";

import './reproductor.css';

const Reproductor = () => {
  const { isPlaying, togglePlay, volume, setVolume, toggleMute, streamUrl } = useContext(AudioContextGlobal);
  const navigate = useNavigate();
  const location = useLocation();
  
  const [isMuted, setIsMuted] = useState(volume === 0);
  const [currentTime, setCurrentTime] = useState(
    new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  
  const playButtonRef = useRef(null);
  const logoRef = useRef(null);
  const volumeButtonRef = useRef(null);
  const sliderRef = useRef(null);
  const contentRef = useRef(null);
  const backButtonRef = useRef(null);
  
  //obtener la página anterior desde el estado o usar '/' como default
  const previousPage = location.state?.from || '/';

  useEffect(() => setIsMuted(volume === 0), [volume]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    //animación de entrada suave
    if (contentRef.current) {
      contentRef.current.style.opacity = '0';
      contentRef.current.style.transform = 'translateY(30px) scale(0.95)';
      
      setTimeout(() => {
        contentRef.current.style.transition = 'all 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
        contentRef.current.style.opacity = '1';
        contentRef.current.style.transform = 'translateY(0) scale(1)';
      }, 150);
    }
  }, []);

  const handlePlayClick = () => {
    //efecto de pulso avanzado
    if (playButtonRef.current) {
      playButtonRef.current.style.transform = 'scale(0.9)';
      playButtonRef.current.style.transition = 'transform 0.1s ease';
      
      setTimeout(() => {
        playButtonRef.current.style.transform = 'scale(1.15) rotate(-8deg)';
        playButtonRef.current.style.transition = 'transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
        
        setTimeout(() => {
          playButtonRef.current.style.transform = 'scale(1) rotate(0deg)';
          playButtonRef.current.style.transition = 'transform 0.3s ease';
        }, 400);
      }, 100);
    }
    
    togglePlay();
  };

  const handleVolumeClick = () => {
    toggleMute();
    
    //efecto de rotación más simple después del toggle
    if (volumeButtonRef.current) {
      setTimeout(() => {
        volumeButtonRef.current.style.transform = 'rotate(180deg) scale(1.2)';
        volumeButtonRef.current.style.transition = 'transform 0.4s ease';
        
        setTimeout(() => {
          volumeButtonRef.current.style.transform = 'rotate(0deg) scale(1)';
        }, 400);
      }, 50);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = Number(e.target.value);
    
    //cambiar volumen sin efectos que puedan interferir
    setVolume(newVolume);
    
    //efectos visuales más simples y seguros
    if (sliderRef.current) {
      sliderRef.current.style.setProperty('--progress', `${newVolume * 100}%`);
    }
  };

  const handleLogoHover = () => {
    if (logoRef.current) {
      logoRef.current.style.transform = 'scale(1.08) rotate(3deg)';
      logoRef.current.style.filter = 'brightness(1.1) saturate(1.2)';
      logoRef.current.style.boxShadow = '0 25px 50px rgba(0,0,0,0.8), 0 0 30px rgba(220, 38, 38, 0.4)';
    }
  };

  const handleLogoLeave = () => {
    if (logoRef.current) {
      logoRef.current.style.transform = 'scale(1) rotate(0deg)';
      logoRef.current.style.filter = 'brightness(1) saturate(1)';
      logoRef.current.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.6)';
    }
  };

  const handleGoBack = () => {
    //animación del botón
    if (backButtonRef.current) {
      backButtonRef.current.style.transform = 'scale(0.9) translateX(-5px)';
      backButtonRef.current.style.transition = 'transform 0.2s ease';
      
      setTimeout(() => {
        backButtonRef.current.style.transform = 'scale(1) translateX(0)';
      }, 200);
    }
    
    //navegar a la página anterior
    setTimeout(() => {
      navigate(previousPage);
    }, 300);
  };

  //si streamurl no es string, muestra "cargando..."
  const streamStatus = typeof streamUrl === "string" && streamUrl.length > 0 ? "En vivo" : "Cargando stream...";

  return (
    <div className="reproductor-page">
      <FondoParticulas />

      {/*botón de volver*/}
      <button 
        ref={backButtonRef}
        onClick={handleGoBack}
        className="btn-back"
        title="Volver"
      >
        <ArrowLeft size={24} />
        <span>Volver</span>
      </button>

      <div className="reproductor-content" ref={contentRef}>
        <img 
          ref={logoRef}
          src="/images/logo.png" 
          alt="Radio Oriente" 
          className="reproductor-logo"
          onMouseEnter={handleLogoHover}
          onMouseLeave={handleLogoLeave}
        />

        <div className="reproductor-controls">
          <button 
            ref={playButtonRef}
            onClick={handlePlayClick} 
            className="btn-play"
          >
            {isPlaying ? <Pause size={50} /> : <Play size={50} />}
          </button>
        </div>

        <div className="reproductor-volume">
          <button 
            ref={volumeButtonRef}
            onClick={handleVolumeClick} 
            className="btn-volume"
          >
            {isMuted ? <VolumeX size={30} /> : <Volume2 size={30} />}
          </button>
          <input
            ref={sliderRef}
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            style={{'--progress': `${volume * 100}%`}}
          />
        </div>

        <span className="reproductor-time">{currentTime}</span>
        <span className="reproductor-status">{streamStatus}</span>
      </div>
    </div>
  );
};

export default Reproductor;