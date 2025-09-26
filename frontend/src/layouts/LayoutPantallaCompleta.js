// src/layouts/LayoutPantallaCompleta.jsx
import React from "react";
import { Outlet } from "react-router-dom";

export default function LayoutPantallaCompleta() {
  return <Outlet />; // solo renderiza la página
}
