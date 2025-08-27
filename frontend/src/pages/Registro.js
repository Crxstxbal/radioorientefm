import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

const Registro = ({ setUsuario }) => {
  const navigate = useNavigate();

  const [nombre, setNombre] = useState("");
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:3001/api/usuarios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre,
          usuario: nombreUsuario,
          correo,
          password,  // clave: debe ser password, no contrasena
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert("Error al registrar: " + (errorData.error || "Error desconocido"));
        return;
      }

      const data = await response.json();

      // Guardar usuario en localStorage y estado global
      localStorage.setItem("usuario", JSON.stringify(data));
      setUsuario(data);

      alert("Usuario registrado con éxito: " + data.usuario);

      // Redirigir a home
      navigate("/");
    } catch (error) {
      alert("Error en el servidor, intenta más tarde.");
      console.error(error);
    }
  };

  return (
    <motion.div
      className="max-w-xl mx-auto mt-24 p-8 bg-white dark:bg-gray-900 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold mb-6 text-purple-main dark:text-purple-light text-center">
        Regístrate en Radio Oriente
      </h2>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nombre completo"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="w-full px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-800 dark:text-white"
          required
        />
        <input
          type="text"
          placeholder="Nombre de usuario"
          value={nombreUsuario}
          onChange={(e) => setNombreUsuario(e.target.value)}
          className="w-full px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-800 dark:text-white"
          required
        />
        <input
          type="email"
          placeholder="Correo electrónico"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          className="w-full px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-800 dark:text-white"
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-800 dark:text-white"
          required
        />
        <button
          type="submit"
          className="w-full bg-purple-main text-white py-2 rounded-md hover:bg-purple-dark transition"
        >
          Registrarse
        </button>
      </form>
    </motion.div>
  );
};

export default Registro;
