import React, { useEffect, useState, useCallback, useMemo } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Menu, X, Radio, User, Sun, Moon, LayoutDashboard, Bell, Wifi } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";
import "./Navbar.css";
import api from '../utils/api';

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

  // --- LOGICA DE NOMBRE SEGURO ---
  // Calculamos qué nombre mostrar. Prioridad:
  // 1. 'user_name' en localStorage (Guardado por GoogleAuth)
  // 2. user.first_name (Si el backend lo envía)
  // 3. user.username (Si es email, lo cortamos antes del @)
  const displayName = useMemo(() => {
    if (!user) return '';
    
    // 1. Intento leer lo que guardó GoogleAuth
    const localName = localStorage.getItem('user_name');
    if (localName && localName !== 'undefined') return localName;

    // 2. Intento leer nombre real del objeto user
    if (user.first_name) return user.first_name;

    // 3. Fallback: Si es un email, mostramos solo la parte antes del @
    const username = user.username || '';
    if (username.includes('@')) {
        return username.split('@')[0]; // "juan@gmail.com" -> "juan"
    }
    return username;
  }, [user]);
  // ------------------------------

  const navItems = [
    { name: "Inicio", path: "/" },
    { name: "Programación", path: "/programacion" },
    { name: "Artículos", path: "/articulos" },
    { name: "En Vivo", path: "/en-vivo", icon: <Wifi size={16} /> },
    { name: "Contacto", path: "/contacto" },
    { name: "Suscripción", path: "/suscripcion" }
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = useCallback(() => {
    logout();
    setIsOpen(false);
    // Limpiamos también las variables de Google por si acaso
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_avatar');
  }, [logout]);

  // fetch de notificaciones
  useEffect(() => {
    let intervalId;
    const token = localStorage.getItem('token');
    if (!token) {
      setNotifCount(0);
      return;
    }
    const fetchCount = async () => {
      try {
        const resp = await api.get('/api/notifications/api/notificaciones/contador/', {
          headers: { Authorization: `Token ${token}` }
        });
        setNotifCount(resp.data?.no_leidas ?? 0);
      } catch (e) {

      }
    };
    fetchCount();
    //Se reduce el polling de 30s a 60s para rendimiento
    intervalId = setInterval(fetchCount, 60000);
    return () => intervalId && clearInterval(intervalId);
  }, [isAuthenticated]);

  const openNotifications = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    setLoadingNotifs(true);
    try {
      const resp = await api.get('/api/notifications/api/notificaciones/no_leidas/', {
        headers: { Authorization: `Token ${token}` }
      });
      setNotifs(Array.isArray(resp.data) ? resp.data : resp.data?.results || []);
    } catch (e) {
      setNotifs([]);
    } finally {
      setLoadingNotifs(false);
    }
  }, []);

  const toggleNotifications = useCallback(async () => {
    const next = !notifsOpen;
    setNotifsOpen(next);
    if (next) await openNotifications();
  }, [notifsOpen, openNotifications]);

  const markAllRead = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await api.post('/api/notifications/api/notificaciones/marcar_todas_leidas/', {}, {
        headers: { Authorization: `Token ${token}` }
      });
      setNotifCount(0);
      setNotifs([]);
    } catch (e) {}
  }, []);

  return (
    <nav className="navbar">
      <div className="container">
        <div className="nav-content">
          {/* logo */}
          <Link to="/" className="nav-logo">
            <img
              src="/images/logo.png"
              alt="Radio Oriente FM"
              className="logo-icon"
            />
            <span className="logo-text">Radio Oriente FM</span>
          </Link>

          {/* links */}
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
          </div>

          {/* sección autenticación */}
          <div className="nav-auth desktop">
            {isAuthenticated ? (
              <div className="user-menu">
                <div className="user-avatar">
                  {/* Intentamos mostrar avatar de Google si existe, sino el ícono por defecto */}
                  {localStorage.getItem('user_avatar') ? (
                      <img src={localStorage.getItem('user_avatar')} alt="Avatar" style={{width: '100%', height: '100%', borderRadius: '50%'}} />
                  ) : (
                      <User className="user-icon" size={18} />
                  )}
                </div>
                {/* AQUI ESTA EL CAMBIO: Usamos displayName en lugar de user.username */}
                <span className="user-name">{displayName}</span>
                {isAdmin && (
                  <a
                    href={dashboardUrl}
                    className="btn-dashboard-compact"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <LayoutDashboard size={14} />
                    <span>Dashboard</span>
                  </a>
                )}
                <button onClick={handleLogout} className="btn btn-logout">
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
            <Link to="/tv" className="nav-tv-btn">
              <Radio size={16} />
              <span>TV en vivo</span>
            </Link>
          </div>

          {/* boton de menu en dispositivo mobil */}
          <button
            className="mobile-menu-btn"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* navegacion mobile */}
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
            {isAuthenticated && (
              <div className="mobile-theme-notification">
                <button
                  className="notification-toggle-mobile"
                  aria-label="Notificaciones"
                  title="Notificaciones"
                  onClick={async (e) => {
                    e.stopPropagation();
                    await toggleNotifications();
                    //aqui no se cierra las notificaciones
                  }}
                >
                  <Bell size={20} />
                  {notifCount > 0 && (
                    <span className="notification-badge-mobile">{Math.min(notifCount, 99)}</span>
                  )}
                  <span>Notificaciones {notifCount > 0 && `(${notifCount})`}</span>
                </button>

                {/* panel de notificaciones mobile */}
                {notifsOpen && (
                  <div className="notifications-dropdown-mobile">
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
            <div className="mobile-theme-toggle-wrapper">
              <button
                className="theme-toggle-mobile"
                onClick={() => { toggleTheme(); setIsOpen(false); }}
                aria-label="Cambiar tema"
                title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                <span className="theme-toggle-text">Modo {theme === 'dark' ? 'Claro' : 'Oscuro'}</span>
              </button>
            </div>
            <div className="mobile-auth">
              {isAuthenticated ? (
                <>
                  <User className="user-icon" size={18} />
                  {/* También actualizado en la vista móvil */}
                  <span className="user-name">Hola {displayName}</span>
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