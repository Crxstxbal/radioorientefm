import { useState, useEffect } from 'react';
import './BarraProgresoLectura.css';

const BarraProgresoLectura = () => {
  const [scrollPercentage, setScrollPercentage] = useState(0);

  const handleScroll = () => {
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (scrollTop / scrollHeight) * 100;
    setScrollPercentage(scrolled);
  };

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Estilo para la barra de progreso con efecto neón
  const progressStyle = {
    width: `${scrollPercentage}%`,
    height: '3px',
    backgroundColor: '#ff0000',
    boxShadow: '0 0 5px #ff0000, 0 0 10px #ff0000, 0 0 15px #ff0000',
    transition: 'width 0.1s ease-out',
    position: 'relative',
    zIndex: 9999,
  };

  return (
    <div className="contenedor-barra-progreso">
      <div className="barra-progreso" style={progressStyle} />
    </div>
  );
};

export default BarraProgresoLectura;
