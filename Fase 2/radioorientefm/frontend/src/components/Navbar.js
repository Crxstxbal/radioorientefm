import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Menu, X, Radio, User, Sun, Moon, LayoutDashboard, Bell } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";
import "./Navbar.css";
import axios from "axios";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const dashboardUrl = import.meta.env.VITE_DASHBOARD_URL || 'http://localhost:8000/dashboard/';
  const [notifCount, setNotifCount] = useState(0);
  const [notifsOpen, setNotifsOpen] = useState(false);
  const [notifs, setNotifs] = useState([]);
  const [loadingNotifs, setLoadingNotifs] = useState(false);

  const navItems = [
    { name: "Inicio", path: "/" },
    { name: "Programación", path: "/programacion" },
    { name: "Artículos", path: "/articulos" },
    { name: "Contacto", path: "/contacto" },
    { name: "Suscripción", path: "/suscripcion" }
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  // Fetch notifications count (if logged in)
  useEffect(() => {
    let intervalId;
    const token = localStorage.getItem('token');
    if (!token) {
      setNotifCount(0);
      return;
    }
    const fetchCount = async () => {
      try {
        const resp = await axios.get('/api/notifications/api/notificaciones/contador/', {
          headers: { Authorization: `Token ${token}` }
        });
        setNotifCount(resp.data?.no_leidas ?? 0);
      } catch (e) {
        // Silently ignore
      }
    };
    fetchCount();
    intervalId = setInterval(fetchCount, 30000);
    return () => intervalId && clearInterval(intervalId);
  }, [isAuthenticated]);

  const openNotifications = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setLoadingNotifs(true);
    try {
      const resp = await axios.get('/api/notifications/api/notificaciones/no_leidas/', {
        headers: { Authorization: `Token ${token}` }
      });
      setNotifs(Array.isArray(resp.data) ? resp.data : resp.data?.results || []);
    } catch (e) {
      setNotifs([]);
    } finally {
      setLoadingNotifs(false);
    }
  };

  const toggleNotifications = async () => {
    const next = !notifsOpen;
    setNotifsOpen(next);
    if (next) await openNotifications();
  };

  const markAllRead = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await axios.post('/api/notifications/api/notificaciones/marcar_todas_leidas/', {}, {
        headers: { Authorization: `Token ${token}` }
      });
      setNotifCount(0);
      setNotifs([]);
    } catch (e) {}
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

          {/* Links desktop */}
          <div className="nav-links desktop">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? "active" : ""}`}
              >
                {item.icon && <span className="nav-icon">{item.icon}</span>}
                {item.name}
              </Link>
            ))}
            {/* Link Dashboard solo para administradores */}
            {isAdmin && (
              <a
                href={dashboardUrl}
                className="nav-link dashboard-link"
                target="_blank"
                rel="noopener noreferrer"
              >
                <LayoutDashboard size={18} />
                Dashboard
              </a>
            )}
          </div>

          {/* Sección autenticación desktop */}
          <div className="nav-auth desktop">
            {isAuthenticated ? (
              <div className="user-menu">
                <User className="user-icon" size={35 } />
                <span className="user-name">Hola, {user.username}</span>
                <button onClick={handleLogout} className="btn btn-primary">
                  Cerrar Sesión
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn btn-primary">
                Iniciar Sesión
              </Link>
            )}
            {isAuthenticated && (
              <div className="notif-wrapper">
                <button
                  className="notification-toggle"
                  aria-label="Notificaciones"
                  title="Notificaciones"
                  onClick={toggleNotifications}
                >
                  <Bell size={18} />
                  {notifCount > 0 && (
                    <span className="notification-badge">{Math.min(notifCount, 99)}</span>
                  )}
                </button>
                {notifsOpen && (
                  <div className="notifications-dropdown">
                    <div className="notifications-header">
                      <span>Notificaciones</span>
                      {notifCount > 0 && (
                        <button className="mark-all" onClick={markAllRead}>Marcar todas como leídas</button>
                      )}
                    </div>
                    <div className="notifications-body">
                      {loadingNotifs ? (
                        <div className="notifications-empty">Cargando...</div>
                      ) : notifs.length === 0 ? (
                        <div className="notifications-empty">Sin notificaciones</div>
                      ) : (
                        notifs.slice(0, 8).map(n => (
                          <div key={n.id} className="notification-item">
                            <div className="notification-title">{n.titulo}</div>
                            <div className="notification-message">{n.mensaje}</div>
                            <div className="notification-meta">{n.tipo_display} · {n.tiempo_transcurrido}</div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label="Cambiar tema"
              title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          {/* Botón de menú en dispositivo mobil */}
          <button
            className="mobile-menu-btn"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Navegación mobile */}
        {isOpen && (
          <div className="mobile-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-link ${isActive(item.path) ? "active" : ""}`}
                onClick={() => setIsOpen(false)}
              >
                {item.icon && <span className="nav-icon">{item.icon}</span>}
                {item.name}
              </Link>
            ))}
            {/* Link Dashboard solo para administradores - Mobile */}
            {isAdmin && (
              <a
                href={dashboardUrl}
                className="mobile-nav-link dashboard-link"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsOpen(false)}
              >
                <LayoutDashboard size={18} />
                Dashboard
              </a>
            )}
            <div className="mobile-theme-notification">
              <button
                className="notification-toggle mobile"
                aria-label="Notificaciones"
                title="Notificaciones"
                onClick={() => {
                  console.log('Abrir notificaciones móvil');
                  setIsOpen(false);
                }}
              >
                <Bell size={18} />
                <span className="notification-badge">0</span>
                <span>Notificaciones</span>
              </button>
              <button
                className="theme-toggle mobile"
                onClick={() => { toggleTheme(); setIsOpen(false); }}
                aria-label="Cambiar tema"
                title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
              >
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                <span className="theme-toggle-text">{theme === 'dark' ? 'Claro' : 'Oscuro'}</span>
              </button>
            </div>
            <div className="mobile-auth">
              {isAuthenticated ? (
                <>
                  <User className="user-icon" size={18} />
                  <span className="user-name">Hola {user.username}</span>
                  <button onClick={handleLogout} className="btn btn-primary">
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
