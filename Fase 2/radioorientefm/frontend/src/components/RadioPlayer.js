import React, { useState, useEffect, useContext } from "react";
import { Play, Pause, Volume2, VolumeX, ChevronDown, ChevronUp, Maximize2 } from "lucide-react";
import { AudioContextGlobal } from "../contexts/AudioContext";
import { useNavigate, useLocation } from "react-router-dom";
import './RadioPlayer.css';

const RadioPlayer = () => {
  const { audioRef, isPlaying, togglePlay, volume, setVolume, toggleMute, streamUrl } = useContext(AudioContextGlobal);
  const navigate = useNavigate();
  const location = useLocation();

  const [lastVolume, setLastVolume] = useState(volume);
  const [isMuted, setIsMuted] = useState(volume === 0);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isExpanding, setIsExpanding] = useState(false);

  useEffect(() => {
    setIsMuted(volume === 0);
    if (volume > 0) setLastVolume(volume);
  }, [volume]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleVolumeChange = (e) => setVolume(Number(e.target.value));
  const handleToggleMute = () => setVolume(isMuted ? (lastVolume || 1) : 0);
  const toggleCollapse = () => {
    setIsCollapsed(prev => !prev);
    //esperar a que termine la animación y ajustar el widget
    setTimeout(() => {
      if (window.forceVapiPosition) {
        window.forceVapiPosition();
      }
    }, 350);
  };

  const handleExpand = () => {
    if (isExpanding) return;
    setIsExpanding(true);

    const playerElement = document.querySelector('.radio-player');
    const rect = playerElement.getBoundingClientRect();

    const expandOverlay = document.createElement('div');
    expandOverlay.className = 'expand-animation-overlay';
    document.body.appendChild(expandOverlay);

    //exactamente centrado horizontal y abajo
    expandOverlay.style.cssText = `
      position: fixed;
      left: 50%;
      top: 100%;
      transform: translateX(-50%);
      width: ${rect.width}px;
      height: ${rect.height}px;
      background: linear-gradient(135deg, #dc2626, #991b1b);
      z-index: 9999;
      transition: all 0.2s cubic-bezier(0.45, 0.46, 0.45, 0.94);
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
    `;

    //forzar repaint
    void expandOverlay.offsetHeight;

    //animación a pantalla completa
    setTimeout(() => {
      expandOverlay.style.cssText += `
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        transform: none;
        border-radius: 0;
        background: #c20606;
        background: radial-gradient(circle, rgba(139,0,0,1) 0%, rgba(0,0,0,1) 100%);
      `;
    }, 50);

    setTimeout(() => {
      navigate('/reproductor', { state: { from: location.pathname } });
      document.body.removeChild(expandOverlay);
      setIsExpanding(false);
    }, 600);
  };

  return (
    <div className={`radio-player-wrapper ${isCollapsed ? 'collapsed' : ''} ${isExpanding ? 'expanding' : ''}`}>
      <div className="collapse-btn-wrapper">
        <button 
          className="collapse-btn" 
          onClick={toggleCollapse}
          aria-label={isCollapsed ? "Mostrar reproductor" : "Ocultar reproductor"}
        >
          {isCollapsed ? <ChevronUp size={20}/> : <ChevronDown size={20}/> }
        </button>
      </div>

      <div className={`radio-player ${isPlaying ? 'playing' : 'paused'}`}>
        <div className="gradient-left" />
        <div className="gradient-right" />

        <div className="radio-info">
          <span
            className={`status-indicator ${isPlaying ? 'playing' : 'paused'}`}
            aria-label={isPlaying ? "En transmisión" : "No está transmitiendo"}
            title={isPlaying ? "On Air" : "Off Air"}
          />
          <div className="radio-details">
            <span className="radio-name">Radio Oriente FM</span>
            <span className="radio-frequency">107.1 FM - En vivo</span>
          </div>
        </div>     

        <div className="player-controls">
          <div className="control-buttons">
            <button
              onClick={togglePlay}
              aria-label="Play/Pause"
              className="control-icon play-pause-btn"
              disabled={!streamUrl}
            >
              {isPlaying ? <Pause size={20} /> : <Play size={20} />}
            </button>
            
            <button
              onClick={handleExpand}
              aria-label="Expandir reproductor"
              className="control-icon expand-btn"
              disabled={isExpanding}
            >
              <Maximize2 size={18} />
            </button>
          </div>
          <span className="text-sm mt-1 opacity-75">{currentTime}</span>
        </div>

        <div className="volume-controls">
          <button
            onClick={handleToggleMute}
            aria-label="Mute/Unmute"
            className="control-button"
          >
            {isMuted ? <VolumeX size={20} className="volume-icon" /> : <Volume2 size={20} className="volume-icon" />}
          </button>

          <div className="volume-slider-container">
            <div 
              className={`volume-progress ${isPlaying ? 'playing' : ''}`}
              style={{ width: `${volume * 100}%` }}
            />
            <div 
              className="volume-thumb"
              style={{ left: `calc(${volume * 100}% - 7px)` }}
            />
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={handleVolumeChange}
              className="volume-range"
              aria-label="Volume control"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RadioPlayer;
