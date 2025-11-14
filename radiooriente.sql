-- Schema PostgreSQL ordenado por dependencias

-- Tablas sin dependencias (nivel 0)
CREATE TABLE public.pais (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL UNIQUE,
  CONSTRAINT pais_pkey PRIMARY KEY (id)
);

CREATE TABLE public.categoria (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  slug character varying NOT NULL UNIQUE,
  CONSTRAINT categoria_pkey PRIMARY KEY (id)
);

CREATE TABLE public.genero_musical (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  CONSTRAINT genero_musical_pkey PRIMARY KEY (id)
);

CREATE TABLE public.estado (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  descripcion text,
  tipo_entidad character varying NOT NULL,
  CONSTRAINT estado_pkey PRIMARY KEY (id)
);

CREATE TABLE public.tipo_asunto (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  CONSTRAINT tipo_asunto_pkey PRIMARY KEY (id)
);

CREATE TABLE public.conductor (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  apellido character varying NOT NULL,
  apodo character varying,
  email character varying UNIQUE,
  telefono character varying,
  activo boolean NOT NULL,
  foto character varying,
  CONSTRAINT conductor_pkey PRIMARY KEY (id)
);

CREATE TABLE public.estacion_radio (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  descripcion text,
  stream_url character varying,
  telefono character varying,
  email character varying,
  direccion text,
  listeners_count integer NOT NULL,
  activo boolean NOT NULL,
  CONSTRAINT estacion_radio_pkey PRIMARY KEY (id)
);

CREATE TABLE public.programa (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  descripcion text,
  imagen_url character varying,
  activo boolean NOT NULL,
  CONSTRAINT programa_pkey PRIMARY KEY (id)
);

CREATE TABLE public.integrante (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  CONSTRAINT integrante_pkey PRIMARY KEY (id)
);

CREATE TABLE public.filtro_contenido_config (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  activo boolean NOT NULL,
  umbral_toxicidad double precision NOT NULL,
  bloquear_enlaces boolean NOT NULL,
  modo_accion character varying NOT NULL,
  strikes_para_bloqueo integer NOT NULL,
  fecha_creacion timestamp with time zone NOT NULL,
  fecha_modificacion timestamp with time zone NOT NULL,
  CONSTRAINT filtro_contenido_config_pkey PRIMARY KEY (id)
);

CREATE TABLE public.palabras_prohibidas (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  palabra character varying NOT NULL UNIQUE,
  severidad character varying NOT NULL,
  activa boolean NOT NULL,
  fecha_creacion timestamp with time zone NOT NULL,
  CONSTRAINT palabras_prohibidas_pkey PRIMARY KEY (id)
);

CREATE TABLE public.publicidad_tipoubicacion (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  codigo character varying NOT NULL UNIQUE,
  nombre character varying NOT NULL,
  descripcion text,
  activo boolean NOT NULL,
  fecha_creacion timestamp with time zone NOT NULL,
  ultima_actualizacion timestamp with time zone NOT NULL,
  CONSTRAINT publicidad_tipoubicacion_pkey PRIMARY KEY (id)
);

CREATE TABLE public.auth_group (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL UNIQUE,
  CONSTRAINT auth_group_pkey PRIMARY KEY (id)
);

CREATE TABLE public.django_content_type (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  app_label character varying NOT NULL,
  model character varying NOT NULL,
  CONSTRAINT django_content_type_pkey PRIMARY KEY (id)
);

CREATE TABLE public.django_migrations (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  app character varying NOT NULL,
  name character varying NOT NULL,
  applied timestamp with time zone NOT NULL,
  CONSTRAINT django_migrations_pkey PRIMARY KEY (id)
);

CREATE TABLE public.django_session (
  session_key character varying NOT NULL,
  session_data text NOT NULL,
  expire_date timestamp with time zone NOT NULL,
  CONSTRAINT django_session_pkey PRIMARY KEY (session_key)
);

CREATE TABLE public.django_site (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  domain character varying NOT NULL UNIQUE,
  name character varying NOT NULL,
  CONSTRAINT django_site_pkey PRIMARY KEY (id)
);

CREATE TABLE public.publicidad (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre_cliente character varying NOT NULL,
  descripcion text,
  tipo character varying NOT NULL,
  fecha_inicio date NOT NULL,
  fecha_fin date NOT NULL,
  activo boolean NOT NULL,
  costo_total numeric,
  fecha_creacion timestamp with time zone NOT NULL,
  CONSTRAINT publicidad_pkey PRIMARY KEY (id)
);

-- Tablas que dependen de usuario (nivel 1)
CREATE TABLE public.usuario (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  password character varying NOT NULL,
  last_login timestamp with time zone,
  username character varying NOT NULL UNIQUE,
  email character varying NOT NULL UNIQUE,
  first_name character varying NOT NULL,
  last_name character varying NOT NULL,
  is_staff boolean NOT NULL,
  is_superuser boolean NOT NULL,
  fecha_creacion timestamp with time zone NOT NULL,
  chat_bloqueado boolean NOT NULL,
  CONSTRAINT usuario_pkey PRIMARY KEY (id)
);

-- Tablas nivel 2 (dependen de usuario y otras tablas base)
CREATE TABLE public.ciudad (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  pais_id bigint NOT NULL,
  CONSTRAINT ciudad_pkey PRIMARY KEY (id),
  CONSTRAINT ciudad_pais_id_13446634_fk_pais_id FOREIGN KEY (pais_id) REFERENCES public.pais(id)
);

CREATE TABLE public.auth_permission (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  name character varying NOT NULL,
  content_type_id integer NOT NULL,
  codename character varying NOT NULL,
  CONSTRAINT auth_permission_pkey PRIMARY KEY (id),
  CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id)
);

CREATE TABLE public.horario_programa (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  dia_semana integer NOT NULL,
  hora_inicio time without time zone NOT NULL,
  hora_fin time without time zone NOT NULL,
  activo boolean NOT NULL,
  programa_id bigint NOT NULL,
  CONSTRAINT horario_programa_pkey PRIMARY KEY (id),
  CONSTRAINT horario_programa_programa_id_b0b96042_fk_programa_id FOREIGN KEY (programa_id) REFERENCES public.programa(id)
);

CREATE TABLE public.programa_conductor (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  conductor_id bigint NOT NULL,
  programa_id bigint NOT NULL,
  CONSTRAINT programa_conductor_pkey PRIMARY KEY (id),
  CONSTRAINT programa_conductor_conductor_id_91ba4c63_fk_conductor_id FOREIGN KEY (conductor_id) REFERENCES public.conductor(id),
  CONSTRAINT programa_conductor_programa_id_b489efbc_fk_programa_id FOREIGN KEY (programa_id) REFERENCES public.programa(id)
);

CREATE TABLE public.ubicacion_publicidad_web (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL UNIQUE,
  descripcion text,
  dimensiones character varying NOT NULL,
  precio_mensual numeric NOT NULL,
  activo boolean NOT NULL,
  orden integer NOT NULL,
  tipo_id bigint NOT NULL,
  CONSTRAINT ubicacion_publicidad_web_pkey PRIMARY KEY (id),
  CONSTRAINT ubicacion_publicidad_tipo_id_12882f11_fk_publicida FOREIGN KEY (tipo_id) REFERENCES public.publicidad_tipoubicacion(id)
);

CREATE TABLE public.publicidad_radial (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  duracion integer NOT NULL,
  repeticiones_diarias integer NOT NULL,
  archivo_audio character varying NOT NULL,
  reproducciones integer NOT NULL,
  publicidad_id bigint NOT NULL UNIQUE,
  CONSTRAINT publicidad_radial_pkey PRIMARY KEY (id),
  CONSTRAINT publicidad_radial_publicidad_id_dc7686f1_fk_publicidad_id FOREIGN KEY (publicidad_id) REFERENCES public.publicidad(id)
);

CREATE TABLE public.publicidad_web (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  url_destino character varying NOT NULL,
  formato character varying NOT NULL,
  impresiones integer NOT NULL,
  clics integer NOT NULL,
  archivo_media character varying,
  publicidad_id bigint NOT NULL UNIQUE,
  CONSTRAINT publicidad_web_pkey PRIMARY KEY (id),
  CONSTRAINT publicidad_web_publicidad_id_5fdbd8e3_fk_publicidad_id FOREIGN KEY (publicidad_id) REFERENCES public.publicidad(id)
);

CREATE TABLE public.account_emailaddress (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  email character varying NOT NULL,
  verified boolean NOT NULL,
  is_primary boolean NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT account_emailaddress_pkey PRIMARY KEY (id),
  CONSTRAINT account_emailaddress_user_id_2c513194_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.authtoken_token (
  key character varying NOT NULL,
  created timestamp with time zone NOT NULL,
  user_id bigint NOT NULL UNIQUE,
  CONSTRAINT authtoken_token_pkey PRIMARY KEY (key),
  CONSTRAINT authtoken_token_user_id_35299eff_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.suscripcion (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  email character varying NOT NULL UNIQUE,
  nombre character varying NOT NULL,
  activa boolean NOT NULL,
  fecha_suscripcion timestamp with time zone NOT NULL,
  fecha_baja timestamp with time zone,
  token_unsuscribe character varying NOT NULL UNIQUE,
  usuario_id bigint NOT NULL,
  CONSTRAINT suscripcion_pkey PRIMARY KEY (id),
  CONSTRAINT suscripcion_usuario_id_11f43d2c_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.dashboard_notificacion (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  titulo character varying NOT NULL,
  mensaje text NOT NULL,
  tipo character varying NOT NULL,
  leida boolean NOT NULL,
  url character varying,
  fecha_creacion timestamp with time zone NOT NULL,
  usuario_id bigint NOT NULL,
  CONSTRAINT dashboard_notificacion_pkey PRIMARY KEY (id),
  CONSTRAINT dashboard_notificacion_usuario_id_e4418005_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.notifications_notification (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  tipo character varying NOT NULL,
  titulo character varying NOT NULL,
  mensaje text NOT NULL,
  leido boolean NOT NULL,
  fecha_creacion timestamp with time zone NOT NULL,
  enlace character varying,
  content_type character varying,
  object_id integer CHECK (object_id >= 0),
  usuario_id bigint NOT NULL,
  CONSTRAINT notifications_notification_pkey PRIMARY KEY (id),
  CONSTRAINT notifications_notification_usuario_id_46cf25ef_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.mensajes (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  contenido text NOT NULL,
  fecha_envio timestamp with time zone NOT NULL,
  usuario_nombre character varying,
  tipo character varying NOT NULL,
  sala character varying NOT NULL,
  id_usuario bigint NOT NULL,
  CONSTRAINT mensajes_pkey PRIMARY KEY (id),
  CONSTRAINT mensajes_id_usuario_64c6f5cf_fk_usuario_id FOREIGN KEY (id_usuario) REFERENCES public.usuario(id)
);

CREATE TABLE public.reproduccion_radio (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  fecha_reproduccion timestamp with time zone NOT NULL,
  estacion_id bigint NOT NULL,
  usuario_id bigint NOT NULL,
  CONSTRAINT reproduccion_radio_pkey PRIMARY KEY (id),
  CONSTRAINT reproduccion_radio_estacion_id_fbf17ede_fk_estacion_radio_id FOREIGN KEY (estacion_id) REFERENCES public.estacion_radio(id),
  CONSTRAINT reproduccion_radio_usuario_id_2a277dcc_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.articulo (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  titulo character varying NOT NULL,
  slug character varying NOT NULL UNIQUE,
  contenido text NOT NULL,
  resumen text,
  imagen_portada character varying,
  imagen_thumbnail character varying,
  imagen_url character varying,
  video_url character varying,
  archivo_adjunto character varying,
  publicado boolean NOT NULL,
  destacado boolean NOT NULL,
  fecha_publicacion timestamp with time zone,
  fecha_creacion timestamp with time zone NOT NULL,
  fecha_actualizacion timestamp with time zone NOT NULL,
  vistas integer NOT NULL CHECK (vistas >= 0),
  autor_id bigint NOT NULL,
  categoria_id bigint,
  CONSTRAINT articulo_pkey PRIMARY KEY (id),
  CONSTRAINT articulo_autor_id_9c422812_fk_usuario_id FOREIGN KEY (autor_id) REFERENCES public.usuario(id),
  CONSTRAINT articulo_categoria_id_ef79c0f0_fk_categoria_id FOREIGN KEY (categoria_id) REFERENCES public.categoria(id)
);

CREATE TABLE public.django_admin_log (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  action_time timestamp with time zone NOT NULL,
  object_id text,
  object_repr character varying NOT NULL,
  action_flag smallint NOT NULL CHECK (action_flag >= 0),
  change_message text NOT NULL,
  content_type_id integer,
  user_id bigint NOT NULL,
  CONSTRAINT django_admin_log_pkey PRIMARY KEY (id),
  CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id),
  CONSTRAINT django_admin_log_user_id_c564eba6_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.socialaccount_socialapp (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  provider character varying NOT NULL,
  name character varying NOT NULL,
  client_id character varying NOT NULL,
  secret character varying NOT NULL,
  key character varying NOT NULL,
  provider_id character varying NOT NULL,
  settings jsonb NOT NULL,
  CONSTRAINT socialaccount_socialapp_pkey PRIMARY KEY (id)
);

CREATE TABLE public.socialaccount_socialaccount (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  provider character varying NOT NULL,
  uid character varying NOT NULL,
  last_login timestamp with time zone NOT NULL,
  date_joined timestamp with time zone NOT NULL,
  extra_data jsonb NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT socialaccount_socialaccount_pkey PRIMARY KEY (id),
  CONSTRAINT socialaccount_socialaccount_user_id_8146e70c_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.usuario_groups (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  group_id integer NOT NULL,
  CONSTRAINT usuario_groups_pkey PRIMARY KEY (id),
  CONSTRAINT usuario_groups_user_id_bf125d45_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id),
  CONSTRAINT usuario_groups_group_id_c67c8651_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id)
);

CREATE TABLE public.usuario_user_permissions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT usuario_user_permissions_pkey PRIMARY KEY (id),
  CONSTRAINT usuario_user_permissions_user_id_96a81eab_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id),
  CONSTRAINT usuario_user_permiss_permission_id_a8893ce7_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id)
);

CREATE TABLE public.auth_group_permissions (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  group_id integer NOT NULL,
  permission_id integer NOT NULL,
  CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id),
  CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id),
  CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id)
);

-- Tablas nivel 3 (dependen de ciudad)
CREATE TABLE public.comuna (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  ciudad_id bigint NOT NULL,
  CONSTRAINT comuna_pkey PRIMARY KEY (id),
  CONSTRAINT comuna_ciudad_id_95ba3c03_fk_ciudad_id FOREIGN KEY (ciudad_id) REFERENCES public.ciudad(id)
);

CREATE TABLE public.account_emailconfirmation (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  created timestamp with time zone NOT NULL,
  sent timestamp with time zone,
  key character varying NOT NULL UNIQUE,
  email_address_id integer NOT NULL,
  CONSTRAINT account_emailconfirmation_pkey PRIMARY KEY (id),
  CONSTRAINT account_emailconfirm_email_address_id_5b7f8c58_fk_account_e FOREIGN KEY (email_address_id) REFERENCES public.account_emailaddress(id)
);

CREATE TABLE public.socialaccount_socialapp_sites (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  socialapp_id integer NOT NULL,
  site_id integer NOT NULL,
  CONSTRAINT socialaccount_socialapp_sites_pkey PRIMARY KEY (id),
  CONSTRAINT socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc FOREIGN KEY (socialapp_id) REFERENCES public.socialaccount_socialapp(id),
  CONSTRAINT socialaccount_social_site_id_2579dee5_fk_django_si FOREIGN KEY (site_id) REFERENCES public.django_site(id)
);

CREATE TABLE public.socialaccount_socialtoken (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  token text NOT NULL,
  token_secret text NOT NULL,
  expires_at timestamp with time zone,
  account_id integer NOT NULL,
  app_id integer,
  CONSTRAINT socialaccount_socialtoken_pkey PRIMARY KEY (id),
  CONSTRAINT socialaccount_social_account_id_951f210e_fk_socialacc FOREIGN KEY (account_id) REFERENCES public.socialaccount_socialaccount(id),
  CONSTRAINT socialaccount_social_app_id_636a42d7_fk_socialacc FOREIGN KEY (app_id) REFERENCES public.socialaccount_socialapp(id)
);

CREATE TABLE public.articulo_usuarios_que_vieron (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  articulo_id bigint NOT NULL,
  user_id bigint NOT NULL,
  CONSTRAINT articulo_usuarios_que_vieron_pkey PRIMARY KEY (id),
  CONSTRAINT articulo_usuarios_qu_articulo_id_fe3a10b9_fk_articulo_ FOREIGN KEY (articulo_id) REFERENCES public.articulo(id),
  CONSTRAINT articulo_usuarios_que_vieron_user_id_d08daa93_fk_usuario_id FOREIGN KEY (user_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.solicitud_publicidad_web (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre_contacto character varying NOT NULL,
  email_contacto character varying NOT NULL,
  telefono_contacto character varying,
  preferencia_contacto character varying NOT NULL,
  estado character varying NOT NULL,
  fecha_solicitud timestamp with time zone NOT NULL,
  fecha_actualizacion timestamp with time zone NOT NULL,
  fecha_inicio_solicitada date NOT NULL,
  fecha_fin_solicitada date NOT NULL,
  mensaje_usuario text,
  notas_admin text,
  motivo_rechazo text,
  costo_total_estimado numeric NOT NULL,
  usuario_id bigint NOT NULL,
  aprobado_por_id bigint,
  fecha_aprobacion timestamp with time zone,
  publicacion_id bigint UNIQUE,
  CONSTRAINT solicitud_publicidad_web_pkey PRIMARY KEY (id),
  CONSTRAINT solicitud_publicidad_web_aprobado_por_id_73d022b4_fk_usuario_id FOREIGN KEY (aprobado_por_id) REFERENCES public.usuario(id),
  CONSTRAINT solicitud_publicidad_publicacion_id_1ce0321e_fk_publicida FOREIGN KEY (publicacion_id) REFERENCES public.publicidad(id),
  CONSTRAINT solicitud_publicidad_web_usuario_id_e3775a1e_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

-- Tablas nivel 4 (dependen de comuna)
CREATE TABLE public.banda_emergente (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre_banda character varying NOT NULL,
  email_contacto character varying NOT NULL,
  telefono_contacto character varying,
  mensaje text NOT NULL,
  documento_presentacion character varying,
  fecha_envio timestamp with time zone NOT NULL,
  fecha_revision timestamp with time zone,
  comuna_id bigint,
  estado_id bigint NOT NULL,
  genero_id bigint NOT NULL,
  revisado_por_id bigint,
  usuario_id bigint,
  CONSTRAINT banda_emergente_pkey PRIMARY KEY (id),
  CONSTRAINT banda_emergente_comuna_id_e6a32326_fk_comuna_id FOREIGN KEY (comuna_id) REFERENCES public.comuna(id),
  CONSTRAINT banda_emergente_estado_id_bd20fecc_fk_estado_id FOREIGN KEY (estado_id) REFERENCES public.estado(id),
  CONSTRAINT banda_emergente_genero_id_6ab342b6_fk_genero_musical_id FOREIGN KEY (genero_id) REFERENCES public.genero_musical(id),
  CONSTRAINT banda_emergente_revisado_por_id_e7cd4b41_fk_usuario_id FOREIGN KEY (revisado_por_id) REFERENCES public.usuario(id),
  CONSTRAINT banda_emergente_usuario_id_b55af8ca_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id)
);

CREATE TABLE public.contacto (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre character varying NOT NULL,
  email character varying NOT NULL,
  telefono character varying,
  mensaje text NOT NULL,
  fecha_envio timestamp with time zone NOT NULL,
  fecha_respuesta timestamp with time zone,
  respondido_por_id bigint,
  usuario_id bigint NOT NULL,
  estado_id bigint NOT NULL,
  tipo_asunto_id bigint NOT NULL,
  CONSTRAINT contacto_pkey PRIMARY KEY (id),
  CONSTRAINT contacto_respondido_por_id_bcd922f7_fk_usuario_id FOREIGN KEY (respondido_por_id) REFERENCES public.usuario(id),
  CONSTRAINT contacto_usuario_id_12677780_fk_usuario_id FOREIGN KEY (usuario_id) REFERENCES public.usuario(id),
  CONSTRAINT contacto_estado_id_0e42e949_fk_estado_id FOREIGN KEY (estado_id) REFERENCES public.estado(id),
  CONSTRAINT contacto_tipo_asunto_id_b68d0b22_fk_tipo_asunto_id FOREIGN KEY (tipo_asunto_id) REFERENCES public.tipo_asunto(id)
);

CREATE TABLE public.item_solicitud_web (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  url_destino character varying NOT NULL,
  formato character varying NOT NULL,
  precio_acordado numeric NOT NULL,
  notas text,
  solicitud_id bigint NOT NULL,
  ubicacion_id bigint NOT NULL,
  CONSTRAINT item_solicitud_web_pkey PRIMARY KEY (id),
  CONSTRAINT item_solicitud_web_solicitud_id_72984053_fk_solicitud FOREIGN KEY (solicitud_id) REFERENCES public.solicitud_publicidad_web(id),
  CONSTRAINT item_solicitud_web_ubicacion_id_fba94940_fk_ubicacion FOREIGN KEY (ubicacion_id) REFERENCES public.ubicacion_publicidad_web(id)
);

-- Tablas nivel 5 (dependen de banda_emergente)
CREATE TABLE public.banda_integrante (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  banda_id bigint NOT NULL,
  integrante_id bigint NOT NULL,
  CONSTRAINT banda_integrante_pkey PRIMARY KEY (id),
  CONSTRAINT banda_integrante_banda_id_4891b693_fk_banda_emergente_id FOREIGN KEY (banda_id) REFERENCES public.banda_emergente(id),
  CONSTRAINT banda_integrante_integrante_id_fdbcea19_fk_integrante_id FOREIGN KEY (integrante_id) REFERENCES public.integrante(id)
);

CREATE TABLE public.banda_link (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  tipo character varying NOT NULL,
  url character varying NOT NULL,
  banda_id bigint NOT NULL,
  CONSTRAINT banda_link_pkey PRIMARY KEY (id),
  CONSTRAINT banda_link_banda_id_54e06a87_fk_banda_emergente_id FOREIGN KEY (banda_id) REFERENCES public.banda_emergente(id)
);

CREATE TABLE public.imagen_publicidad_web (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  imagen character varying NOT NULL,
  descripcion character varying,
  orden integer NOT NULL,
  fecha_subida timestamp with time zone NOT NULL,
  item_id bigint NOT NULL,
  CONSTRAINT imagen_publicidad_web_pkey PRIMARY KEY (id),
  CONSTRAINT imagen_publicidad_web_item_id_a5f7a80c_fk_item_solicitud_web_id FOREIGN KEY (item_id) REFERENCES public.item_solicitud_web(id)
);

CREATE TABLE public.infracciones_usuario (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  usuario_nombre character varying NOT NULL,
  mensaje_original text NOT NULL,
  tipo_infraccion character varying NOT NULL,
  score_toxicidad double precision,
  fecha_infraccion timestamp with time zone NOT NULL,
  accion_tomada character varying NOT NULL,
  id_usuario bigint NOT NULL,
  mensaje_id bigint,
  palabra_prohibida_id bigint,
  CONSTRAINT infracciones_usuario_pkey PRIMARY KEY (id),
  CONSTRAINT infracciones_usuario_mensaje_id_47cc69a9_fk_mensajes_id FOREIGN KEY (mensaje_id) REFERENCES public.mensajes(id),
  CONSTRAINT infracciones_usuario_id_usuario_9b096f1d_fk_usuario_id FOREIGN KEY (id_usuario) REFERENCES public.usuario(id),
  CONSTRAINT infracciones_usuario_palabra_prohibida_id_6f82e9d3_fk_palabras_ FOREIGN KEY (palabra_prohibida_id) REFERENCES public.palabras_prohibidas(id)
);

ALTER TABLE public.programa
ADD COLUMN estacion_id bigint NOT NULL,
ADD CONSTRAINT programa_estacion_id_fk
  FOREIGN KEY (estacion_id)
  REFERENCES public.estacion_radio(id);

