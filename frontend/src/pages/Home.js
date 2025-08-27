// ========== src/pages/Home.js ==========
import React from "react";

const Home = () => (
  <section className="bg-gradient-to-br from-light-purple-bg to-light-purple-bg dark:from-dark-purple-bg dark:to-dark-purple-bg py-16 px-4 text-center">
    <h1 className="text-4xl md:text-5xl font-bold text-purple-main dark:text-purple-light mb-4">
      Bienvenido a Radio Oriente
    </h1>
    <p className="text-lg text-purple-dark dark:text-purple-light mb-6 max-w-2xl mx-auto">
      Tu espacio digital de música, cultura, y vibras auténticas. Descubre programas, noticias y contenido con identidad.
    </p>
    <a href="#programas" className="inline-block px-6 py-3 bg-purple-main hover:bg-purple-dark text-white font-semibold rounded-lg transition">
      🎧 Explorar Programas
    </a>
  </section>
);

export default Home;
