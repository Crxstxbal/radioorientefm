import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import RadioPlayer from './components/RadioPlayer';
import LiveChat from './components/LiveChat';
import Home from './pages/Home';
import Programming from './pages/Programming';
import News from './pages/News';
import Contact from './pages/Contact';
import Subscription from './pages/Subscription';
import Blog from './pages/Blog';
import Login from './pages/Login';
import Register from './pages/Register';
import './App.css';

function App() {

  useEffect(() => {
    const originalTitle = document.title;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        document.title = "¡Vuelve a la mejor radio!";
      } else {
        document.title = originalTitle;
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/programacion" element={<Programming />} />
              <Route path="/noticias" element={<News />} />
              <Route path="/contacto" element={<Contact />} />
              <Route path="/suscripcion" element={<Subscription />} />
              <Route path="/blog" element={<Blog />} />
              <Route path="/login" element={<Login />} />
              <Route path="/registro" element={<Register />} />
            </Routes>
          </main>
          <RadioPlayer />
          <LiveChat />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#000',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
