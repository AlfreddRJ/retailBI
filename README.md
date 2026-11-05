# RetailBI: Plataforma de Modernización Analítica y Business Intelligence para PYMES

Solución automatizada de Extracción, Transformación y Carga (ETL) y Business Intelligence diseñada para comercios minoristas (papelerías, jugueterías y ferreterías) que operan con sistemas de Punto de Venta (POS) locales. El sistema extrae transacciones de forma incremental, las transforma a un esquema dimensional en estrella y las centraliza en Google BigQuery para alimentar tableros ejecutivos en Looker Studio.

## Arquitectura y Tecnologías

* **Capa Transaccional Local (On-Premise):** PostgreSQL 15 en contenedor Docker simulando la base de datos operativa del POS.
* **Motor ETL y Procesamiento:** Python 3.12 con Pandas, SQLAlchemy, PyArrow y Cryptography (Fernet).
* **Orquestación de Flujos:** Prefect (Servidor y Worker locales en Docker) con ejecución nocturna programada y políticas de reintentos.
* **Data Warehouse en la Nube:** Google BigQuery estructurado bajo modelo en estrella (`Fact_Ventas`, `Dim_Producto`, `Dim_Tiempo`, `Dim_Stock`) y vistas analíticas precalculadas.
* **Visualización Ejecutiva:** Google Looker Studio conectado en tiempo real a BigQuery.

## Estructura del Proyecto

```text
retailbi-pipeline/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── credentials/
│   └── gcp_service_account.json
├── pos_simulator/
│   ├── init_pos_db.sql
│   ├── seed_pos_data.py
│   └── simulate_new_sale.py
└── src/
    ├── config.py
    ├── database.py
    ├── extract.py
    ├── transform.py
    ├── load.py
    ├── fallback.py
    ├── init_bigquery.py
    ├── create_views.py
    └── main_flow.py
```
## Requisitos Previos

1. Docker Desktop instalado y en ejecución.
2. Python 3.10+ (opcional para ejecutar scripts de simulación desde terminal local).
3. Proyecto activo en Google Cloud Platform con la API de BigQuery habilitada y una llave de Cuenta de Servicio en formato JSON colocada en `credentials/gcp_service_account.json`.

---

## Manual de Instalación y Despliegue

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd retailbi-pipeline
   ```

2. **Configurar variables de entorno:**  
   Duplicar el archivo `.env.example` bajo el nombre `.env` y ajustar los parámetros de conexión local y el identificador del proyecto de Google Cloud.

3. **Levantar la infraestructura contenerizada:**
   ```bash
   docker compose up -d --build
   ```
   Esto despliega tres contenedores en red local:
   - `retailbi_pos_db`: Base de datos PostgreSQL del POS.
   - `retailbi_prefect_server`: Panel visual de Prefect disponible en `http://localhost:4200`.
   - `retailbi_etl_worker`: Contenedor de ingesta que registra y mantiene activo el despliegue nocturno.

4. **Poblar datos iniciales y crear esquema en BigQuery (solo la primera vez):**
   ```bash
   python pos_simulator/seed_pos_data.py
   python src/init_bigquery.py
   python src/main_flow.py
   python src/create_views.py
   ```

---

## Operación y Simulación de Ventas en Vivo

- **Ejecución programada:** El despliegue `despliegue-nocturno-retailbi` se ejecuta de forma desatendida todos los días a las 23:00 hrs.
- **Simulación de cobro en mostrador:** Para insertar un ticket nuevo y descontar existencias en el POS local, ejecutar:
  ```bash
  python pos_simulator/simulate_new_sale.py
  ```
- **Sincronización manual inmediata:** Ingresar a [http://localhost:4200](http://localhost:4200), abrir la sección **Deployments**, seleccionar `despliegue-nocturno-retailbi` y presionar **Quick run**.

---

## Guía de Interpretación para el Usuario Directivo (Looker Studio)

El tablero ejecutivo se divide en tres vistas interactivas con filtros por rango de fechas y categoría comercial:

1. **Panel Ejecutivo de Resumen de Ventas:** Presenta los indicadores globales de Ingresos Totales, Ticket Promedio y Utilidad Bruta, acompañados de una serie temporal que compara ingresos contra costos operativos.
2. **Matriz de Rotación e Inventario:** Muestra el desplazamiento de unidades por artículo y clasifica el catálogo mediante un semáforo automático en tres estados: *Alta rotación*, *Stock estancado* y *Riesgo de desabasto* (cuando la existencia actual es menor o igual al stock mínimo).
3. **Explorador de Categorías y Estacionalidad:** Desglosa la aportación porcentual de utilidad entre Juguetería y Papelería, permitiendo identificar picos de demanda en temporadas escolares y festivas.

---

## Autores

- **Alfredo Ramírez Jiménez:** Arquitectura de datos, pipeline ETL, contenedores Docker y Google BigQuery.
- **Adrián García López:** Diseño de tableros en Looker Studio, métricas de negocio, pruebas y documentación.