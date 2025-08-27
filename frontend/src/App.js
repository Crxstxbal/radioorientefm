import React, { useState, useEffect } from "react";
import { Routes, Route, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { AnimatePresence } from "framer-motion";

// Componentes globales
import PageWrapper from "./components/PageWrapper";
import Navbar from "./components/Navbar";
import AudioPlayer from "./components/AudioPlayer";
import Footer from "./components/Footer";
import AnimatedTitle from "./components/AnimatedTitle";

import Chat from "./components/Chat";
import LoginModal from "./components/LoginModal";

// Páginas
import Home from "./pages/Home";
import Programas from "./pages/Programas";
import Registro from "./pages/Registro";
import ContactoPage from "./pages/ContactoPage"; // <-- Importa la página contacto

function App() {
  const [usuarios, setUsuarios] = useState([]);
  const [usuario, setUsuario] = useState(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [showLogoutMessage, setShowLogoutMessage] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://localhost:3001/api/usuarios")
      .then((res) => setUsuarios(res.data))
      .catch((err) => console.error("Error al obtener usuarios:", err));
  }, []);

  useEffect(() => {
    const guardado = localStorage.getItem("usuario");
    if (guardado) {
      setUsuario(JSON.parse(guardado));
    }
  }, []);

  const cerrarSesion = () => {
    setShowLogoutMessage(true);
    setTimeout(() => {
      localStorage.removeItem("usuario");
      setUsuario(null);
      setShowLogoutMessage(false);
      navigate("/");
    }, 2000);
  };

  return (
    <div className="flex flex-col min-h-screen relative">
      <Navbar
        onLoginClick={() => setIsLoginOpen(true)}
        usuario={usuario}
        setUsuario={setUsuario}
        cerrarSesion={cerrarSesion}
      />

      <main className="max-w-6xl mx-auto pt-16 py-8 px-4 mb-24 flex-grow">
        <AnimatePresence mode="wait" initial={false}>
          <Routes location={location} key={location.pathname}>
            <Route
              path="/"
              element={
                <PageWrapper>
                  <Home />
                  <section className="mt-8">
                    <h2 className="text-2xl font-bold mb-4">
                      👥 Usuarios de Radio Oriente
                    </h2>
                    {usuarios.length > 0 ? (
                      <ul className="list-disc pl-6">
                        {usuarios.map((u) => (
                          <li key={u.id}>
                            {u.nombre} — {u.correo}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p>Cargando usuarios...</p>
                    )}
                  </section>

                  <section className="mt-12">
                    <Chat />
                  </section>
                </PageWrapper>
              }
            />
            <Route
              path="/programas"
              element={
                <PageWrapper>
                  <Programas />
                </PageWrapper>
              }
            />
            <Route
              path="/registro"
              element={
                <PageWrapper>
                  <Registro setUsuario={setUsuario} />
                </PageWrapper>
              }
            />
            <Route
              path="/contacto"
              element={
                <PageWrapper>
                  <ContactoPage />
                </PageWrapper>
              }
            />
          </Routes>
        </AnimatePresence>
      </main>

      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        setUsuario={setUsuario}
      />

      {showLogoutMessage && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50">
          <AnimatedTitle className="text-white text-4xl text-center">
            ¡Hasta pronto, fiel oyente {usuario?.usuario}!
          </AnimatedTitle>
        </div>
      )}

      <Footer />
      <AudioPlayer />
    </div>
  );
}

export default App;
