import { useState, useEffect, useRef, useMemo } from 'react';
import { MessageCircle, Send, X, Users, Minimize2, Maximize2, Radio, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import './LiveChat.css';

const LiveChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isRadioOnline, setIsRadioOnline] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState(0);
  const [error, setError] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isPlayerCollapsed, setIsPlayerCollapsed] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const messagesEndRef = useRef(null);
  const pollingIntervalRef = useRef(null);
  const wsRef = useRef(null);

  // --- LOGICA DE NOMBRE SEGURO (PRIVACIDAD) ---
  // 1. Calculamos tu nombre para mostrar en mensajes nuevos
  const displayName = useMemo(() => {
    if (!user) return '';
    
    // Prioridad 1: Nombre guardado por GoogleAuth
    const localName = localStorage.getItem('user_name');
    if (localName && localName !== 'undefined') return localName;

    // Prioridad 2: Nombre del objeto user
    if (user.first_name) return user.first_name;

    // Prioridad 3: Username cortado si es correo
    const username = user.username || '';
    if (username.includes('@')) {
        return username.split('@')[0]; 
    }
    return username;
  }, [user]);

  // 2. Función para limpiar nombres en el historial del chat (Otros usuarios)
  const formatAuthorName = (name) => {
    if (!name) return 'Anónimo';
    // Si el nombre parece un correo, lo cortamos
    if (name.includes('@')) {
        return name.split('@')[0]; 
    }
    return name;
  };
  // ---------------------------------------------

  //detectar si el reproductor está colapsado
  useEffect(() => {
    const checkPlayerCollapsed = () => {
      const radioPlayer = document.querySelector('.radio-player-wrapper');
      setIsPlayerCollapsed(radioPlayer?.classList.contains('collapsed') || false);
    };

    checkPlayerCollapsed();

    //observer para detectar cambios
    const observer = new MutationObserver(checkPlayerCollapsed);
    const radioPlayer = document.querySelector('.radio-player-wrapper');

    if (radioPlayer) {
      observer.observe(radioPlayer, { attributes: true, attributeFilter: ['class'] });
    }

    return () => observer.disconnect();
  }, []);

  //verificar estado de la radio
  useEffect(() => {
    const checkRadioStatus = async () => {
      try {
        const response = await api.get('/api/chat/radio-status/');
        setIsRadioOnline(response.data.is_online);
      } catch (error) {
        console.error('Error checking radio status:', error);
        setIsRadioOnline(false);
      }
    };

    checkRadioStatus();
    const statusInterval = setInterval(checkRadioStatus, 10000); // Cada 10 segundos

    return () => clearInterval(statusInterval);
  }, []);

  //cargar mensajes cuando se abre el chat
  useEffect(() => {
    if (isOpen && isAuthenticated) {
      loadMessages();
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [isOpen, isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  //websocket para presencia en tiempo real (usuarios activos en la sala)
  useEffect(() => {
    try {
      const rawBase = (import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').toString();
      const toWs = (u) => {
        let s = u.trim();
        if (!/^https?:\/\//i.test(s) && !/^wss?:\/\//i.test(s)) s = 'http://' + s;
        s = s.replace(/^http:/i, 'ws:').replace(/^https:/i, 'wss:');
        return s.replace(/\/$/, '') + '/ws/chat/radio-oriente/';
      };
      const wsUrl = toWs(rawBase);
      
      console.log('🔌 Conectando WebSocket a:', wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket conectado');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 Mensaje WebSocket recibido:', data);
          
          if (data && data.type === 'presence' && typeof data.users_online === 'number') {
            console.log('👥 Actualizando usuarios conectados:', data.users_online);
            setOnlineUsers(data.users_online);
          }
        } catch (error) {
          console.error('❌ Error parseando mensaje WS:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket cerrado:', event.code, event.reason);
        wsRef.current = null;
      };

      ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
      };

      return () => {
        try { 
          console.log('🔌 Cerrando WebSocket');
          ws.close(); 
        } catch (_) {}
      };
    } catch (error) {
      console.error('❌ Error creando WebSocket:', error);
    }
  }, []);

  const loadMessages = async () => {
    try {
      const response = await api.get('/api/chat/messages/radio-oriente/');

      //la api puede devolver un array directo o un objeto con 'results'
      const messagesData = Array.isArray(response.data) ? response.data : (response.data.results || []);

      const loadedMessages = messagesData.map(msg => ({
        id: msg.id,
        message: msg.contenido,
        user_name: msg.usuario_nombre,
        username: msg.usuario_nombre,
        timestamp: msg.fecha_envio,
        isOwn: msg.usuario_nombre === user?.username
      }));
      setMessages(loadedMessages.reverse());
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const startPolling = () => {
    //actualizar mensajes cada 3 segundos
    pollingIntervalRef.current = setInterval(() => {
      loadMessages();
    }, 3000);
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    if (!isRadioOnline) {
      setError('El chat solo está disponible cuando la radio está en vivo');
      setTimeout(() => setError(''), 3000);
      return;
    }

    const messageContent = newMessage.trim();
    setIsSending(true);
    setError('');
    setNewMessage(''); // Limpiar input inmediatamente

    //optimistic actualizar: agregar mensaje inmediatamente
    const tempMessage = {
      id: `temp-${Date.now()}`,
      message: messageContent,
      // AQUI EL CAMBIO 1: Usamos displayName en vez de user.username
      user_name: displayName,
      username: displayName,
      timestamp: new Date().toISOString(),
      isOwn: true
    };
    setMessages(prev => [...prev, tempMessage]);

    try {
      await api.post('/api/chat/messages/radio-oriente/', {
        contenido: messageContent
      });
      //recargar mensajes para obtener el mensaje real del servidor
      await loadMessages();
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Error response:', error.response?.data);

      //remover mensaje temporal
      setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));

      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else if (error.response?.data) {
        //mostrar el primer error que encuentre
        const firstError = Object.values(error.response.data)[0];
        setError(Array.isArray(firstError) ? firstError[0] : firstError);
      } else {
        setError('Error al enviar el mensaje. Intenta de nuevo.');
      }
      setTimeout(() => setError(''), 3000);
    } finally {
      setIsSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setIsMinimized(false);
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <>
      {/*chat toggle button*/}
      <button
        className={`chat-toggle ${isOpen ? 'active' : ''} ${isPlayerCollapsed ? 'player-collapsed' : ''}`}
        onClick={toggleChat}
        title="Chat en vivo"
      >
        <MessageCircle size={22} />
        <span>Chat en Vivo</span>
        {!isOpen && isRadioOnline && (
          <span className="chat-notification">
            <span className="notification-dot"></span>
          </span>
        )}
      </button>

      {/*chat window*/}
      <div className={`chat-window ${isMinimized ? 'minimized' : ''} ${isOpen ? 'open' : ''}`}>
          {/*chat header*/}
          <div className="chat-header">
            <div className="chat-title">
              <MessageCircle size={20} />
              <span>Chat en Vivo</span>
              <div className="connection-status">
                <Radio size={14} />
                <span className={`status-dot ${isRadioOnline ? 'connected' : 'disconnected'}`}></span>
                <span className="status-text">
                  {isRadioOnline ? 'Radio en Vivo' : 'Radio Offline'}
                </span>
              </div>
            </div>
            <div className="chat-controls">
              <button
                className="control-btn"
                onClick={toggleMinimize}
                title={isMinimized ? 'Maximizar' : 'Minimizar'}
              >
                {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
              </button>
              <button
                className="control-btn close-btn"
                onClick={toggleChat}
                title="Cerrar chat"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/*online users*/}
              <div className="online-users">
                <Users size={16} />
                <span>{onlineUsers} usuarios conectados</span>
              </div>

              {/*messages area*/}
              <div className="messages-container">
                {!isAuthenticated ? (
                  <div className="auth-required">
                    <MessageCircle size={48} />
                    <p>Inicia sesión para participar en el chat</p>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => window.location.href = '/login'}
                    >
                      Iniciar Sesión
                    </button>
                  </div>
                ) : !isRadioOnline ? (
                  <div className="auth-required">
                    <Radio size={48} />
                    <p>El chat está disponible cuando la radio está en vivo</p>
                    <small>Vuelve cuando estemos transmitiendo</small>
                  </div>
                ) : (
                  <>
                    <div className="messages-list">
                      {messages.length === 0 ? (
                        <div className="no-messages">
                          <MessageCircle size={48} />
                          <p>¡Sé el primero en enviar un mensaje!</p>
                        </div>
                      ) : (
                        messages.map((message) => (
                          <div
                            key={message.id}
                            className={`message ${message.isOwn ? 'own' : 'other'}`}
                          >
                            <div className="message-content">
                              <div className="message-header">
                                <span className="message-author">
                                  {/* AQUI EL CAMBIO 2: Aplicamos el filtro al mostrar el nombre */}
                                  {formatAuthorName(message.user_name || message.username)}
                                </span>
                                <span className="message-time">
                                  {formatTime(message.timestamp)}
                                </span>
                              </div>
                              <div className="message-text">
                                {message.message}
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                      <div ref={messagesEndRef} />
                    </div>

                    {/*error message*/}
                    {error && (
                      <div className="chat-error">
                        <AlertCircle size={14} />
                        <span>{error}</span>
                      </div>
                    )}

                    {/*message input*/}
                    <form onSubmit={sendMessage} className="message-form">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder={isRadioOnline ? "Escribe tu mensaje..." : "Radio offline"}
                        className="message-input"
                        disabled={!isRadioOnline || isSending}
                        maxLength={500}
                      />
                      <button
                        type="submit"
                        className="send-btn"
                        disabled={!newMessage.trim() || !isRadioOnline || isSending}
                      >
                        <Send size={18} />
                      </button>
                    </form>
                  </>
                )}
              </div>
            </>
          )}
        </div>
    </>
  );
};

export default LiveChat;