-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema Gomeria
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema Gomeria
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Gomeria` ;
USE `Gomeria` ;

-- -----------------------------------------------------
-- Table `Gomeria`.`producto_servicio`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`producto_servicio` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`producto_servicio` (
  `idproducto_servicio` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NOT NULL,
  `tipo` VARCHAR(45) NOT NULL,
  `marca` VARCHAR(45) NULL,
  `medidas` VARCHAR(45) NULL,
  `imagen_producto` VARCHAR(45) NULL,
  `activo` TINYINT NOT NULL DEFAULT 1,
  `cantidad_actual` INT NOT NULL,
  `cantidad_minima` INT NULL,
  `precio` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`idproducto_servicio`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`proveedor`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`proveedor` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`proveedor` (
  `idproveedore` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(45) NOT NULL,
  `cuit` VARCHAR(20) NOT NULL,
  `direccion` VARCHAR(45) NULL,
  `mail` VARCHAR(45) NULL,
  `ciudad` VARCHAR(45) NULL,
  `activo` TINYINT NOT NULL DEFAULT 1,
  `telefono` VARCHAR(45) NULL,
  PRIMARY KEY (`idproveedore`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`compra`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`compra` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`compra` (
  `idcompra` INT NOT NULL AUTO_INCREMENT,
  `fecha` DATE NULL,
  `horas` TIME NULL,
  `forma_de_pago` VARCHAR(45) NOT NULL,
  `cantidad_total_comprada` INT NULL,
  `iva` DECIMAL NULL,
  `idproveedore` INT NOT NULL,
  `activo` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`idcompra`),
  INDEX `fk_compras_proveedores1_idx` (`idproveedore` ASC) VISIBLE,
  CONSTRAINT `fk_compras_proveedores1`
    FOREIGN KEY (`idproveedore`)
    REFERENCES `Gomeria`.`proveedor` (`idproveedore`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`item_compra`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`item_compra` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`item_compra` (
  `iditem_compracol` INT NOT NULL AUTO_INCREMENT,
  `idproducto_servicio` INT NOT NULL,
  `idcompra` INT NOT NULL,
  `precio_unitario` DECIMAL(10,2) NULL,
  `cantidad` INT NULL,
  PRIMARY KEY (`iditem_compracol`),
  INDEX `fk_productos_has_compras_compras1_idx` (`idcompra` ASC) VISIBLE,
  INDEX `fk_productos_has_compras_productos_idx` (`idproducto_servicio` ASC) VISIBLE,
  CONSTRAINT `fk_productos_has_compras_productos`
    FOREIGN KEY (`idproducto_servicio`)
    REFERENCES `Gomeria`.`producto_servicio` (`idproducto_servicio`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_productos_has_compras_compras1`
    FOREIGN KEY (`idcompra`)
    REFERENCES `Gomeria`.`compra` (`idcompra`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`cliente`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`cliente` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`cliente` (
  `idcliente` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(35) NOT NULL,
  `apellido` VARCHAR(15) NOT NULL,
  `cuit` VARCHAR(20) NOT NULL,
  `forma_de_contacto` VARCHAR(45) NOT NULL,
  `plazo_de_pago` INT NOT NULL,
  `deuda` DECIMAL(10,2) NOT NULL,
  `activo` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`idcliente`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`empleado`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`empleado` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`empleado` (
  `idempleado` INT NOT NULL AUTO_INCREMENT,
  `nombre_usuario` VARCHAR(45) NOT NULL,
  `mail` VARCHAR(45) NOT NULL,
  `contraseña` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(45) NOT NULL,
  `activo` TINYINT NOT NULL DEFAULT 1,
  `telefono` VARCHAR(45) NULL,
  PRIMARY KEY (`idempleado`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`venta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`venta` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`venta` (
  `idventa` INT NOT NULL,
  `numero_factura` INT NOT NULL,
  `fecha_emision_factura` DATETIME NOT NULL,
  `descuento` DECIMAL(10,2) NULL,
  `iva` DECIMAL NULL,
  `cantidad_total_productos` INT NULL,
  `idcliente` INT NOT NULL,
  `idempleado` INT NOT NULL,
  `activa` TINYINT NOT NULL,
  PRIMARY KEY (`idventa`),
  INDEX `fk_ventas_clientes1_idx` (`idcliente` ASC) VISIBLE,
  INDEX `fk_ventas_empleados1_idx` (`idempleado` ASC) VISIBLE,
  CONSTRAINT `fk_ventas_clientes1`
    FOREIGN KEY (`idcliente`)
    REFERENCES `Gomeria`.`cliente` (`idcliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_ventas_empleados1`
    FOREIGN KEY (`idempleado`)
    REFERENCES `Gomeria`.`empleado` (`idempleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`item_venta`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`item_venta` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`item_venta` (
  `id_item_venta` INT NOT NULL AUTO_INCREMENT,
  `idproducto_servicio` INT NOT NULL,
  `idventa` INT NOT NULL,
  `precio_unitario` DECIMAL(10,2) NOT NULL,
  `cantidad` INT NOT NULL,
  PRIMARY KEY (`id_item_venta`),
  INDEX `fk_productos_has_ventas_ventas1_idx` (`idventa` ASC) VISIBLE,
  INDEX `fk_productos_has_ventas_productos1_idx` (`idproducto_servicio` ASC) VISIBLE,
  CONSTRAINT `fk_productos_has_ventas_productos1`
    FOREIGN KEY (`idproducto_servicio`)
    REFERENCES `Gomeria`.`producto_servicio` (`idproducto_servicio`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_productos_has_ventas_ventas1`
    FOREIGN KEY (`idventa`)
    REFERENCES `Gomeria`.`venta` (`idventa`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `Gomeria`.`historial_pago`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Gomeria`.`historial_pago` ;

CREATE TABLE IF NOT EXISTS `Gomeria`.`historial_pago` (
  `idhistorial_pago` INT NOT NULL AUTO_INCREMENT,
  `fecha` DATE NULL,
  `hora` TIME NULL,
  `monto` DECIMAL(10,2) NULL,
  `forma_pago` VARCHAR(45) NULL,
  `codigo_pago` VARCHAR(45) NULL,
  `numero_comprobante` VARCHAR(45) NULL,
  `fecha_vencimiento` DATE NULL,
  `historial_pagos` VARCHAR(45) NULL,
  `idventa` INT NOT NULL,
  PRIMARY KEY (`idhistorial_pago`),
  INDEX `fk_historial_pago_venta1_idx` (`idventa` ASC) VISIBLE,
  CONSTRAINT `fk_historial_pago_venta1`
    FOREIGN KEY (`idventa`)
    REFERENCES `Gomeria`.`venta` (`idventa`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
