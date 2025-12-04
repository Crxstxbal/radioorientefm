import React, { useEffect, useRef } from "react";
import { Instagram, Facebook, Youtube, Radio } from "lucide-react";
import "./Footer.css";

const Footer = () => {
  const piePaginaRef = useRef(null);
  const ondaRef = useRef(null);
  const enlacesSocialesRef = useRef([]);
  const textoRef = useRef(null);
  const logoRef = useRef(null);

  useEffect(() => {
    //simulamos gsap con css animations y javascript
    const piePagina = piePaginaRef.current;
    const onda = ondaRef.current;
    const enlacesSociales = enlacesSocialesRef.current;
    const texto = textoRef.current;
    const logo = logoRef.current;

    //animación de entrada del pie de página
    if (piePagina) {
      piePagina.style.transform = 'translateY(50px)';
      piePagina.style.opacity = '0';
      
      setTimeout(() => {
        piePagina.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        piePagina.style.transform = 'translateY(0)';
        piePagina.style.opacity = '1';
      }, 100);
    }

    //animación de onda
    if (onda) {
      onda.style.animation = 'animacionOnda 3s ease-in-out infinite';
    }

    //animación del logo
    if (logo) {
      setTimeout(() => {
        logo.style.transform = 'scale(1) rotate(0deg)';
        logo.style.opacity = '1';
      }, 400);
    }

    //animación escalonada de redes sociales
    enlacesSociales.forEach((enlace, indice) => {
      if (enlace) {
        enlace.style.transform = 'translateY(30px) scale(0.8)';
        enlace.style.opacity = '0';
        
        setTimeout(() => {
          enlace.style.transition = 'all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
          enlace.style.transform = 'translateY(0) scale(1)';
          enlace.style.opacity = '1';
        }, 600 + indice * 150);
      }
    });

    //animación del texto
    if (texto) {
      texto.style.transform = 'translateX(-30px)';
      texto.style.opacity = '0';
      
      setTimeout(() => {
        texto.style.transition = 'all 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        texto.style.transform = 'translateX(0)';
        texto.style.opacity = '1';
      }, 300);
    }

    //animación de hover para las redes sociales
    enlacesSociales.forEach(enlace => {
      if (enlace) {
        enlace.addEventListener('mouseenter', () => {
          enlace.style.transform = 'translateY(-8px) scale(1.15) rotate(5deg)';
          enlace.style.filter = 'drop-shadow(0 10px 20px rgba(230, 0, 35, 0.4))';
        });
        
        enlace.addEventListener('mouseleave', () => {
          enlace.style.transform = 'translateY(0) scale(1) rotate(0deg)';
          enlace.style.filter = 'none';
        });
      }
    });

    }, []);

    return (
        <footer className="pie-pagina" ref={piePaginaRef}>
        <div className="patron-fondo"></div>
        <div className="onda-superior" ref={ondaRef}></div>
        <div className="ondas-fondo"></div>
        
        <div className="contenedor-pie">
            <div className="marca-radio">
            <div className="logo-radio" ref={logoRef}>
                <Radio size={24} />
            </div>
            <div>
                <h3 className="texto-marca">Radio Oriente FM</h3>
                <p className="frecuencia">Tu música, tu momento</p>
            </div>
            </div>
            
            <div className="redes-sociales">
            <a
                href="https://www.instagram.com/radioorientefm"
                target="_blank"
                rel="noopener noreferrer"
                className="enlace-social instagram"
                ref={el => enlacesSocialesRef.current[0] = el}
            >
                <Instagram size={22} />
            </a>
            <a
                href="https://www.facebook.com/RadioOrienteFm/?locale=es_LA"
                target="_blank"
                rel="noopener noreferrer"
                className="enlace-social facebook"
                ref={el => enlacesSocialesRef.current[1] = el}
            >
                <Facebook size={22} />
            </a>
            <a
                href="https://www.youtube.com/@eldc100"
                target="_blank"
                rel="noopener noreferrer"
                className="enlace-social youtube"
                ref={el => enlacesSocialesRef.current[2] = el}
            >
                <Youtube size={22} />
            </a>
            </div>
            <div ref={textoRef}>
                <p className="derechos-autor">
                    © {new Date().getFullYear()} Radio Oriente FM<br />
                    Todos los derechos reservados
                </p>
            </div>
        </div>
        </footer>
    );
    };

export default Footer;