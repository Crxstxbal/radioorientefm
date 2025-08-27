🎵 Radio Oriente
Sitio web oficial de Radio Oriente - Una experiencia radiofónica moderna y dinámica.
📋 Descripción del Proyecto
Radio Oriente es una plataforma web que ofrece streaming en vivo, programación, noticias y contenido multimedia para nuestra audiencia. Este proyecto incluye:

🎙️ Streaming en vivo
📻 Programación de radio
🗞️ Sección de noticias
👥 Sistema de usuarios
🎵 Reproductor de audio integrado
📱 Diseño responsive

🛠️ Tecnologías Utilizadas

Frontend: React.js / HTML5 / CSS3 / JavaScript
Backend: Node.js / Express
Base de Datos: PostgreSQL (Supabase)
Autenticación: Supabase Auth
Deployment: GitHub Pages / Netlify

🚀 Configuración Inicial para Desarrolladores
Prerrequisitos
Asegúrate de tener instalado:

Node.js (versión 16 o superior)
Git
Editor de código (recomendado: VS Code)

📦 Instalación

Clonar el repositorio:
bashgit clone https://github.com/tu-usuario/radio-oriente.git
cd radio-oriente

Instalar dependencias:
bashnpm install

Configurar variables de entorno:
bash# Crear archivo de configuración local
cp .env.example .env

Completar el archivo .env con las credenciales reales (solicítalas al administrador):
env# Base de datos Supabase
REACT_APP_SUPABASE_URL=https://yzrkskltrwhtwbqjowll.supabase.co
REACT_APP_SUPABASE_ANON_KEY=tu-anon-key-aqui

# Configuración de la radio
REACT_APP_RADIO_STREAM_URL=url-del-stream-aqui
REACT_APP_API_BASE_URL=https://api.radiooriente.com

# Servicios externos
REACT_APP_GOOGLE_MAPS_API_KEY=tu-google-maps-key
REACT_APP_YOUTUBE_API_KEY=tu-youtube-api-key

Iniciar el servidor de desarrollo:
bashnpm start

Abrir en el navegador: http://localhost:3000


