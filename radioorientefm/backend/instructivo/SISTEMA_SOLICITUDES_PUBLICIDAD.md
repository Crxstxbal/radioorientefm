# Sistema de Solicitudes de Publicidad - Radio Oriente FM

## 📋 Resumen del Sistema

Sistema completo de solicitudes de publicidad con aprobación administrativa, diseñado para que los usuarios puedan solicitar espacios publicitarios sin implementar pagos en línea. El administrador revisa, aprueba/rechaza y contacta al usuario por teléfono, WhatsApp o correo.

---

## 🗂️ Estructura de Base de Datos

### Modelos Creados

#### 1. **UbicacionPublicidad** (`ubicacion_publicidad`)
Catálogo de las 4 ubicaciones disponibles para publicidad.

**Campos:**
- `nombre`: Nombre descriptivo de la ubicación
- `tipo`: Tipo de ubicación (choices: panel_izquierdo, panel_derecho, banner_superior_home, banner_articulos)
- `descripcion`: Descripción detallada
- `dimensiones`: Dimensiones en píxeles (ej: "728x90")
- `precio_mensual`: Precio mensual en decimal
- `activo`: Si está disponible para contratar
- `orden`: Orden de visualización en el catálogo

**Ubicaciones Predefinidas:**
1. **Panel Lateral Izquierdo** (160x600) - $199/mes
2. **Panel Lateral Derecho** (300x600) - $249/mes
3. **Banner Superior Home** (728x90) - $299/mes - Solo visible en Home, debajo del navbar
4. **Banner Debajo de Últimos Artículos** (970x250) - $349/mes

---

#### 2. **SolicitudPublicidad** (`solicitud_publicidad`)
Solicitud completa de publicidad (carrito del usuario).

**Campos principales:**
- `usuario`: FK a Usuario (quien solicita)
- `nombre_contacto`, `email_contacto`, `telefono_contacto`, `whatsapp_contacto`: Datos de contacto
- `estado`: Estado de la solicitud (choices: pendiente, en_revision, aprobada, rechazada, activa, finalizada)
- `fecha_solicitud`, `fecha_actualizacion`: Timestamps
- `fecha_inicio_solicitada`, `fecha_fin_solicitada`: Fechas deseadas de publicación
- `mensaje_usuario`: Mensaje/comentarios del usuario
- `notas_admin`: Notas internas del administrador
- `motivo_rechazo`: Razón si se rechaza
- `publicidad_aprobada`: FK a Publicidad (si se aprueba y activa)
- `costo_total_estimado`: Suma de todos los items

**Estados del flujo:**
1. **pendiente**: Recién creada por el usuario
2. **en_revision**: Admin está revisando
3. **aprobada**: Admin aprobó, pendiente de activación
4. **rechazada**: Admin rechazó la solicitud
5. **activa**: Publicidad publicándose actualmente
6. **finalizada**: Publicidad terminó su período

---

#### 3. **ItemSolicitud** (`item_solicitud`)
Cada ubicación seleccionada dentro de una solicitud.

**Campos:**
- `solicitud`: FK a SolicitudPublicidad
- `ubicacion`: FK a UbicacionPublicidad
- `url_destino`: URL a la que redirige al hacer clic
- `precio_acordado`: Precio específico (puede variar del catálogo)
- `notas`: Notas específicas del item

---

#### 4. **ImagenPublicidad** (`imagen_publicidad`)
Imágenes asociadas a cada item de solicitud.

**Campos:**
- `item`: FK a ItemSolicitud
- `imagen`: ImageField (se guarda en `publicidad/solicitudes/YYYY/MM/`)
- `descripcion`: Descripción de la imagen
- `orden`: Orden si hay múltiples imágenes
- `fecha_subida`: Timestamp

---

## 🔌 API Endpoints

### Base URL: `/api/publicidad/api/`

#### **Ubicaciones (Catálogo)**

**GET** `/ubicaciones/`
- Listar todas las ubicaciones activas
- Público (no requiere autenticación)
- Retorna: Lista de ubicaciones con precios y dimensiones

**GET** `/ubicaciones/{id}/`
- Detalle de una ubicación específica
- Público

---

#### **Solicitudes**

**GET** `/solicitudes/`
- Listar mis solicitudes (usuario autenticado)
- Requiere: Autenticación
- Retorna: Lista simplificada de solicitudes del usuario

**POST** `/solicitudes/`
- Crear nueva solicitud
- Requiere: Autenticación
- Body:
```json
{
  "nombre_contacto": "Juan Pérez",
  "email_contacto": "juan@example.com",
  "telefono_contacto": "+56912345678",
  "whatsapp_contacto": "+56912345678",
  "fecha_inicio_solicitada": "2025-01-01",
  "fecha_fin_solicitada": "2025-01-31",
  "mensaje_usuario": "Mensaje opcional",
  "items": [
    {
      "ubicacion": 1,
      "url_destino": "https://miempresa.com",
      "precio_acordado": "199.00",
      "notas": "Notas opcionales"
    }
  ]
}
```

**GET** `/solicitudes/{id}/`
- Ver detalle completo de una solicitud
- Requiere: Autenticación (solo propias solicitudes)

**PUT/PATCH** `/solicitudes/{id}/`
- Actualizar solicitud (solo si está pendiente)
- Requiere: Autenticación

**POST** `/solicitudes/{id}/subir_imagen/`
- Subir imagen para un item específico
- Requiere: Autenticación, Content-Type: multipart/form-data
- Body (FormData):
  - `item_id`: ID del item
  - `imagen`: Archivo de imagen
  - `descripcion`: (opcional)
  - `orden`: (opcional, default: 0)

**DELETE** `/solicitudes/{id}/eliminar_imagen/`
- Eliminar una imagen
- Requiere: Autenticación
- Body:
```json
{
  "imagen_id": 123
}
```

**GET** `/solicitudes/mis_solicitudes/`
- Endpoint alternativo para obtener solicitudes del usuario actual

---

## 🎨 Panel de Administración (Django Admin)

### Gestión de Ubicaciones
- Crear/editar/desactivar ubicaciones
- Cambiar precios y dimensiones
- Ordenar catálogo

### Gestión de Solicitudes
**Vista de lista:**
- Filtros: Estado, fecha de solicitud, fecha de inicio
- Búsqueda: Email, nombre, teléfono
- Badges de colores por estado
- Información de contacto visible (teléfono, WhatsApp)

**Acciones masivas:**
- ✅ Aprobar solicitudes seleccionadas
- ❌ Rechazar solicitudes seleccionadas
- 🔍 Marcar en revisión
- 🚀 Activar publicidad (solo aprobadas)

**Vista de detalle:**
- Información completa del solicitante
- Items con ubicaciones e imágenes (inline)
- Campos para notas del admin y motivo de rechazo
- Fechas solicitadas
- Costo total calculado

### Gestión de Items
- Ver items por solicitud
- Editar URL de destino y precios
- Gestionar imágenes con vista previa

### Gestión de Imágenes
- Vista previa de imágenes
- Organizar por orden
- Filtrar por fecha

---

## 🔄 Flujo de Trabajo Completo

### 1. **Usuario Frontend**
1. Navega a `/publicidad`
2. Ve el catálogo de 4 ubicaciones con precios
3. Selecciona ubicaciones (carrito)
4. Sube imágenes para cada ubicación
5. Completa formulario de contacto
6. Envía solicitud

### 2. **Sistema Backend**
1. Crea `SolicitudPublicidad` con estado `pendiente`
2. Crea `ItemSolicitud` por cada ubicación seleccionada
3. Asocia `ImagenPublicidad` a cada item
4. Calcula `costo_total_estimado`
5. Envía notificación al admin (opcional - implementar)

### 3. **Administrador Dashboard**
1. Ve nueva solicitud en admin
2. Revisa imágenes y detalles
3. Marca como `en_revision`
4. Contacta al usuario por:
   - Teléfono
   - WhatsApp
   - Email
5. Negocia términos finales
6. Aprueba o rechaza:
   - **Si aprueba**: Cambia a `aprobada`
   - **Si rechaza**: Cambia a `rechazada` + motivo
7. Si se aprueba y se confirma pago/acuerdo:
   - Crea `Publicidad` (modelo existente)
   - Crea `PublicidadWeb` con ubicaciones
   - Vincula `solicitud.publicidad_aprobada`
   - Cambia estado a `activa`

### 4. **Publicación en Frontend**
1. Sistema consulta `PublicidadWeb` con `activo=True`
2. Filtra por ubicación y fechas vigentes
3. Muestra publicidad en las 4 ubicaciones:
   - Paneles laterales (izq/der) - Visibles en Home
   - Banner superior - Debajo navbar en Home
   - Banner artículos - Debajo de últimos artículos en Home
4. Al hacer clic, redirige a `url_destino`
5. Registra impresiones y clics

---

## 📦 Instalación y Configuración

### 1. Aplicar Migraciones
```bash
cd backend
python manage.py migrate publicidad
```

### 2. Crear Ubicaciones Iniciales
```bash
python manage.py crear_ubicaciones_publicidad
```

### 3. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
```

### 4. Acceder al Admin
```
http://localhost:8000/admin/
```

---

## 🎯 Próximos Pasos

### Backend
- [ ] Implementar notificaciones por email al admin cuando hay nueva solicitud
- [ ] Implementar notificaciones al usuario cuando cambia el estado
- [ ] Crear endpoint para obtener publicidades activas por ubicación
- [ ] Implementar sistema de métricas (impresiones/clics)

### Frontend
- [ ] Crear componente de carrito de publicidad
- [ ] Implementar formulario de solicitud con subida de imágenes
- [ ] Crear vista de "Mis Solicitudes" para usuarios
- [ ] Implementar componentes de visualización de publicidad en Home:
  - Panel lateral izquierdo
  - Panel lateral derecho
  - Banner superior (debajo navbar)
  - Banner debajo de artículos
- [ ] Agregar tracking de clics e impresiones

---

## 📝 Notas Importantes

1. **Sin Pagos en Línea**: El sistema NO procesa pagos. Todo se coordina manualmente con el administrador.

2. **Contacto Manual**: El administrador debe contactar al usuario usando los datos proporcionados (teléfono, WhatsApp, email).

3. **Ubicaciones Fijas**: Solo hay 4 ubicaciones disponibles, todas visibles en el Home.

4. **Imágenes**: Las imágenes se guardan en `media/publicidad/solicitudes/YYYY/MM/`.

5. **Relación con Publicidad Existente**: Cuando se aprueba una solicitud, se crea un registro en el modelo `Publicidad` existente y se vincula.

6. **Estados**: El flujo de estados es lineal pero flexible:
   - pendiente → en_revision → aprobada → activa → finalizada
   - pendiente → en_revision → rechazada

---

## 🔐 Permisos

- **Ubicaciones**: Público (cualquiera puede ver el catálogo)
- **Solicitudes**: Solo usuarios autenticados
- **Mis Solicitudes**: Cada usuario solo ve sus propias solicitudes
- **Admin**: Solo staff/superusers pueden gestionar desde el dashboard

---

## 📊 Modelos Relacionados Existentes

El sistema se integra con:
- **Usuario** (`usuario`): Para identificar al solicitante
- **Publicidad** (`publicidad`): Se crea cuando se aprueba una solicitud
- **PublicidadWeb** (`publicidad_web`): Configuración específica de la publicidad web aprobada

---

## 🛠️ Tecnologías Utilizadas

- **Django 4.x**: Framework backend
- **Django REST Framework**: API REST
- **PostgreSQL**: Base de datos
- **Pillow**: Procesamiento de imágenes
- **React**: Frontend (a implementar)
