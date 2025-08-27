import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const Navbar = ({ onLoginClick, usuario, cerrarSesion }) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    }
  }, []);

  const toggleDarkMode = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-light-purple-bg dark:bg-dark-purple-bg shadow-md z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link
          to="/"
          className="text-2xl font-bold text-purple-main dark:text-purple-light"
        >
          Radio Oriente FM
        </Link>

        <ul className="hidden md:flex space-x-6">
          <li>
            <Link
              to="/"
              className="text-purple-dark dark:text-purple-light hover:text-purple-main dark:hover:text-white"
            >
              Inicio
            </Link>
          </li>
          <li>
            <Link
              to="/programas"
              className="text-purple-dark dark:text-purple-light hover:text-purple-main dark:hover:text-white"
            >
              Programas
            </Link>
          </li>
          <li>
            <Link
              to="/noticias"
              className="text-purple-dark dark:text-purple-light hover:text-purple-main dark:hover:text-white"
            >
              Noticias
            </Link>
          </li>
          <li>
            <Link
              to="/contacto"
              className="text-purple-dark dark:text-purple-light hover:text-purple-main dark:hover:text-white"
            >
              Contacto
            </Link>
          </li>
        </ul>

        <div className="flex items-center space-x-4">
          <button
            onClick={toggleDarkMode}
            className="text-sm px-3 py-2 border rounded-lg text-purple-dark dark:text-purple-light border-purple-light dark:border-purple-dark hover:bg-purple-light dark:hover:bg-purple-dark transition-colors duration-300"
          >
            {isDark ? "🌙" : "☀️"}
          </button>

          {usuario && (
            <span className="text-purple-dark dark:text-purple-light font-semibold hidden sm:inline">
              @{usuario.usuario}
            </span>
          )}

          {!usuario ? (
            <button
              onClick={onLoginClick}
              className="btn-login px-3 py-2 bg-purple-main text-white rounded-lg hover:bg-purple-dark transition duration-300"
            >
              Iniciar sesión
            </button>
          ) : (
            <button
              onClick={cerrarSesion}
              className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition duration-300"
            >
              Cerrar sesión
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
