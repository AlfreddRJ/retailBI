import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POS_DB_USER", "postgres")
DB_PASS = os.getenv("POS_DB_PASSWORD", "admin_pos_123")
DB_HOST = os.getenv("POS_DB_HOST", "localhost")
DB_PORT = os.getenv("POS_DB_PORT", "5433")
DB_NAME = os.getenv("POS_DB_NAME", "pos_alfredos")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

PRODUCTOS = [
    ("750100010001", "Mochila Escolar Básica", "Papelería", "Norma", 180.00, 380.00, 45, 15, 100),
    ("750100010002", "Calculadora Científica", "Papelería", "Casio", 220.00, 350.00, 30, 10, 60),
    ("750100010003", "Resistol en Barra 40g", "Papelería", "Pritt", 12.00, 22.00, 120, 40, 200),
    ("750100010004", "Cuaderno Profesional 100h", "Papelería", "Scribe", 25.00, 45.00, 200, 50, 300),
    ("750100010005", "Paquete Lápices No. 2 (12pzas)", "Papelería", "Dixon", 32.00, 45.00, 85, 25, 150),
    ("750100010006", "Caja de Colores 24pzas", "Papelería", "Prismacolor", 95.00, 145.00, 60, 20, 120),
    ("750200020001", "Peluche Mediano", "Juguetería", "Mi Alegría", 110.00, 200.00, 18, 10, 50),
    ("750200020002", "Rompecabezas 500 pzs", "Juguetería", "Ravensburger", 140.00, 250.00, 12, 8, 40),
    ("750200020003", "Juego de Mesa Familiar", "Juguetería", "Hasbro", 210.00, 380.00, 8, 10, 45),
    ("750200020004", "Set de Bloques de Construcción", "Juguetería", "Lego", 320.00, 520.00, 14, 8, 35),
    ("750200020005", "Coche de Fricción", "Juguetería", "Hot Wheels", 45.00, 85.00, 5, 15, 80),
]

def poblar_pos():
    with engine.begin() as conn:
        existentes = conn.execute(text("SELECT COUNT(*) FROM pos_productos")).scalar()
        if existentes > 0:
            print("La base de datos ya contiene registros iniciales.")
            return

        mapa_productos = {}
        for cod, desc, cat, marca, costo, precio, stock, s_min, s_max in PRODUCTOS:
            res = conn.execute(
                text("""
                    INSERT INTO pos_productos (codigo_barras, descripcion, categoria, marca, costo_actual, precio_unitario)
                    VALUES (:cod, :desc, :cat, :marca, :costo, :precio)
                    RETURNING producto_id
                """),
                {"cod": cod, "desc": desc, "cat": cat, "marca": marca, "costo": costo, "precio": precio}
            )
            prod_id = res.scalar()
            mapa_productos[prod_id] = (cat, costo, precio)

            conn.execute(
                text("""
                    INSERT INTO pos_inventario (producto_id, existencia_actual, stock_minimo, stock_maximo, ultima_fecha_reabastecimiento)
                    VALUES (:pid, :stock, :smin, :smax, :fecha_reab)
                """),
                {
                    "pid": prod_id,
                    "stock": stock,
                    "smin": s_min,
                    "smax": s_max,
                    "fecha_reab": (datetime.now() - timedelta(days=random.randint(5, 45))).date()
                }
            )

        fecha_inicio = datetime.now() - timedelta(days=180)
        for dia in range(181):
            fecha_actual = fecha_inicio + timedelta(days=dia)
            num_tickets = random.randint(8, 20)
            if fecha_actual.month in [8, 12]:
                num_tickets = random.randint(20, 40)

            for _ in range(num_tickets):
                hora_venta = fecha_actual.replace(
                    hour=random.randint(9, 20),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                res_venta = conn.execute(
                    text("INSERT INTO pos_ventas (fecha_venta, sucursal_id, total_ticket) VALUES (:fecha, 'SUC-01', 0) RETURNING id_venta"),
                    {"fecha": hora_venta}
                )
                id_venta = res_venta.scalar()

                total_ticket = 0
                items_en_ticket = random.sample(list(mapa_productos.keys()), k=random.randint(1, 4))
                for pid in items_en_ticket:
                    cat, costo, precio = mapa_productos[pid]
                    peso_cantidad = [1, 2, 3, 4] if (fecha_actual.month == 8 and cat == "Papelería") else [1, 2]
                    cantidad = random.choice(peso_cantidad)
                    subtotal = round(cantidad * precio, 2)
                    total_ticket += subtotal

                    conn.execute(
                        text("""
                            INSERT INTO pos_ventas_detalle (id_venta, producto_id, cantidad_vendida, precio_unitario, costo_unitario, subtotal)
                            VALUES (:idv, :pid, :cant, :precio, :costo, :sub)
                        """),
                        {"idv": id_venta, "pid": pid, "cant": cantidad, "precio": precio, "costo": costo, "sub": subtotal}
                    )

                conn.execute(
                    text("UPDATE pos_ventas SET total_ticket = :tot WHERE id_venta = :idv"),
                    {"tot": total_ticket, "idv": id_venta}
                )

        print("Base de datos POS poblada exitosamente con catálogo e historial de 6 meses.")

if __name__ == "__main__":
    poblar_pos()