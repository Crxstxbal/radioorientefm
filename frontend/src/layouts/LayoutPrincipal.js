// src/layouts/LayoutPrincipal.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import RadioPlayer from "../components/RadioPlayer";
import LiveChat from "../components/LiveChat";
import Footer from "../components/Footer";

export default function LayoutPrincipal() {
  return (
    <>
      <Navbar />
      <Outlet />
      <RadioPlayer />
      <LiveChat />
      <Footer />
    </>
  );
}
