from google.cloud import bigquery
from config import GCP_PROJECT_ID, BQ_DATASET_NAME

def inicializar_data_warehouse():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    dataset_id = f"{GCP_PROJECT_ID}.{BQ_DATASET_NAME}"

    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset verificado/creado: {dataset_id}")

    esquemas = {
        "Dim_Producto": [
            bigquery.SchemaField("producto_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("codigo_barras", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("descripcion", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("categoria", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("marca", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("costo_actual", "FLOAT64", mode="REQUIRED"),
        ],
        "Dim_Tiempo": [
            bigquery.SchemaField("fecha_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("fecha_completa", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("dia", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("mes", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("anio", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("dia_semana", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("temporada", "STRING", mode="REQUIRED"),
        ],
        "Dim_Stock": [
            bigquery.SchemaField("stock_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("producto_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("existencia_actual", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("stock_minimo", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("stock_maximo", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("ultima_fecha_reabastecimiento", "DATE", mode="REQUIRED"),
        ],
        "Fact_Ventas": [
            bigquery.SchemaField("id_venta", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("fecha_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("producto_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sucursal_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("cantidad_vendida", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("precio_unitario", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("costo_unitario", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("total_venta", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("margen_bruto_calculado", "FLOAT64", mode="REQUIRED"),
        ],
    }

    for nombre_tabla, schema in esquemas.items():
        table_id = f"{dataset_id}.{nombre_tabla}"
        tabla = bigquery.Table(table_id, schema=schema)
        client.create_table(tabla, exists_ok=True)
        print(f"Tabla dimensional verificada/creada: {nombre_tabla}")

    print("Infraestructura analítica en Google BigQuery desplegada con éxito.")

if __name__ == "__main__":
    inicializar_data_warehouse()