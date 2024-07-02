DROP DATABASE IF EXISTS scraping_db;
CREATE DATABASE scraping_db;

USE scraping_db;


CREATE TABLE Supermercado (
    idSupermercado INT NOT NULL AUTO_INCREMENT,
    nombreSupermercado VARCHAR(45),
    PRIMARY KEY (idSupermercado)
);

CREATE TABLE Producto (
    idProducto INT NOT NULL AUTO_INCREMENT,
    nombreProducto VARCHAR(255),
    marcaProducto VARCHAR(255),
    formatoProducto VARCHAR(45),
    categoriaProducto VARCHAR(45),
    PRIMARY KEY (idProducto)
);

CREATE TABLE Precio (
    idPrecio INT NOT NULL AUTO_INCREMENT,
    idProducto INT NOT NULL,
    idSupermercado INT NOT NULL,
    Precio DECIMAL(10, 2) NOT NULL,
    fecha DATETIME NOT NULL,
    PRIMARY KEY (idPrecio),
    FOREIGN KEY (idProducto) REFERENCES Producto(idProducto),
    FOREIGN KEY (idSupermercado) REFERENCES Supermercado(idSupermercado)
);
-- Agregar datos iniciales
INSERT INTO Supermercado (nombreSupermercado) VALUES ('Jumbo');
INSERT INTO Supermercado (nombreSupermercado) VALUES ('Santa Isabel');
INSERT INTO Supermercado (nombreSupermercado) VALUES ('Acuenta');
INSERT INTO Supermercado (nombreSupermercado) VALUES ('Unimarc');
