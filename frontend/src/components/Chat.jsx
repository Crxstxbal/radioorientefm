import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Chat() {
  const [mensajes, setMensajes] = useState([]);
  const [nuevoMensaje, setNuevoMensaje] = useState('');
  const [usuarioId, setUsuarioId] = useState(1); // Ajusta según usuario logueado

  // Cargar mensajes
  const cargarMensajes = () => {
    axios.get('http://localhost:3001/api/mensajes')
      .then(res => setMensajes(res.data))
      .catch(err => console.error('Error al cargar mensajes:', err));
  };

  useEffect(() => {
    cargarMensajes();
  }, []);

  // Enviar mensaje
  const enviarMensaje = async (e) => {
    e.preventDefault();
    if (!nuevoMensaje.trim()) return;

    try {
      await axios.post('http://localhost:3001/api/mensajes', {
        id_usuario: usuarioId,
        contenido: nuevoMensaje.trim()
      });
      setNuevoMensaje('');
      cargarMensajes();
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
    }
  };

  return (
    <div className="chat-container p-4 border rounded max-w-xl mx-auto bg-white shadow-md">
      <h2 className="text-xl font-bold mb-4">Chat en vivo</h2>
      <ul className="mb-4 max-h-60 overflow-y-auto border p-2 rounded">
        {mensajes.map(msg => (
          <li key={msg.id} className="mb-2">
            <b>{msg.usuario}:</b> {msg.contenido} <small className="text-gray-500">({new Date(msg.fecha_envio).toLocaleTimeString()})</small>
          </li>
        ))}
      </ul>

      <form onSubmit={enviarMensaje} className="flex gap-2">
        <input
          type="text"
          value={nuevoMensaje}
          onChange={e => setNuevoMensaje(e.target.value)}
          placeholder="Escribe tu mensaje..."
          className="flex-grow border rounded px-3 py-1"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700">
          Enviar
        </button>
      </form>
    </div>
  );
}

export default Chat;
