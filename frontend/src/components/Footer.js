import React from "react";
import { Instagram, Facebook, Youtube } from "lucide-react";
import "./Footer.css";

const Footer = () => {
    return (
        <footer className="footer">
        <div className="footer-container">
            <div className="footer-left">
            <p>© {new Date().getFullYear()} Radio Oriente FM. Todos los derechos reservados.</p>
            </div>
            <div className="footer-right">
            <a
                href="https://www.instagram.com/radioorientefm"
                target="_blank"
                rel="noopener noreferrer"
                className="social-link"
            >
                <Instagram size={24} />
            </a>
            <a
                href="https://www.facebook.com/RadioOrienteFm/?locale=es_LA"
                target="_blank"
                rel="noopener noreferrer"
                className="social-link"
            >
                <Facebook size={24} />
            </a>
            <a
                href="https://www.youtube.com/@eldc100"
                target="_blank"
                rel="noopener noreferrer"
                className="social-link"
            >
                <Youtube size={24} />
            </a>
            </div>
        </div>
        </footer>
    );
};

export default Footer;
