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

  //traer url del backend solo una vez al cargar el componentee
  useEffect(() => {
    const fetchStream = async () => {
      try {
        const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const res = await fetch(`${base}/api/radio/station/`);
        const data = await res.json();

        //asegurarse de que streamurl sea un string
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

  //mantener volumen sincronizado - este useefecto sí debe tener volume como dependencia
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