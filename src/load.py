import pandas as pd
from google.cloud import bigquery
from config import GCP_PROJECT_ID, BQ_DATASET_NAME
from database import get_bq_client, guardar_ultima_sincronizacion
from fallback import guardar_respaldo_encriptado, recuperar_respaldo_encriptado

def _cargar_tabla(client: bigquery.Client, df: pd.DataFrame, nombre_tabla: str, modo: str):
    if df.empty:
        return
    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_NAME}.{nombre_tabla}"
    job_config = bigquery.LoadJobConfig(write_disposition=modo)
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Tabla {nombre_tabla} actualizada ({len(df)} filas, modo: {modo}).")

def cargar_a_bigquery(dim_producto, dim_stock, dim_tiempo, fact_ventas, max_fecha_str):
    try:
        client = get_bq_client()

        respaldo = recuperar_respaldo_encriptado()
        if respaldo:
            print("Restaurando lote pendiente desde respaldo local encriptado...")
            cargar_a_bigquery(**respaldo)

        _cargar_tabla(client, dim_producto, "Dim_Producto", bigquery.WriteDisposition.WRITE_TRUNCATE)
        _cargar_tabla(client, dim_stock, "Dim_Stock", bigquery.WriteDisposition.WRITE_TRUNCATE)

        if not dim_tiempo.empty:
            table_tiempo = f"{GCP_PROJECT_ID}.{BQ_DATASET_NAME}.Dim_Tiempo"
            fechas_bq = client.query(f"SELECT fecha_id FROM `{table_tiempo}`").to_dataframe()
            nuevas_fechas = dim_tiempo[~dim_tiempo["fecha_id"].isin(fechas_bq["fecha_id"])]
            _cargar_tabla(client, nuevas_fechas, "Dim_Tiempo", bigquery.WriteDisposition.WRITE_APPEND)

        if not fact_ventas.empty:
            _cargar_tabla(client, fact_ventas, "Fact_Ventas", bigquery.WriteDisposition.WRITE_APPEND)
            if max_fecha_str:
                guardar_ultima_sincronizacion(max_fecha_str)

        print("Sincronización con Google BigQuery completada exitosamente.")

    except Exception as e:
        print(f"Error de conexión con Google BigQuery: {e}")
        guardar_respaldo_encriptado({
            "dim_producto": dim_producto,
            "dim_stock": dim_stock,
            "dim_tiempo": dim_tiempo,
            "fact_ventas": fact_ventas,
            "max_fecha_str": max_fecha_str
        })
        raise