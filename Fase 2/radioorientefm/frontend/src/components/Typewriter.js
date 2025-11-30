// frontend/src/components/Typewriter.js

import React, { useState, useEffect } from 'react';

// Lista de textos para animar
const animatedTexts = [
  "Radio Oriente FM",
  "La Mejor de Peñalolén"
];

const Typewriter = () => {
  const [displayedText, setDisplayedText] = useState("");
  const [textIndex, setTextIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentFullText = animatedTexts[textIndex];
    const typingSpeed = isDeleting ? 50 : 50;
    const pauseAfterComplete = 2500;
    const pauseAfterDelete = 500;

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        // Escribiendo
        if (displayedText.length < currentFullText.length) {
          setDisplayedText(currentFullText.substring(0, displayedText.length + 1));
        } else {
          // Terminó de escribir, esperar y luego borrar
          setTimeout(() => setIsDeleting(true), pauseAfterComplete);
        }
      } else {
        // Borrando
        if (displayedText.length > 0) {
          setDisplayedText(currentFullText.substring(0, displayedText.length - 1));
        } else {
          // Terminó de borrar, cambiar al siguiente texto
          setIsDeleting(false);
          setTextIndex((prev) => (prev + 1) % animatedTexts.length);
          setTimeout(() => {}, pauseAfterDelete);
        }
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [displayedText, isDeleting, textIndex]); // Quitamos 'animatedTexts' de las dependencias

  return (
    <span className="text-red typewriter-text">
      {displayedText}
      <span
        className="cursor"
        style={{
          display: 'inline-block',
          marginLeft: '2px',
          fontWeight: 700
        }}
      >
        <span style={{
          animation: 'pulse-cursor 0.8s ease-in-out infinite',
          display: 'inline-block'
        }}>|</span>
      </span>
    </span>
  );
};

export default Typewriter;