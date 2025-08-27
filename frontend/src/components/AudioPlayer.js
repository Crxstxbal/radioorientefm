// src/components/AudioPlayer.js
import React, { useRef, useState, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX } from "lucide-react";

const AudioPlayer = () => {
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
    <div className="fixed bottom-0 left-0 right-0 z-50 flex justify-center pointer-events-none">
      <div className="relative w-full max-w-3xl bg-purple-main dark:bg-purple-dark text-white flex items-center py-4 px-6 shadow-2xl backdrop-blur-md rounded-t-xl pointer-events-auto overflow-hidden">

        {/* Gradientes laterales */}
        <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-black/80 via-black/50 to-transparent z-30" />
        <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-black/80 via-black/50 to-transparent z-30" />

        {/* Izquierda */}
        <div className="flex items-center gap-2 w-48 flex-shrink-0 z-40">
          <span
            className={`w-3 h-3 rounded-full ${
              isPlaying ? "bg-green-500 animate-pulse" : "bg-red-500"
            }`}
            aria-label={isPlaying ? "En transmisión" : "No está transmitiendo"}
            title={isPlaying ? "On Air" : "Off Air"}
          />
          <div>
            <span>Radio Oriente FM</span>
            <br />
            <span className="text-sm opacity-80">107.1 FM - En vivo</span>
          </div>
        </div>     

        {/* Centro */}
        <div className="flex-grow flex flex-col items-center justify-center z-40">
          <button
            onClick={togglePlay}
            aria-label="Play/Pause"
            className="bg-purple-light dark:bg-purple-light hover:bg-purple-600 dark:hover:bg-purple-700 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300"
          >
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>
          <span className="text-sm mt-1 opacity-75">{currentTime}</span>
        </div>
        
        {/* Visualizador de onda estilo MHz */}
        <div className="absolute bottom-full mb-1 left-1/2 transform -translate-x-1/2 w-64 h-16 bg-black/50 rounded-md overflow-hidden backdrop-blur-lg border border-purple-500 shadow-lg flex items-center justify-center z-50">
          <svg
            className={`w-full h-full ${
              isPlaying ? "animate-wave" : "opacity-30"
            } transition-all duration-500`}
            viewBox="0 0 100 20"
            preserveAspectRatio="none"
          >
            <polyline
              fill="none"
              stroke={isPlaying ? "#8b5cf6" : "#ef4444"}
              strokeWidth="2"
              points="0,10 10,5 20,15 30,5 40,15 50,5 60,15 70,5 80,15 90,5 100,10"
            />
          </svg>
        </div>

        {/* Derecha: volumen modernizado con punto */}
        <div className="flex items-center gap-3 w-48 flex-shrink-0 z-40">
          <button
            onClick={toggleMute}
            aria-label="Mute/Unmute"
            className="p-2 rounded-full hover:bg-white/10 transition duration-200"
          >
            {isMuted ? (
              <VolumeX size={20} className="text-white" />
            ) : (
              <Volume2 size={20} className="text-white" />
            )}
          </button>

          <div className="relative group w-28 h-2 rounded-full bg-white/10 overflow-hidden transition-all duration-300">
            {/* Barra dinámica: verde si en reproducción, rojo si no */}
            <div
              className={`absolute top-0 left-0 h-full ${
                isPlaying ? "bg-purple-400 group-hover:bg-green-400" : "bg-red-500"
              } transition-all duration-300`}
              style={{ width: `${volume * 100}%` }}
            />

            {/* Punto (thumb) visible solo en hover */}
            <div
              className={`absolute top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 rounded-full border-2 ${
                isPlaying ? "bg-purple-500 group-hover:bg-green-500" : "bg-red-500"
              } border-white shadow transition-all duration-300 opacity-0 group-hover:opacity-100`}
              style={{ left: `calc(${volume * 100}% - 7px)` }}
            />

            {/* Input invisible funcional */}
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={handleVolumeChange}
              className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
            />
          </div>
        </div>

      </div>
    </div>
  );
};

export default AudioPlayer;
