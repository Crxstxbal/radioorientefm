//src/diseños/diseñoprincipal.jsx
import React from "react";
import { Outlet, useLocation, Link } from "react-router-dom";
import { Radio } from "lucide-react";
import Navbar from "../components/Navbar";
import RadioPlayer from "../components/RadioPlayer";
import LiveChat from "../components/LiveChat";
import Footer from "../components/Footer";
import PublicidadCarousel from "../components/PublicidadCarousel";
import BarraProgresoLectura from "../components/BarraProgresoLectura";

export default function LayoutPrincipal() {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <>
      <Navbar />
      <BarraProgresoLectura />
      
      {/*panel izquierdo fijo 300x600*/}
      <PublicidadCarousel dimensiones="300x600" query="Izquierdo" position="left-fixed" autoPlayMs={7000} />
      {/*panel derecho fijo 300x600*/}
      <PublicidadCarousel dimensiones="300x600" query="Derecho" position="right-fixed" autoPlayMs={7000} />
      <Outlet />
      <RadioPlayer />
      <LiveChat />
      {/*banner inferior sobre el footer*/}
      <PublicidadCarousel dimensiones="1200x200" position="bottom" autoPlayMs={7000} />
      <Footer />
    </>
  );
}
