from config import GCP_PROJECT_ID, BQ_DATASET_NAME
from database import get_bq_client

def configurar_vistas_analiticas():
    client = get_bq_client()
    dataset_ref = f"{GCP_PROJECT_ID}.{BQ_DATASET_NAME}"

    query_dedup = f"""
    CREATE OR REPLACE TABLE `{dataset_ref}.Fact_Ventas` AS
    SELECT DISTINCT * FROM `{dataset_ref}.Fact_Ventas`;
    """
    client.query(query_dedup).result()
    print("Tabla Fact_Ventas optimizada sin duplicados.")

    query_vista_ventas = f"""
    CREATE OR REPLACE VIEW `{dataset_ref}.vw_ventas_completas` AS
    SELECT
        v.id_venta,
        SPLIT(v.id_venta, '-')[OFFSET(0)] AS id_ticket,
        v.fecha_id,
        t.fecha_completa,
        t.anio,
        t.mes,
        t.dia,
        t.dia_semana,
        t.temporada,
        v.sucursal_id,
        v.producto_id,
        p.codigo_barras,
        p.descripcion AS producto,
        p.categoria,
        p.marca,
        v.cantidad_vendida,
        v.precio_unitario,
        v.costo_unitario,
        v.total_venta AS ingresos_totales,
        (v.cantidad_vendida * v.costo_unitario) AS costo_total,
        v.margen_bruto_calculado AS utilidad_bruta
    FROM `{dataset_ref}.Fact_Ventas` v
    LEFT JOIN `{dataset_ref}.Dim_Producto` p ON v.producto_id = p.producto_id
    LEFT JOIN `{dataset_ref}.Dim_Tiempo` t ON v.fecha_id = t.fecha_id;
    """
    client.query(query_vista_ventas).result()
    print("Vista analítica creada: vw_ventas_completas")

    query_vista_inventario = f"""
    CREATE OR REPLACE VIEW `{dataset_ref}.vw_estado_inventario` AS
    WITH ventas_por_producto AS (
        SELECT
            producto_id,
            SUM(cantidad_vendida) AS unidades_vendidas,
            SUM(total_venta) AS ingresos_acumulados,
            SUM(margen_bruto_calculado) AS margen_bruto_acumulado
        FROM `{dataset_ref}.Fact_Ventas`
        GROUP BY producto_id
    )
    SELECT
        s.stock_id,
        s.producto_id,
        p.codigo_barras,
        p.descripcion AS producto,
        p.categoria,
        p.marca,
        p.costo_actual,
        s.existencia_actual,
        s.stock_minimo,
        s.stock_maximo,
        s.ultima_fecha_reabastecimiento,
        COALESCE(vp.unidades_vendidas, 0) AS cantidad_vendida_historica,
        COALESCE(vp.ingresos_acumulados, 0) AS ingresos_acumulados,
        COALESCE(vp.margen_bruto_acumulado, 0) AS margen_bruto,
        CASE
            WHEN s.existencia_actual <= s.stock_minimo THEN 'Riesgo de desabasto'
            WHEN COALESCE(vp.unidades_vendidas, 0) >= 1000 THEN 'Alta rotación'
            ELSE 'Stock estancado'
        END AS semaforo_rotacion
    FROM `{dataset_ref}.Dim_Stock` s
    INNER JOIN `{dataset_ref}.Dim_Producto` p ON s.producto_id = p.producto_id
    LEFT JOIN ventas_por_producto vp ON s.producto_id = vp.producto_id;
    """
    client.query(query_vista_inventario).result()
    print("Vista analítica creada: vw_estado_inventario")

if __name__ == "__main__":
    configurar_vistas_analiticas()