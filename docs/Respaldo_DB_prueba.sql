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
78d7f13c-ba6b-11f1-9a76-be97c8a213a1:1-70,
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
  PRIMARY KEY (`idcliente`),
  UNIQUE KEY `cuit_UNIQUE` (`cuit`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Consumidor','Final','0',0,'0','Rosario',NULL,1),(2,'Juan Carlos','Pérez','20-30123456-7',341555123,'juan.perez@email.com','Roldan',NULL,1),(3,'María Laura','González','27-32987654-8',341555234,'maria.gonzalez@email.com','Funes',NULL,1),(4,'Carlos','Rodríguez','20-28456789-3',341555345,'carlos.rodriguez@gmail.com','Carcaraña',NULL,1),(5,'Transportes','Roldán SRL','30-71123456-9',341555456,'contacto@transproldan.com','Venado Tuerto',NULL,1),(6,'Lucía','Fernández','27-35678901-2',341555567,'lucia.f@hotmail.com','Reconquista',NULL,1),(7,'Agropecuaria','El Sol SA','30-60987654-1',341555678,'compras@elsolagro.com','Rosario',NULL,1),(8,'Roberto','Gómez','20-22341678-4',341555789,'roberto.gomez@yahoo.com','Rosario',NULL,0),(9,'María Laura','González','27-32947654-8',341555234,'maria.gonzalez@email.com','Rosario',NULL,1),(10,'Carlos','Rodríguez','20-28426789-3',341555345,'carlos.rodriguez@gmail.com','Rosario',NULL,1),(11,'Transportes','Roldán SRL','30-71123416-9',341555456,'contacto@transproldan.com','Roldan',NULL,1),(12,'Lucía','Fernández','27-35978901-2',341555567,'lucia.f@hotmail.com','Funes',NULL,1),(13,'Agropecuaria','El Sol SA','30-60947654-1',341555678,'compras@elsolagro.com','Rosario',NULL,1),(14,'Roberto','Gómez','20-22345679-4',341555789,'roberto.gomez@yahoo.com','Reconquista',NULL,0);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `compra`
--

LOCK TABLES `compra` WRITE;
/*!40000 ALTER TABLE `compra` DISABLE KEYS */;
INSERT INTO `compra` VALUES (1,'2026-10-04','20:31:14',2,2,1,1),(7,'2026-10-14','15:51:23',5,2,0,1);
/*!40000 ALTER TABLE `compra` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`idempleado`),
  UNIQUE KEY `nombre_usuario_UNIQUE` (`nombre_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (1,'luci',NULL,'scrypt:32768:8:1$Y581GpTivPk2Nl65$91774a5ce183ee281de80ac66027b8bc26c9dc2feeff3b9208a1044c22d5cea21d08c1c2350903e577c02917527af824293a037624cfcad6bfcc5987160ac3ff','AD',1,NULL),(2,'diego','','scrypt:32768:8:1$5O8LCieIyNnwFAYV$d0277a7a81cbca62cb495b2c3c1c267b8dbd874faa9599b89a1b2adf88a36d6ee234e2cf7ca8ac4cbff432e73a6743926d99a38cafe54ed62f67a2d020af72e3','AD',1,''),(3,'l','','scrypt:32768:8:1$c8ygL5NBm2kt942C$14641527bf15f0f653a10f8934687bdb8ace5ec0c7b14f48fa14d8fa4dfffb832b0c9f9ada8a8a73f930cbab706f465261630644a3913a9c0462be1295e50458','Empleado',0,''),(4,'e','lu@gmail.com','scrypt:32768:8:1$jQ1JUaTZq0vHtmbR$beed6db02808c59aad3826e219b7e6cb1e60ebad94db26a0e5f95c1b7b864fe1fbc6609fa2404dd77f5ce1bb04c9a62761a1aea9f18efab3d05a8a50687e80e8','Empleado',1,'3416556449'),(5,'micha04','','scrypt:32768:8:1$aoBO4MiwwGXWDtbi$6869f4c46cb57ad4d9064c13337af36d65844f77617e90a5b3c502d3cf76d54cb5da78e7c91f9be27275ba9688451c3d1f2b3cce9aff5a7fed36a33156ba7d26','AD',1,''),(6,'Pacho','','scrypt:32768:8:1$Oc8DXdcYhVz6A9ur$7137e1a56af03db117cf272d3d0f930e0750b11d4709a1a39c1b6800c10eb68d6f5a1db9e5d099c499c937a81ffa5a9361446aad59a39677f3906074b29360b2','Empleado',1,''),(7,'Lu','','scrypt:32768:8:1$afYWv5jxLJT6L1DW$4ce7412beb2d9443bc847f3ece0c405dc911c4c7146d552fd6acec4e4a320105e166f25630115c8ecbc6ef7955f6707ef9b8fe1a99a48681a39e463c2fda39cf','Empleado',1,'');
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_pago_cliente`
--

LOCK TABLES `historial_pago_cliente` WRITE;
/*!40000 ALTER TABLE `historial_pago_cliente` DISABLE KEYS */;
INSERT INTO `historial_pago_cliente` VALUES (1,'2026-09-06','23:38:09',290000.00,1,NULL,NULL,NULL,NULL,NULL,5),(2,'2026-09-07','18:16:14',290000.00,1,NULL,NULL,NULL,NULL,NULL,6),(3,'2026-09-07','21:21:27',145000.00,1,NULL,NULL,NULL,NULL,NULL,7),(4,'2026-09-08','18:53:45',145000.00,1,NULL,NULL,NULL,NULL,NULL,8),(5,'2026-09-08','20:02:56',145000.00,5,NULL,NULL,NULL,NULL,NULL,9),(6,'2026-09-09','19:17:16',120000.00,2,NULL,NULL,NULL,NULL,NULL,10),(7,'2026-09-09','19:19:18',120800.00,4,NULL,NULL,NULL,NULL,NULL,11),(8,'2026-09-09','19:36:55',1600.00,1,NULL,NULL,NULL,NULL,NULL,12),(9,'2026-09-09','19:40:34',8000.00,5,NULL,NULL,NULL,NULL,NULL,13),(10,'2026-09-17','22:18:54',53600.00,2,NULL,NULL,NULL,NULL,NULL,14),(11,'2026-09-29','20:35:27',97500.00,1,NULL,NULL,NULL,NULL,NULL,15),(12,'2026-10-15','19:58:07',315000.00,1,NULL,NULL,NULL,NULL,0,16);
/*!40000 ALTER TABLE `historial_pago_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_compra`
--

DROP TABLE IF EXISTS `item_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_compra` (
  `iditem_compra` int NOT NULL AUTO_INCREMENT,
  `idproducto` int NOT NULL,
  `idcompra` int NOT NULL,
  `cantidad_pedida` int DEFAULT NULL COMMENT 'Al proveedor',
  `cantidad_entregada` int DEFAULT NULL COMMENT 'Por el proveedor',
  PRIMARY KEY (`iditem_compra`),
  KEY `fk_productos_has_compras_compras1_idx` (`idcompra`),
  KEY `fk_productos_has_compras_productos_idx` (`idproducto`),
  CONSTRAINT `fk_item_compra_producto` FOREIGN KEY (`idproducto`) REFERENCES `producto` (`idproducto`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_compra`
--

LOCK TABLES `item_compra` WRITE;
/*!40000 ALTER TABLE `item_compra` DISABLE KEYS */;
INSERT INTO `item_compra` VALUES (1,1,1,2,2),(2,28,7,5,1);
/*!40000 ALTER TABLE `item_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_venta`
--

DROP TABLE IF EXISTS `item_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_venta` (
  `id_item_venta` int NOT NULL AUTO_INCREMENT,
  `idproducto` int DEFAULT NULL,
  `idservicio` int DEFAULT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `cantidad` int NOT NULL,
  `idventa` int NOT NULL,
  PRIMARY KEY (`id_item_venta`),
  KEY `fk_productos_has_ventas_productos1_idx` (`idproducto`),
  KEY `fk_idventa_idx` (`idventa`),
  KEY `fk_item_venta_servicio` (`idservicio`),
  CONSTRAINT `fk_item_venta_producto` FOREIGN KEY (`idproducto`) REFERENCES `producto` (`idproducto`),
  CONSTRAINT `fk_item_venta_servicio` FOREIGN KEY (`idservicio`) REFERENCES `servicio` (`idservicio`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_venta`
--

LOCK TABLES `item_venta` WRITE;
/*!40000 ALTER TABLE `item_venta` DISABLE KEYS */;
INSERT INTO `item_venta` VALUES (1,1,NULL,145000.00,1,1),(2,1,NULL,145000.00,1,2),(3,1,NULL,145000.00,5,3),(4,1,NULL,145000.00,2,4),(5,1,NULL,145000.00,2,5),(6,1,NULL,145000.00,2,6),(7,1,NULL,145000.00,1,7),(8,1,NULL,145000.00,1,8),(9,1,NULL,145000.00,1,9),(10,11,NULL,800.00,2,10),(11,10,NULL,8200.00,2,10),(12,7,NULL,1500.00,2,10),(13,5,NULL,35000.00,2,10),(14,6,NULL,14500.00,2,10),(15,2,NULL,85000.00,1,11),(16,5,NULL,35000.00,1,11),(17,11,NULL,800.00,1,11),(18,11,NULL,800.00,2,12),(19,11,NULL,800.00,10,13),(20,6,NULL,14500.00,2,14),(21,10,NULL,8200.00,3,14),(22,3,NULL,12500.00,1,15),(23,2,NULL,85000.00,1,15),(24,1,NULL,145000.00,1,16),(25,2,NULL,85000.00,2,16);
/*!40000 ALTER TABLE `item_venta` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `metodos_pago`
--

LOCK TABLES `metodos_pago` WRITE;
/*!40000 ALTER TABLE `metodos_pago` DISABLE KEYS */;
INSERT INTO `metodos_pago` VALUES (1,'Efectivo',1),(2,'Transferencia',1),(3,'Tarjeta de Débito',1),(4,'Tarjeta de Crédito',1),(5,'Mercado Pago',1);
/*!40000 ALTER TABLE `metodos_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `idproducto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `idtipo` int NOT NULL,
  `marca` varchar(45) DEFAULT NULL,
  `medidas` varchar(45) DEFAULT NULL,
  `imagen_producto` varchar(255) DEFAULT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  `cantidad_actual` int NOT NULL,
  `cantidad_minima` int DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`idproducto`),
  UNIQUE KEY `uq_producto_unicidad` (`nombre`,`idtipo`,`marca`,`medidas`),
  KEY `fk_producto_tipos` (`idtipo`),
  CONSTRAINT `fk_producto_tipos` FOREIGN KEY (`idtipo`) REFERENCES `tipos` (`idtipo`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,'Neumático Michelin 205/55 R16',1,'Michelin','205/55 R16','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980629/Neumatico_Michelin.jpg',1,24,5,145000.00),(2,'Llanta Aleación',2,'EB Wheels','15 pulgadas','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980629/llanta_aleacion.jpg',1,10,4,85000.00),(3,'Kit Reparación Neumáticos',3,'Slime','Universal','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980628/kit_reparacion_neumaticos.jpg',1,24,5,12500.00),(4,'Manómetro Digital',4,'Bremen','0-150 PSI','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980627/manometro.jpg',1,15,3,18000.00),(5,'Compresor Aire Portátil 12V',4,'Lüsqtoff','12V / 150 PSI','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980626/compresor_aire_portatil_12v.jpg',1,8,2,35000.00),(6,'Llave de Cruz para Ruedas',4,'Bremen','17-19-21-23 mm','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980626/llave_cruz_ruedas.jpg',1,8,2,14500.00),(7,'Picos Rueda Sin Cámara',3,'Generic','TR414','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980626/picos_para_ruedas_sin_camaras.jpg',1,100,20,1500.00),(8,'Gato Hidráulico Carrito',4,'Bremen','2 Toneladas','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980624/gato_hidraulico_carrito.jpg',1,5,1,65000.00),(9,'Cámara de Aire Neumático',5,'Horng Chern','175/70 R13','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980624/camara_aire_para_neumaticos.jpg',1,30,8,9500.00),(10,'Aerosol Sellador Inflador',3,'Bardahl','450 ml','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980623/aerosol_sellador_e_inflador_neumaticos.jpg',1,37,10,8200.00),(11,'Contrapesas Adhesivas',3,'Vulcan','Tira 60g (5g/10g)','https://res.cloudinary.com/jmzlqhiv/image/upload/v1788980623/contrapesas_adhesivas_para_balanceo_ruedas.jpg',1,10,50,800.00),(12,'Pasta para Montaje de Neumáticos',3,'Slime','4 kg',NULL,1,15,3,22000.00),(15,'Llanta',2,'EB Wheels','15 pulgadas','',1,12,4,85000.00),(16,'Kit Reparación',3,'Slime','Universal','',1,25,5,12500.00),(17,'Manómetro',4,'Bremen','0-150 PSI','',1,15,3,18000.00),(18,'Compresor',4,'Lüsqtoff','12V / 150 PSI','',1,8,2,35000.00),(19,'Llave',4,'Bremen','17-19-21-23 mm','',1,10,2,14500.00),(20,'Picos Rueda',3,'Generic','TR414','',1,100,20,1500.00),(21,'Gato',4,'Bremen','2 Toneladas','',1,5,1,65000.00),(22,'Cámara',5,'Horng Chern','175/70 R13','',1,30,8,9500.00),(23,'Aerosol',3,'Bardahl','450 ml','',1,40,10,8200.00),(24,'Contrapesas',3,'Vulcan','Tira 60g (5g/10g)','',1,200,50,800.00),(28,'Moño',6,'','20','https://res.cloudinary.com/jmzlqhiv/image/upload/v1792009840/gomeria/nwqrnuhc1fwxrzesc21u.jpg',1,10,20,1500000.00),(29,'NS',7,'','','https://res.cloudinary.com/jmzlqhiv/image/upload/v1792009840/gomeria/nwqrnuhc1fwxrzesc21u.jpg',1,20,100,15.00);
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`idproveedor`),
  UNIQUE KEY `cuit_UNIQUE` (`cuit`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'luchis','46039626','Diaguitas 569','lucianogonzalez@gmail.com','roldan','(341) 6556449','General',0),(2,'lucho','46039726','Diaguitas 569','lucianogonzalez1274@gmail.com','Roldan','3416556449','Parasito',1),(3,'micha','2045654434','Lopez 1234','','Rosario','341435642','Insumos',1),(4,'lu','12232145556321','','','Rosario','','Insumos',1);
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio`
--

DROP TABLE IF EXISTS `servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio` (
  `idservicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `idtipo` int NOT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`idservicio`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  UNIQUE KEY `uq_servicio_unicidad` (`nombre`,`idtipo`),
  KEY `fk_servicio_tipos` (`idtipo`),
  CONSTRAINT `fk_servicio_tipos` FOREIGN KEY (`idtipo`) REFERENCES `tipos` (`idtipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio`
--

LOCK TABLES `servicio` WRITE;
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos`
--

DROP TABLE IF EXISTS `tipos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos` (
  `idtipo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `activo` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`idtipo`),
  UNIQUE KEY `uq_tipo_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos`
--

LOCK TABLES `tipos` WRITE;
/*!40000 ALTER TABLE `tipos` DISABLE KEYS */;
INSERT INTO `tipos` VALUES (1,'Neumático',1),(2,'Producto',1),(3,'Insumo',1),(4,'Herramienta',1),(5,'Repuesto',1),(6,'Aleatorio',1),(7,'NS',1);
/*!40000 ALTER TABLE `tipos` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
INSERT INTO `venta` VALUES (1,1,'2026-09-01 21:59:02',0.00,21,1,145000.00,NULL,1,1,1),(2,1,'2026-09-06 19:05:07',0.00,21,1,145000.00,NULL,1,1,1),(3,1,'2026-09-06 19:13:17',0.00,21,5,725000.00,NULL,1,1,1),(4,1,'2026-09-06 22:05:33',50002.00,21,2,239998.00,NULL,1,1,1),(5,1,'2026-09-06 23:38:08',0.00,21,2,290000.00,1,1,1,1),(6,1,'2026-09-07 18:16:14',0.00,21,2,290000.00,1,1,1,1),(7,1,'2026-09-07 21:21:26',0.00,21,1,145000.00,1,1,1,1),(8,1,'2026-09-08 18:53:44',0.00,21,1,145000.00,1,1,1,1),(9,1,'2026-09-08 20:02:56',0.00,21,1,145000.00,1,1,1,1),(10,1,'2026-09-09 19:17:13',0.00,21,10,120000.00,2,2,1,1),(11,1,'2026-09-09 19:19:16',0.00,21,3,120800.00,1,2,1,1),(12,1,'2026-09-09 19:36:54',0.00,21,2,1600.00,2,1,1,1),(13,1,'2026-09-09 19:40:34',0.00,21,10,8000.00,1,1,1,1),(14,1,'2026-09-17 22:18:54',0.00,21,5,53600.00,1,1,1,1),(15,1,'2026-09-29 20:35:27',0.00,21,2,97500.00,2,1,1,1),(16,1,'2026-10-15 19:58:06',0.00,21,3,315000.00,1,7,0,1);
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-16 19:32:46
