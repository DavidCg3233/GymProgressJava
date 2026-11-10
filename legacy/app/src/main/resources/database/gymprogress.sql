-- ========================================
-- BASE DE DATOS: GymProgress
-- Autor: David Fernando Calambas Gómez
-- Descripción: Modelo relacional normalizado (3FN)
-- ========================================

CREATE DATABASE IF NOT EXISTS gymprogress;
USE gymprogress;

-- ========================================
-- TABLA: SEXO
-- ========================================
CREATE TABLE sexo (
                      codigo_sexo INT AUTO_INCREMENT PRIMARY KEY,
                      nombre_sexo VARCHAR(20) NOT NULL
) ENGINE=InnoDB;

-- =Añadir datos por defecto a SEXO
INSERT INTO `sexo` (`codigo_sexo`, `nombre_sexo`) VALUES (1, 'Masculino'), (2, 'Femenino');

-- ========================================
-- TABLA: USUARIO
-- ========================================
CREATE TABLE usuario (
                         codigo_usuario INT AUTO_INCREMENT PRIMARY KEY,
                         nombre_usuario VARCHAR(50) NOT NULL,
                         email VARCHAR(100) NOT NULL UNIQUE,
                         fecha_creacion DATE NOT NULL,
                         contrasena VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- ========================================
-- TABLA: CLIENTE (relación 1:1 con USUARIO)
-- ========================================
CREATE TABLE cliente (
                         codigo_usuario INT PRIMARY KEY,
                         primer_nombre VARCHAR(50) NOT NULL,
                         segundo_nombre VARCHAR(50),
                         primer_apellido VARCHAR(50) NOT NULL,
                         segundo_apellido VARCHAR(50),
                         codigo_sexo INT NOT NULL,
                         fecha_nacimiento DATE NOT NULL,
                         FOREIGN KEY (codigo_usuario) REFERENCES usuario(codigo_usuario)
                             ON DELETE CASCADE
                             ON UPDATE CASCADE,
                         FOREIGN KEY (codigo_sexo) REFERENCES sexo(codigo_sexo)
                             ON DELETE RESTRICT
                             ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: EJERCICIO
-- ========================================
CREATE TABLE ejercicio (
                           codigo_ejercicio INT AUTO_INCREMENT PRIMARY KEY,
                           nombre VARCHAR(50) NOT NULL,
                           grupo_muscular VARCHAR(50) NOT NULL,
                           descripcion TEXT
) ENGINE=InnoDB;

-- ========================================
-- TABLA: RUTINA
-- ========================================
CREATE TABLE rutina (
                        codigo_rutina INT AUTO_INCREMENT PRIMARY KEY,
                        codigo_usuario INT NOT NULL,
                        nombre_rutina VARCHAR(50) NOT NULL,
                        descripcion TEXT,
                        fecha_creacion DATE NOT NULL,
                        FOREIGN KEY (codigo_usuario) REFERENCES usuario(codigo_usuario)
                            ON DELETE CASCADE
                            ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: RUTINA_EJERCICIO (relación N:N)
-- ========================================
CREATE TABLE rutina_ejercicio (
                                  codigo_rutina_ejercicio INT AUTO_INCREMENT PRIMARY KEY,
                                  codigo_rutina INT NOT NULL,
                                  codigo_ejercicio INT NOT NULL,
                                  series INT NOT NULL,
                                  repeticiones INT NOT NULL,
                                  peso DECIMAL(5,2),
                                  FOREIGN KEY (codigo_rutina) REFERENCES rutina(codigo_rutina)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE,
                                  FOREIGN KEY (codigo_ejercicio) REFERENCES ejercicio(codigo_ejercicio)
                                      ON DELETE CASCADE
                                      ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: PROGRESO
-- ========================================
CREATE TABLE progreso (
                          codigo_progreso INT AUTO_INCREMENT PRIMARY KEY,
                          codigo_usuario INT NOT NULL,
                          fecha DATE NOT NULL,
                          peso_corporal DECIMAL(5,2) NOT NULL,
                          altura DECIMAL(5,2) NOT NULL,
                          notas TEXT,
                          FOREIGN KEY (codigo_usuario) REFERENCES usuario(codigo_usuario)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: TIPO_REPORTE
-- ========================================
CREATE TABLE tipo_reporte (
                              codigo_tipo_reporte INT AUTO_INCREMENT PRIMARY KEY,
                              nombre_tipo_reporte VARCHAR(20) NOT NULL
) ENGINE=InnoDB;

-- ========================================
-- TABLA: REPORTE
-- ========================================
CREATE TABLE reporte (
                         codigo_reporte INT AUTO_INCREMENT PRIMARY KEY,
                         codigo_usuario INT NOT NULL,
                         codigo_tipo_reporte INT NOT NULL,
                         fecha_generacion DATE NOT NULL,
                         descripcion TEXT,
                         FOREIGN KEY (codigo_usuario) REFERENCES usuario(codigo_usuario)
                             ON DELETE CASCADE
                             ON UPDATE CASCADE,
                         FOREIGN KEY (codigo_tipo_reporte) REFERENCES tipo_reporte(codigo_tipo_reporte)
                             ON DELETE RESTRICT
                             ON UPDATE CASCADE
) ENGINE=InnoDB;
ALTER TABLE rutina
ADD COLUMN dia_semana VARCHAR(20) NULL;

-- ========================================
-- NUEVA COLUMNA: peso_objetivo (Cliente)
-- ========================================
-- Agrega un peso objetivo opcional por usuario para objetivos de pérdida/ganancia
ALTER TABLE cliente
ADD COLUMN peso_objetivo DECIMAL(5,2) NULL AFTER fecha_nacimiento;
