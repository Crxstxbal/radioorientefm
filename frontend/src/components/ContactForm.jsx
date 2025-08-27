import React, { useState } from "react";

const ContactForm = () => {
  const [formData, setFormData] = useState({
    nombre: "",
    correo: "",
    telefono: "",
    asunto: "",
    mensaje: "",
  });

  const [mensajeEnviado, setMensajeEnviado] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
    setMensajeEnviado("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.nombre || !formData.correo || !formData.mensaje) {
      setError("Por favor completa los campos obligatorios.");
      return;
    }

    try {
      const res = await fetch("http://localhost:3001/api/contacto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setMensajeEnviado("¡Mensaje enviado con éxito! 🥳");
        setFormData({
          nombre: "",
          correo: "",
          telefono: "",
          asunto: "",
          mensaje: "",
        });
      } else {
        setError("Ocurrió un error al enviar el mensaje.");
      }
    } catch (err) {
      console.error(err);
      setError("Error de conexión con el servidor.");
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          name="nombre"
          value={formData.nombre}
          onChange={handleChange}
          placeholder="Tu nombre"
          className="w-full p-2 border rounded-md"
          required
        />
        <input
          name="correo"
          type="email"
          value={formData.correo}
          onChange={handleChange}
          placeholder="Correo electrónico"
          className="w-full p-2 border rounded-md"
          required
        />
        <input
          name="telefono"
          value={formData.telefono}
          onChange={handleChange}
          placeholder="Teléfono (opcional)"
          className="w-full p-2 border rounded-md"
        />
        <input
          name="asunto"
          value={formData.asunto}
          onChange={handleChange}
          placeholder="Asunto (opcional)"
          className="w-full p-2 border rounded-md"
        />
        <textarea
          name="mensaje"
          value={formData.mensaje}
          onChange={handleChange}
          placeholder="Escribe tu mensaje..."
          className="w-full p-2 border rounded-md h-32"
          required
        />

        {error && <p className="text-red-500 text-sm">{error}</p>}
        {mensajeEnviado && <p className="text-green-600 text-sm">{mensajeEnviado}</p>}

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-all"
        >
          Enviar mensaje
        </button>
      </form>
    </div>
  );
};

export default ContactForm;
