import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AudioProvider } from './contexts/AudioContext';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';


//componentees
import Navbar from './components/Navbar';
import RadioPlayer from './components/RadioPlayer';
import LiveChat from './components/LiveChat';
import Footer from "./components/Footer";
import ScrollToTop from './components/ScrollToTop';

//páginas
import Home from './pages/Home';
import Programacion from './pages/Programacion';
import Articulos from './pages/Articulos';
import Contacto from './pages/Contacto';
import Suscripcion from './pages/Suscripcion';
import IniciarSesion from './pages/IniciarSesion';
import Registro from './pages/Registro';
import RecuperarContrasena from './pages/RecuperarContrasena';
import ResetearContrasena from './pages/ResetearContrasena';
import Emergente from './components/Emergente';
import Reproductor from './pages/reproductor';
import PublicidadPage from './pages/PublicidadPage';
import EnVivo from './pages/EnVivo';
import Television from './pages/Television';

//diseños
import LayoutPrincipal from './layouts/LayoutPrincipal';
import LayoutPantallaCompleta from './layouts/LayoutPantallaCompleta';

function App() {

  useEffect(() => {
    const originalTitle = document.title;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        document.title = "¡Vuelve a la mejor radio!";
      } else {
        document.title = originalTitle;
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  return (
    <ThemeProvider>
      <AudioProvider> {/*<-- audioprovider envuelve todo*/}
        <Router>
          <ScrollToTop />
          <Routes>
            {/*diseño principal con navbar, radio, chat y footer*/}
            <Route element={<LayoutPrincipal />}>
              <Route path="/" element={<Home />} />
              <Route path="/programacion" element={<Programacion />} />
              <Route path="/articulos" element={<Articulos />} />
              <Route path="/articulos/:slug" element={<Articulos />} /> {/*artículo individual por slug*/}
              <Route path="/noticias" element={<Articulos />} /> {/*redirecciona a artículos*/}
              <Route path="/blog" element={<Articulos />} /> {/*redirecciona a artículos har que arreglarlo*/}
              <Route path="/contacto" element={<Contacto />} />
              <Route path="/suscripcion" element={<Suscripcion />} />
              <Route path="/emergente" element={<Emergente />} />
              <Route path="/iniciar-sesion" element={<IniciarSesion />} />
              <Route path="/login" element={<IniciarSesion />} /> {/*redirección de compatibilidad*/}
              <Route path="/registro" element={<Registro />} />
              <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
              <Route path="/resetear-contrasena/:uid/:token" element={<ResetearContrasena />} />
              <Route path="/publicidad" element={<PublicidadPage />} />
              <Route path="/en-vivo" element={<EnVivo />} />
              <Route path="/tv" element={<Television />} />
            </Route>

            {/*diseño full screen solo para el reproductor de radio*/}
            <Route element={<LayoutPantallaCompleta />}>
              <Route path="/reproductor" element={<Reproductor />} />
            </Route>
          </Routes>

          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#000',
                color: '#fff',
              },
            }}
          />
        </Router>
      </AudioProvider>
    </ThemeProvider>
  );
}

export default App;
