# from extract import extraer_datos_pos
# from transform import transformar_a_esquema_estrella
# from load import cargar_a_bigquery

# def ejecutar_pipeline_retailbi():
#     print("--- Iniciando Pipeline ETL RetailBI ---")
#     df_prod, df_inv, df_ven = extraer_datos_pos()
#     dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha = transformar_a_esquema_estrella(
#         df_prod, df_inv, df_ven
#     )
#     cargar_a_bigquery(dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha)
#     print("--- Pipeline ETL Finalizado ---")

# if __name__ == "__main__":
#     ejecutar_pipeline_retailbi()


#Código refactorizado para Prefect
import sys
from prefect import flow, task
from extract import extraer_datos_pos
from transform import transformar_a_esquema_estrella
from load import cargar_a_bigquery

@task(
    name="1. Extracción Incremental POS",
    retries=2,
    retry_delay_seconds=15,
    log_prints=True
)
def tarea_extraccion():
    return extraer_datos_pos()

@task(
    name="2. Transformación y Esquema Estrella",
    log_prints=True
)
def tarea_transformacion(df_prod, df_inv, df_ven):
    return transformar_a_esquema_estrella(df_prod, df_inv, df_ven)

@task(
    name="3. Carga Incremental a BigQuery",
    retries=3,
    retry_delay_seconds=30,
    log_prints=True
)
def tarea_carga(dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha):
    cargar_a_bigquery(dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha)

@flow(
    name="RetailBI - Pipeline ETL",
    log_prints=True
)
def ejecutar_pipeline_retailbi():
    print("--- Iniciando Pipeline ETL RetailBI Orquestado con Prefect ---")
    df_prod, df_inv, df_ven = tarea_extraccion()
    dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha = tarea_transformacion(
        df_prod, df_inv, df_ven
    )
    tarea_carga(dim_prod, dim_stock, dim_tiempo, fact_ventas, max_fecha)
    print("--- Pipeline ETL Finalizado ---")

if __name__ == "__main__":
    if "--serve" in sys.argv:
        ejecutar_pipeline_retailbi.serve(
            name="despliegue-nocturno-retailbi",
            cron="0 22 * * *", # Ejecutar a las 22:00 horas todos los días
            tags=["retailbi", "produccion", "etl"]
        )
    else:
        ejecutar_pipeline_retailbi()