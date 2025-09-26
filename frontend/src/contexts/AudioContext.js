import React, { createContext, useState, useRef, useEffect } from "react";

export const AudioContextGlobal = createContext();

export const AudioProvider = ({ children }) => {
  const audioRef = useRef(new Audio()); // Una sola instancia de audio
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(() => {
    const saved = localStorage.getItem("radioVolume");
    return saved !== null ? Number(saved) : 1;
  });
  const [streamUrl, setStreamUrl] = useState(null);

  // Traer URL del backend SOLO UNA VEZ al cargar el componente
  useEffect(() => {
    const fetchStream = async () => {
      try {
        const res = await fetch("/api/radio/station/");
        const data = await res.json();

        // Asegurarse de que streamUrl sea un string
        const url = typeof data.stream_url === "string"
          ? data.stream_url
          : data.stream_url?.src || null;

        setStreamUrl(url);

        if (url) {
          audioRef.current.src = url;
          audioRef.current.volume = volume; // Setear volumen inicial
        }
      } catch (err) {
        console.error("Error al cargar stream:", err);
      }
    };

    fetchStream();
  }, []); // SIN 'volume' aquí - solo se ejecuta una vez

  // Mantener volumen sincronizado - ESTE useEffect SÍ debe tener volume como dependencia
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
      localStorage.setItem("radioVolume", volume);
    }
  }, [volume]);

  const togglePlay = () => {
    if (!streamUrl) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
  };

  const toggleMute = () => {
    setVolume(prev => (prev > 0 ? 0 : 1));
  };

  return (
    <AudioContextGlobal.Provider value={{
      audioRef,
      isPlaying,
      togglePlay,
      volume,
      setVolume,
      toggleMute,
      streamUrl
    }}>
      {children}
    </AudioContextGlobal.Provider>
  );
};