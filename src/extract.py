import pandas as pd
from sqlalchemy import text
from database import get_pos_engine, leer_ultima_sincronizacion

def extraer_datos_pos():
    engine = get_pos_engine()
    ultima_sync = leer_ultima_sincronizacion()
    print(f"Extrayendo transacciones posteriores a: {ultima_sync}")

    with engine.connect() as conn:
        df_productos = pd.read_sql(text("SELECT * FROM pos_productos"), conn)
        df_inventario = pd.read_sql(text("SELECT * FROM pos_inventario"), conn)

        query_ventas = text("""
            SELECT 
                v.id_venta,
                d.id_detalle,
                v.fecha_venta,
                v.sucursal_id,
                d.producto_id,
                d.cantidad_vendida,
                d.precio_unitario,
                d.costo_unitario,
                d.subtotal
            FROM pos_ventas v
            INNER JOIN pos_ventas_detalle d ON v.id_venta = d.id_venta
            WHERE v.fecha_venta > :ultima_sync
            ORDER BY v.fecha_venta ASC
        """)
        df_ventas = pd.read_sql(query_ventas, conn, params={"ultima_sync": ultima_sync})

    print(f"Registros extraídos -> Productos: {len(df_productos)} | Stock: {len(df_inventario)} | Líneas de venta nuevas: {len(df_ventas)}")
    return df_productos, df_inventario, df_ventas