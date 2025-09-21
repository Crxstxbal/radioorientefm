import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Menu, X, Radio, User } from "lucide-react"; // agregamos User
import "./Navbar.css";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: "Inicio", path: "/" },
    { name: "Programación", path: "/programacion" },
    { name: "Noticias", path: "/noticias" },
    { name: "Contacto", path: "/contacto" },
    { name: "Suscripción", path: "/suscripcion" },
    { name: "Blog", path: "/blog" },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="container">
        <div className="nav-content">
          {/* Logo */}
          <Link to="/" className="nav-logo">
            <img
              src="/images/logo.png"
              alt="Radio Oriente FM"
              className="logo-icon"
            />
            <span className="logo-text">Radio Oriente FM</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="nav-links desktop">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? "active" : ""}`}
              >
                {item.name}
              </Link>
            ))}
          </div>

          {/* Auth Section */}
          <div className="nav-auth desktop">
            {isAuthenticated ? (
              <div className="user-menu">
                <User className="user-icon" size={20} /> {/* icono al lado del nombre */}
                <span className="user-name">Hola {user.username}</span>
                <button onClick={handleLogout} className="btn btn-outline">
                  Cerrar Sesión
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn btn-primary">
                Iniciar Sesión
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="mobile-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-link ${
                  isActive(item.path) ? "active" : ""
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            <div className="mobile-auth">
              {isAuthenticated ? (
                <>
                  <User className="user-icon" size={18} />
                  <span className="user-name">Hola {user.username}</span>
                  <button onClick={handleLogout} className="btn btn-outline">
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  className="btn btn-primary"
                  onClick={() => setIsOpen(false)}
                >
                  Iniciar Sesión
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
