-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: gestion-sotck-2-lucianogonzalez1274-bc78.i.aivencloud.com    Database: Gomeria
-- ------------------------------------------------------
-- Server version	8.4.8

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '1b60d2d3-8f76-11f1-8541-e6f0651671a1:1-119,
6907ba4b-94bf-11f1-972d-1ef0a6ac4bea:1-97,
78d7f13c-ba6b-11f1-9a76-be97c8a213a1:1-42,
8aaee54c-7d5e-11f1-9f3d-5aed042dc655:1-48,
f122064f-7bea-11f1-ae00-c27b75c3b46a:1-71';

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `idcliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(35) DEFAULT NULL,
  `apellido` varchar(15) DEFAULT NULL,
  `cuit` varchar(20) NOT NULL,
  `numero_tel` int DEFAULT NULL,
  `mail` varchar(45) DEFAULT NULL,
  `ciudad` varchar(50) DEFAULT NULL,
  `direccion` varchar(60) DEFAULT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`idcliente`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `compra`
--

DROP TABLE IF EXISTS `compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compra` (
  `idcompra` int NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `horas` time DEFAULT NULL,
  `cantidad_total` int DEFAULT NULL,
  `idproveedor` int NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  `completo` tinyint NOT NULL DEFAULT '0' COMMENT 'Marca si el pedido ya fue entregado al local por parte del proveedor o no',
  PRIMARY KEY (`idcompra`),
  KEY `fk_compras_proveedores1_idx` (`idproveedor`),
  CONSTRAINT `fk_compras_proveedores1` FOREIGN KEY (`idproveedor`) REFERENCES `proveedor` (`idproveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `idempleado` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(45) NOT NULL,
  `mail` varchar(45) DEFAULT NULL,
  `contrasena` varchar(255) NOT NULL,
  `tipo` varchar(45) NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  `telefono` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idempleado`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historial_pago_cliente`
--

DROP TABLE IF EXISTS `historial_pago_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_pago_cliente` (
  `idhistorial_pago` int NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `idmetodos_pago` int NOT NULL,
  `codigo_pago` varchar(45) DEFAULT NULL,
  `numero_comprobante` varchar(45) DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `historial_pagos` varchar(45) DEFAULT NULL,
  `plazo_pago` int DEFAULT NULL,
  `idventa` int NOT NULL,
  PRIMARY KEY (`idhistorial_pago`),
  UNIQUE KEY `fecha_vencimiento_UNIQUE` (`fecha_vencimiento`),
  KEY `idventa_idx` (`idventa`),
  KEY `idmetodos_pago_idx` (`idmetodos_pago`),
  CONSTRAINT `idmetodos_pago` FOREIGN KEY (`idmetodos_pago`) REFERENCES `metodos_pago` (`idmetodos_pago`),
  CONSTRAINT `idventa` FOREIGN KEY (`idventa`) REFERENCES `venta` (`idventa`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `item_compra`
--

DROP TABLE IF EXISTS `item_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_compra` (
  `iditem_compra` int NOT NULL AUTO_INCREMENT,
  `idproducto_servicio` int NOT NULL,
  `idcompra` int NOT NULL,
  `cantidad_pedida` int DEFAULT NULL COMMENT 'Al proveedor',
  `cantidad_entregada` int DEFAULT NULL COMMENT 'Por el proveedor',
  PRIMARY KEY (`iditem_compra`),
  KEY `fk_productos_has_compras_compras1_idx` (`idcompra`),
  KEY `fk_productos_has_compras_productos_idx` (`idproducto_servicio`),
  CONSTRAINT `fk_productos_has_compras_compras1` FOREIGN KEY (`idcompra`) REFERENCES `compra` (`idcompra`),
  CONSTRAINT `fk_productos_has_compras_productos` FOREIGN KEY (`idproducto_servicio`) REFERENCES `producto_servicio` (`idproducto_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `item_venta`
--

DROP TABLE IF EXISTS `item_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_venta` (
  `id_item_venta` int NOT NULL AUTO_INCREMENT,
  `idproducto_servicio` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `cantidad` int NOT NULL,
  `idventa` int NOT NULL,
  PRIMARY KEY (`id_item_venta`),
  KEY `fk_productos_has_ventas_productos1_idx` (`idproducto_servicio`),
  KEY `fk_idventa_idx` (`idventa`),
  CONSTRAINT `fk_idventa` FOREIGN KEY (`idventa`) REFERENCES `venta` (`idventa`),
  CONSTRAINT `fk_productos_has_ventas_productos1` FOREIGN KEY (`idproducto_servicio`) REFERENCES `producto_servicio` (`idproducto_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `metodos_pago`
--

DROP TABLE IF EXISTS `metodos_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metodos_pago` (
  `idmetodos_pago` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`idmetodos_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `producto_servicio`
--

DROP TABLE IF EXISTS `producto_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_servicio` (
  `idproducto_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `tipo` varchar(45) NOT NULL,
  `marca` varchar(45) DEFAULT NULL,
  `medidas` varchar(45) DEFAULT NULL,
  `imagen_producto` varchar(255) DEFAULT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  `cantidad_actual` int NOT NULL,
  `cantidad_minima` int DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`idproducto_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `idproveedor` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `cuit` varchar(20) NOT NULL,
  `direccion` varchar(45) DEFAULT NULL,
  `mail` varchar(45) DEFAULT NULL,
  `ciudad` varchar(45) DEFAULT NULL,
  `telefono` varchar(45) DEFAULT NULL,
  `rubro` varchar(75) NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`idproveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta` (
  `idventa` int NOT NULL AUTO_INCREMENT,
  `numero_factura` int NOT NULL,
  `fecha_emision_factura` datetime NOT NULL,
  `descuento` decimal(10,2) DEFAULT NULL,
  `iva` decimal(10,0) DEFAULT NULL,
  `cantidad_total_productos` int DEFAULT NULL,
  `precio_total` decimal(10,2) NOT NULL,
  `idcliente` int DEFAULT NULL,
  `idempleado` int NOT NULL,
  `activa` tinyint NOT NULL DEFAULT '1' COMMENT 'Estado de la venta. Se utiliza para el "Borrado" logico de una venta, 1 es activo mientras que 0 es desactivado',
  `estado` tinyint NOT NULL DEFAULT '1' COMMENT 'Determina si una venta fue completada o está pendiente, 1 indica que es una venta que ya fue pagada en su totalidad, mientras que 0 indica que hay pagos pendientes',
  PRIMARY KEY (`idventa`),
  KEY `fk_ventas_clientes1_idx` (`idcliente`),
  KEY `fk_ventas_empleados1_idx` (`idempleado`),
  KEY `idx_activa_fecha` (`activa`,`fecha_emision_factura`),
  KEY `idx_cliente` (`idcliente`),
  CONSTRAINT `fk_ventas_clientes1` FOREIGN KEY (`idcliente`) REFERENCES `cliente` (`idcliente`),
  CONSTRAINT `fk_ventas_empleados1` FOREIGN KEY (`idempleado`) REFERENCES `empleado` (`idempleado`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-14 19:20:48
