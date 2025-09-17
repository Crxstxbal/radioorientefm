import React, { useRef, useState, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX } from "lucide-react";
import './RadioPlayer.css';

const RadioPlayer = () => {
  const audioRef = useRef(new Audio("https://sonic-us.fhost.cl/8126/stream"));
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(() => {
    const saved = localStorage.getItem("radioVolume");
    return saved !== null ? Number(saved) : 1;
  });
  const [lastVolume, setLastVolume] = useState(volume);
  const [isMuted, setIsMuted] = useState(volume === 0);
  const [currentTime, setCurrentTime] = useState(() =>
    new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );

  // Actualizar hora cada segundo
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(
        new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Guardar volumen y mute
  useEffect(() => {
    audioRef.current.volume = volume;
    localStorage.setItem("radioVolume", volume);
    setIsMuted(volume === 0);
  }, [volume]);

  // Mantener reproducción al cambiar de pestaña
  useEffect(() => {
    const wasPlaying = sessionStorage.getItem("radioPlaying") === "true";
    if (wasPlaying) {
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
    return () => {
      sessionStorage.setItem("radioPlaying", audioRef.current.paused ? "false" : "true");
    };
  }, []);

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = Number(e.target.value);
    setVolume(newVolume);
    if (newVolume > 0) {
      setLastVolume(newVolume);
    }
  };

  const toggleMute = () => {
    if (isMuted) {
      setVolume(lastVolume || 1);
    } else {
      setLastVolume(volume);
      setVolume(0);
    }
  };

  return (
    <div className="radio-player-container">
      <div className="radio-player">
        {/* Side gradients */}
        <div className="gradient-left" />
        <div className="gradient-right" />

        {/* Left section */}
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

        {/* Center section */}
        <div className="player-controls">
          <button
            onClick={togglePlay}
            aria-label="Play/Pause"
            className="control-icon"
          >
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>
          <span className="text-sm mt-1 opacity-75">{currentTime}</span>
        </div>
        
        {/* Waveform visualization */}
        <div className="waveform-container">
          <svg
            className={`waveform-svg ${isPlaying ? 'animate-wave' : 'waveform-paused'}`}
            viewBox="0 0 100 20"
            preserveAspectRatio="none"
          >
            <polyline
              className="waveform-line"
              points="0,10 10,5 20,15 30,5 40,15 50,5 60,15 70,5 80,15 90,5 100,10"
            />
          </svg>
        </div>

        {/* Control del volumen */}
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
