import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const LoginModal = ({ isOpen, onClose, setUsuario }) => {
  const [modoRecuperar, setModoRecuperar] = useState(false);
  const [usuarioInput, setUsuarioInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [correoRecuperar, setCorreoRecuperar] = useState("");
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  if (!isOpen) return null;

  // Función para login
  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await axios.post("http://localhost:3001/api/login", {
        usuario: usuarioInput,
        password: passwordInput,
      });
      setUsuario(res.data);
      localStorage.setItem("usuario", JSON.stringify(res.data));
      onClose();
    } catch (err) {
      setError("Usuario o contraseña incorrectos");
    }
  };

  // Función para enviar correo de recuperación
  const handleRecuperar = async (e) => {
    e.preventDefault();
    setError(null);
    setMensaje(null);
    try {
      const res = await axios.post("http://localhost:3001/api/recuperar", {
        correo: correoRecuperar,
      });
      setMensaje(res.data.mensaje);
    } catch (err) {
      setError(
        err.response?.data?.mensaje ||
          "Error enviando correo, revisa el correo ingresado"
      );
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg max-w-md w-full p-6 relative">
        <button
          className="absolute top-2 right-2 text-gray-600 dark:text-gray-300"
          onClick={() => {
            setModoRecuperar(false);
            setError(null);
            setMensaje(null);
            onClose();
          }}
          aria-label="Cerrar modal"
        >
          ✖
        </button>

        {!modoRecuperar ? (
          <>
            <h2 className="text-xl font-bold mb-4 text-center">Iniciar Sesión</h2>
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="text"
                placeholder="Usuario"
                value={usuarioInput}
                onChange={(e) => setUsuarioInput(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                required
              />
              <input
                type="password"
                placeholder="Contraseña"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                required
              />
              {error && <p className="text-red-600">{error}</p>}
              <button
                type="submit"
                className="w-full bg-purple-main text-white py-2 rounded hover:bg-purple-dark transition"
              >
                Entrar
              </button>
            </form>

            <p className="mt-4 text-center text-sm text-gray-700 dark:text-gray-300">
              <button
                className="underline hover:text-purple-main"
                onClick={() => {
                  setModoRecuperar(true);
                  setError(null);
                  setMensaje(null);
                }}
              >
                ¿Olvidaste tu contraseña?
              </button>
            </p>

            {/* Botón para registrarse */}
            <p className="mt-4 text-center text-sm text-gray-700 dark:text-gray-300">
              ¿No tienes cuenta?{" "}
              <button
                onClick={() => {
                  onClose();
                  navigate("/registro");
                }}
                className="underline text-blue-600 hover:text-blue-800"
              >
                Regístrate aquí
              </button>
            </p>
          </>
        ) : (
          <>
            <h2 className="text-xl font-bold mb-4 text-center">
              Recuperar Contraseña
            </h2>
            <form onSubmit={handleRecuperar} className="space-y-4">
              <input
                type="email"
                placeholder="Correo electrónico"
                value={correoRecuperar}
                onChange={(e) => setCorreoRecuperar(e.target.value)}
                className="w-full px-3 py-2 border rounded"
                required
              />
              {error && <p className="text-red-600">{error}</p>}
              {mensaje && <p className="text-green-600">{mensaje}</p>}
              <button
                type="submit"
                className="w-full bg-purple-main text-white py-2 rounded hover:bg-purple-dark transition"
              >
                Enviar correo de recuperación
              </button>
            </form>
            <p className="mt-4 text-center text-sm text-gray-700 dark:text-gray-300">
              <button
                className="underline hover:text-purple-main"
                onClick={() => {
                  setModoRecuperar(false);
                  setError(null);
                  setMensaje(null);
                }}
              >
                Volver a iniciar sesión
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default LoginModal;
