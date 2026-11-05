CREATE TABLE IF NOT EXISTS pos_productos (
    producto_id SERIAL PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    costo_actual NUMERIC(10, 2) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pos_inventario (
    stock_id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES pos_productos(producto_id),
    existencia_actual INT NOT NULL,
    stock_minimo INT NOT NULL,
    stock_maximo INT NOT NULL,
    ultima_fecha_reabastecimiento DATE NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pos_ventas (
    id_venta SERIAL PRIMARY KEY,
    fecha_venta TIMESTAMP NOT NULL,
    sucursal_id VARCHAR(20) DEFAULT 'SUC-01',
    total_ticket NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS pos_ventas_detalle (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INT REFERENCES pos_ventas(id_venta),
    producto_id INT REFERENCES pos_productos(producto_id),
    cantidad_vendida INT NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    costo_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);