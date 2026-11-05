import pandas as pd

DIAS_SEMANA = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo"
}

def clasificar_temporada(mes: int) -> str:
    if mes in [8, 9]:
        return "Escolar"
    if mes in [11, 12, 1]:
        return "Festividades"
    return "Normal"

def transformar_a_esquema_estrella(df_productos: pd.DataFrame, df_inventario: pd.DataFrame, df_ventas: pd.DataFrame):
    dim_producto = pd.DataFrame({
        "producto_id": df_productos["producto_id"].astype(str),
        "codigo_barras": df_productos["codigo_barras"].astype(str).str.strip(),
        "descripcion": df_productos["descripcion"].astype(str).str.strip(),
        "categoria": df_productos["categoria"].astype(str).str.strip().str.title(),
        "marca": df_productos["marca"].astype(str).str.strip().str.title(),
        "costo_actual": df_productos["costo_actual"].astype(float).round(2)
    }).drop_duplicates(subset=["producto_id"])

    dim_stock = pd.DataFrame({
        "stock_id": df_inventario["stock_id"].astype(str),
        "producto_id": df_inventario["producto_id"].astype(str),
        "existencia_actual": df_inventario["existencia_actual"].fillna(0).astype("int64"),
        "stock_minimo": df_inventario["stock_minimo"].fillna(0).astype("int64"),
        "stock_maximo": df_inventario["stock_maximo"].fillna(0).astype("int64"),
        "ultima_fecha_reabastecimiento": pd.to_datetime(df_inventario["ultima_fecha_reabastecimiento"]).dt.date
    }).drop_duplicates(subset=["stock_id"])

    if df_ventas.empty:
        return dim_producto, dim_stock, pd.DataFrame(), pd.DataFrame(), None

    df_ventas = df_ventas.dropna(subset=["id_venta", "producto_id", "fecha_venta"]).copy()
    fechas_ts = pd.to_datetime(df_ventas["fecha_venta"])
    max_fecha_str = fechas_ts.max().strftime("%Y-%m-%d %H:%M:%S.%f")

    fechas_unicas = pd.Series(fechas_ts.dt.date.unique())
    fechas_dt = pd.to_datetime(fechas_unicas)

    dim_tiempo = pd.DataFrame({
        "fecha_id": fechas_dt.dt.strftime("%Y%m%d"),
        "fecha_completa": fechas_dt.dt.date,
        "dia": fechas_dt.dt.day.astype("int64"),
        "mes": fechas_dt.dt.month.astype("int64"),
        "anio": fechas_dt.dt.year.astype("int64"),
        "dia_semana": fechas_dt.dt.dayofweek.map(DIAS_SEMANA),
        "temporada": fechas_dt.dt.month.map(clasificar_temporada)
    }).drop_duplicates(subset=["fecha_id"])

    cantidad = df_ventas["cantidad_vendida"].astype("int64")
    precio = df_ventas["precio_unitario"].astype(float).round(2)
    costo = df_ventas["costo_unitario"].astype(float).round(2)
    total_venta = (cantidad * precio).round(2)
    margen_bruto = ((precio - costo) * cantidad).round(2)

    fact_ventas = pd.DataFrame({
        "id_venta": df_ventas["id_venta"].astype(str) + "-" + df_ventas["id_detalle"].astype(str),
        "fecha_id": fechas_ts.dt.strftime("%Y%m%d"),
        "producto_id": df_ventas["producto_id"].astype(str),
        "sucursal_id": df_ventas["sucursal_id"].fillna("SUC-01").astype(str),
        "cantidad_vendida": cantidad,
        "precio_unitario": precio,
        "costo_unitario": costo,
        "total_venta": total_venta,
        "margen_bruto_calculado": margen_bruto
    }).drop_duplicates(subset=["id_venta"])

    return dim_producto, dim_stock, dim_tiempo, fact_ventas, max_fecha_str