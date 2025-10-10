-- auth_group definition

CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);


-- blog_articulos definition

CREATE TABLE "blog_articulos" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "titulo" varchar(200) NOT NULL, "contenido" text NOT NULL, "resumen" text NULL, "imagen_url" varchar(500) NULL, "autor_id" integer NULL, "autor_nombre" varchar(100) NULL, "categoria" varchar(50) NULL, "tags" varchar(500) NULL, "publicado" bool NOT NULL, "fecha_publicacion" datetime NOT NULL, "fecha_creacion" datetime NOT NULL, "fecha_actualizacion" datetime NOT NULL);


-- blog_comentarios definition

CREATE TABLE "blog_comentarios" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "articulo_id" integer NOT NULL, "autor_nombre" varchar(100) NOT NULL, "autor_correo" varchar(150) NULL, "contenido" text NOT NULL, "aprobado" bool NOT NULL, "fecha_creacion" datetime NOT NULL);


-- django_content_type definition

CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);

CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");


-- django_migrations definition

CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);


-- django_session definition

CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);

CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");


-- estacion_radio definition

CREATE TABLE "estacion_radio" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre" varchar(100) NOT NULL, "descripcion" text NULL, "stream_url" varchar(500) NULL, "telefono" varchar(20) NULL, "correo" varchar(150) NULL, "direccion" text NULL, "listeners_count" integer NOT NULL, "activa" bool NOT NULL, "fecha_creacion" datetime NOT NULL, "fecha_actualizacion" datetime NOT NULL);


-- formulario_contacto definition

CREATE TABLE "formulario_contacto" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre" varchar(100) NOT NULL, "correo" varchar(150) NOT NULL, "telefono" varchar(20) NOT NULL, "asunto" varchar(150) NOT NULL, "mensaje" text NOT NULL, "fecha_envio" datetime NOT NULL, "estado" varchar(20) NOT NULL);


-- mensajes definition

CREATE TABLE "mensajes" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "id_usuario" integer NOT NULL, "contenido" text NOT NULL, "fecha_envio" datetime NOT NULL, "usuario_nombre" varchar(100) NULL, "tipo" varchar(20) NOT NULL, "sala" varchar(50) NOT NULL);


-- noticias definition

CREATE TABLE "noticias" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "titulo" varchar(200) NOT NULL, "contenido" text NOT NULL, "resumen" text NULL, "imagen_url" varchar(500) NULL, "autor_id" integer NULL, "autor_nombre" varchar(100) NULL, "categoria" varchar(50) NULL, "destacada" bool NOT NULL, "publicada" bool NOT NULL, "fecha_publicacion" datetime NOT NULL, "fecha_creacion" datetime NOT NULL, "fecha_actualizacion" datetime NOT NULL);


-- programacion definition

CREATE TABLE "programacion" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre_programa" varchar(100) NOT NULL, "descripcion" text NULL, "conductor" varchar(100) NULL, "dia_semana" integer NOT NULL, "hora_inicio" time NOT NULL, "hora_fin" time NOT NULL, "activo" bool NOT NULL, "fecha_creacion" datetime NOT NULL, "fecha_actualizacion" datetime NOT NULL);


-- roles definition

CREATE TABLE "roles" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre" varchar(50) NOT NULL UNIQUE, "descripcion" text NULL);


-- suscripciones definition

CREATE TABLE "suscripciones" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "correo" varchar(150) NOT NULL UNIQUE, "nombre" varchar(100) NOT NULL, "activa" bool NOT NULL, "fecha_suscripcion" datetime NOT NULL, "token_unsuscribe" varchar(100) NULL UNIQUE);


-- auth_permission definition

CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);

CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");


-- usuarios definition

CREATE TABLE "usuarios" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "nombre" text NOT NULL, "usuario" text NOT NULL UNIQUE, "correo" text NOT NULL UNIQUE, "fecha_creacion" datetime NOT NULL, "first_name" varchar(50) NULL, "last_name" varchar(50) NULL, "is_active" bool NOT NULL, "is_staff" bool NOT NULL, "rol_id_id" bigint NULL REFERENCES "roles" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE INDEX "usuarios_rol_id_id_2908e64b" ON "usuarios" ("rol_id_id");


-- usuarios_groups definition

CREATE TABLE "usuarios_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "usuarios" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE UNIQUE INDEX "usuarios_groups_user_id_group_id_7afcf963_uniq" ON "usuarios_groups" ("user_id", "group_id");
CREATE INDEX "usuarios_groups_user_id_2e7c7c45" ON "usuarios_groups" ("user_id");
CREATE INDEX "usuarios_groups_group_id_18c61092" ON "usuarios_groups" ("group_id");


-- usuarios_user_permissions definition

CREATE TABLE "usuarios_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "usuarios" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE UNIQUE INDEX "usuarios_user_permissions_user_id_permission_id_4166b112_uniq" ON "usuarios_user_permissions" ("user_id", "permission_id");
CREATE INDEX "usuarios_user_permissions_user_id_f5777c78" ON "usuarios_user_permissions" ("user_id");
CREATE INDEX "usuarios_user_permissions_permission_id_af615ca1" ON "usuarios_user_permissions" ("permission_id");


-- auth_group_permissions definition

CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");


-- authtoken_token definition

CREATE TABLE "authtoken_token" ("key" varchar(40) NOT NULL PRIMARY KEY, "created" datetime NOT NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "usuarios" ("id") DEFERRABLE INITIALLY DEFERRED);


-- bandas_emergentes definition

CREATE TABLE "bandas_emergentes" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nombre_banda" varchar(150) NOT NULL, "integrantes" text NULL, "genero" varchar(50) NOT NULL, "ciudad" varchar(100) NULL, "correo_contacto" varchar(254) NOT NULL, "telefono_contacto" varchar(20) NULL, "mensaje" text NOT NULL, "links" text NULL, "press_kit" varchar(100) NULL, "fecha_envio" datetime NOT NULL, "estado" varchar(10) NOT NULL, "usuario_id" bigint NULL REFERENCES "usuarios" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE INDEX "bandas_emergentes_usuario_id_bc1ee245" ON "bandas_emergentes" ("usuario_id");


-- django_admin_log definition

CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "usuarios" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);

CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");