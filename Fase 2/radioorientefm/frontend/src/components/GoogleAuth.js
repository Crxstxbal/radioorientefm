import React, { useState } from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";
import axios from 'axios';

// Leemos el ID desde el archivo .env
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

// Utilidad para enmascarar correos (Fallback por si no hay nombre)
const maskEmail = (email) => {
    if (!email) return 'Usuario';
    const [name, domain] = email.split('@');
    return `${name.substring(0, 2)}***@${domain}`;
};

const GoogleAuth = () => {
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);

    // Maneja el éxito del login
    const handleLoginSuccess = async (credentialResponse) => {
        try {
            const { credential } = credentialResponse;
            
            // 1. Decodificamos el token
            const decodedUser = jwtDecode(credential);
            
            // 2. PRIVACIDAD: Determinamos qué mostrar (Nombre o Email censurado)
            const safeDisplayName = decodedUser.given_name || decodedUser.name || maskEmail(decodedUser.email);

            console.log("Iniciando sesión segura..."); 
            
            // 3. Validamos con el Backend
            const res = await axios.post('http://127.0.0.1:8000/api/radio/auth/google/', {
                token: credential
            });

            if (res.status === 200) {
                const { token } = res.data;
                
                // 4. GUARDADO DE SEGURIDAD (Tokens)
                localStorage.setItem('access_token', token); 
                localStorage.setItem('token', token);
                
                // 5. SUPER HACK DE PRIVACIDAD (Objeto de Usuario Falso)
                // Creamos un objeto de usuario donde el 'email' es en realidad el nombre.
                // Esto engaña a los contextos que leen JSON.parse(localStorage.getItem('user'))
                const fakeUserObject = {
                    email: safeDisplayName,      // <--- Aquí está el truco
                    username: safeDisplayName,
                    name: safeDisplayName,
                    first_name: safeDisplayName,
                    user_id: res.data.user_id,
                    pk: res.data.user_id,
                    avatar: decodedUser.picture
                };

                // Guardamos el objeto completo serializado
                localStorage.setItem('user', JSON.stringify(fakeUserObject));
                localStorage.setItem('currentUser', JSON.stringify(fakeUserObject));

                // También guardamos las claves sueltas por si acaso
                localStorage.setItem('user_name', safeDisplayName);
                localStorage.setItem('username', safeDisplayName);
                localStorage.setItem('email', safeDisplayName); // Sobrescribimos email suelto
                
                if (decodedUser.picture) {
                    localStorage.setItem('user_avatar', decodedUser.picture);
                }
                
                // 6. REDIRECCIÓN
                window.location.href = '/';
            }

        } catch (err) {
            console.error("Error de autenticación:", err);
            if (err.response) {
                setError(`Error: ${err.response.data.error || 'Fallo del servidor'}`);
            } else {
                setError("Error de conexión.");
            }
        }
    };

    const handleLoginError = () => {
        setError("Google rechazó el inicio de sesión.");
    };

    if (!GOOGLE_CLIENT_ID) return null;

    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div className="flex flex-col items-center">
                <GoogleLogin
                    onSuccess={handleLoginSuccess}
                    onError={handleLoginError}
                    theme="filled_black"
                    shape="pill"
                    text="signin_with"
                    locale="es"
                    size="medium"
                />
                
                {error && (
                    <p className="text-red-500 text-xs mt-2 bg-red-100 px-2 py-1 rounded border border-red-200">
                        {error}
                    </p>
                )}
            </div>
        </GoogleOAuthProvider>
    );
};

export default GoogleAuth;