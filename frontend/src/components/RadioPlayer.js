import React, { useRef, useState, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX, ChevronDown, ChevronUp } from "lucide-react";
import './RadioPlayer.css';

const RadioPlayer = () => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(() => {
    const saved = localStorage.getItem("radioVolume");
    return saved !== null ? Number(saved) : 1;
  });
  const [lastVolume, setLastVolume] = useState(volume);
  const [isMuted, setIsMuted] = useState(volume === 0);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [streamUrl, setStreamUrl] = useState(null);

  // Traer URL desde backend
  useEffect(() => {
    fetch("/api/radio/station/") // Endpoint que devuelve JSON con el stream_url
      .then(res => res.json())
      .then(data => {
        setStreamUrl(data.stream_url);
        if (!audioRef.current) {
          audioRef.current = new Audio(data.stream_url);
          audioRef.current.volume = volume;
        }
      })
      .catch(err => console.error("Error fetching stream URL:", err));
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
    setIsMuted(volume === 0);
    localStorage.setItem("radioVolume", volume);
  }, [volume]);

  useEffect(() => {
    const wasPlaying = sessionStorage.getItem("radioPlaying") === "true";
    if (wasPlaying && audioRef.current) {
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
    return () => {
      if (audioRef.current) {
        sessionStorage.setItem("radioPlaying", audioRef.current.paused ? "false" : "true");
      }
    };
  }, []);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
  };

  const handleVolumeChange = (e) => {
    const newVol = Number(e.target.value);
    setVolume(newVol);
    if (newVol > 0) setLastVolume(newVol);
  };

  const toggleMute = () => {
    if (isMuted) {
      setVolume(lastVolume || 1);
    } else {
      setLastVolume(volume);
      setVolume(0);
    }
  };

  const toggleCollapse = () => setIsCollapsed(prev => !prev);

  return (
    <div className={`radio-player-wrapper ${isCollapsed ? 'collapsed' : ''}`}>
      
      {/* Botón de colapso sobresaliendo */}
      <div className="collapse-btn-wrapper">
        <button 
          className="collapse-btn" 
          onClick={toggleCollapse}
          aria-label={isCollapsed ? "Mostrar reproductor" : "Ocultar reproductor"}
        >
          {isCollapsed ? <ChevronUp size={20}/> : <ChevronDown size={20}/>}
        </button>
      </div>

      {/* Reproductor principal */}
      <div className={`radio-player ${isPlaying ? 'playing' : 'paused'}`}>
        {/* Gradientes laterales */}
        <div className="gradient-left" />
        <div className="gradient-right" />

        {/* Información de radio */}
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

        {/* Controles centrales */}
        <div className="player-controls">
          <button
            onClick={togglePlay}
            aria-label="Play/Pause"
            className="control-icon"
            disabled={!streamUrl} // Desactiva botón si no hay URL
          >
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>
          <span className="text-sm mt-1 opacity-75">{currentTime}</span>
        </div>

        {/* Controles de volumen */}
        <div className="volume-controls">
          <button
            onClick={toggleMute}
            aria-label="Mute/Unmute"
            className="control-button"
          >
            {isMuted ? (
              <VolumeX size={20} className="volume-icon" />
            ) : (
              <Volume2 size={20} className="volume-icon" />
            )}
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
