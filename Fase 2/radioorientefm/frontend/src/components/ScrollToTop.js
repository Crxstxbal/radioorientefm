import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const ScrollToTop = () => {
    const { pathname } = useLocation();

    useEffect(() => {
        //scroll al inicio de la página cuando cambia la ruta
        window.scrollTo({
            top: 0,
            left: 0,
            behavior: 'instant' // 'instant' para que sea inmediato, 'smooth' para animación
        });
    }, [pathname]);

    return null;
};

export default ScrollToTop;
