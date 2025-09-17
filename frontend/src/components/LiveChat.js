import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, X, Users, Minimize2, Maximize2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import './LiveChat.css';

const LiveChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState(0);
  const { user, isAuthenticated } = useAuth();
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      connectWebSocket();
    } else if (wsRef.current) {
      wsRef.current.close();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isOpen, isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/chat/radio-oriente/`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, {
        id: Date.now(),
        message: data.message,
        user_name: data.user_name,
        username: data.username,
        timestamp: data.timestamp,
        isOwn: data.username === user?.username
      }]);
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() && wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        message: newMessage.trim()
      }));
      setNewMessage('');
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
      {/* Chat Toggle Button */}
      <button 
        className={`chat-toggle ${isOpen ? 'active' : ''}`}
        onClick={toggleChat}
        title="Chat en vivo"
      >
        <MessageCircle size={24} />
        {!isOpen && (
          <span className="chat-notification">
            <span className="notification-dot"></span>
          </span>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={`chat-window ${isMinimized ? 'minimized' : ''}`}>
          {/* Chat Header */}
          <div className="chat-header">
            <div className="chat-title">
              <MessageCircle size={20} />
              <span>Chat en Vivo</span>
              <div className="connection-status">
                <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
                <span className="status-text">
                  {isConnected ? 'Conectado' : 'Desconectado'}
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
              {/* Online Users */}
              <div className="online-users">
                <Users size={16} />
                <span>{onlineUsers} usuarios conectados</span>
              </div>

              {/* Messages Area */}
              <div className="messages-container">
                {!isAuthenticated ? (
                  <div className="auth-required">
                    <p>Inicia sesión para participar en el chat</p>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => window.location.href = '/login'}
                    >
                      Iniciar Sesión
                    </button>
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
                                  {message.user_name || message.username}
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

                    {/* Message Input */}
                    <form onSubmit={sendMessage} className="message-form">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Escribe tu mensaje..."
                        className="message-input"
                        disabled={!isConnected}
                        maxLength={500}
                      />
                      <button 
                        type="submit" 
                        className="send-btn"
                        disabled={!newMessage.trim() || !isConnected}
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
      )}
    </>
  );
};

export default LiveChat;
