import random
from datetime import datetime
from sqlalchemy import text
from seed_pos_data import engine

def registrar_venta_en_vivo():
    with engine.begin() as conn:
        productos = conn.execute(
            text("SELECT producto_id, descripcion, costo_actual, precio_unitario FROM pos_productos")
        ).fetchall()

        seleccion = random.sample(productos, k=random.randint(1, 3))
        ahora = datetime.now()

        res_venta = conn.execute(
            text("INSERT INTO pos_ventas (fecha_venta, sucursal_id, total_ticket) VALUES (:fecha, 'SUC-01', 0) RETURNING id_venta"),
            {"fecha": ahora}
        )
        id_venta = res_venta.scalar()

        total_ticket = 0
        lineas_generadas = 0
        for prod_id, desc, costo, precio in seleccion:
            cantidad = random.randint(1, 3)
            subtotal = round(float(precio) * cantidad, 2)
            total_ticket += subtotal
            lineas_generadas += 1

            conn.execute(
                text("""
                    INSERT INTO pos_ventas_detalle (id_venta, producto_id, cantidad_vendida, precio_unitario, costo_unitario, subtotal)
                    VALUES (:idv, :pid, :cant, :precio, :costo, :sub)
                """),
                {"idv": id_venta, "pid": prod_id, "cant": cantidad, "precio": precio, "costo": costo, "sub": subtotal}
            )
            conn.execute(
                text("UPDATE pos_inventario SET existencia_actual = GREATEST(existencia_actual - :cant, 0), fecha_actualizacion = :fecha WHERE producto_id = :pid"),
                {"cant": cantidad, "fecha": ahora, "pid": prod_id}
            )
            print(f"  + Vendido: {cantidad}x {desc} (${subtotal})")

        conn.execute(
            text("UPDATE pos_ventas SET total_ticket = :tot WHERE id_venta = :idv"),
            {"tot": total_ticket, "idv": id_venta}
        )
        print(f"Ticket #{id_venta} registrado en POS local ({lineas_generadas} líneas | Total: ${total_ticket:.2f}).")

if __name__ == "__main__":
    registrar_venta_en_vivo()