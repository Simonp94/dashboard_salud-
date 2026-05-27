import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURACION PAGINA
# =========================

st.set_page_config(
    page_title="Dashboard Facturación",
    layout="wide"
)

st.title("Dashboard Facturación Salud")

# =========================
# CARGA EXCEL
# =========================

archivo = "Libro5.xlsx"
@st.cache_data

def cargar_datos():
    df = pd.read_excel(archivo)

    # Convertir fecha
    df["FECHA RADICACION"] = pd.to_datetime(
        df["FECHA RADICACION"],
        errors="coerce"
    )

    return df


df = cargar_datos()

# =========================
# SIDEBAR FILTROS
# =========================

st.sidebar.header("Filtros")

proveedor = st.sidebar.multiselect(
    "Proveedor",
    options=sorted(df["nombre proveedor"].dropna().unique()),
    default=sorted(df["nombre proveedor"].dropna().unique())
)

estado = st.sidebar.multiselect(
    "Estado",
    options=sorted(df["estado"].dropna().unique()),
    default=sorted(df["estado"].dropna().unique())
)

# Aplicar filtros

df_filtrado = df[
    (df["nombre proveedor"].isin(proveedor)) &
    (df["estado"].isin(estado))
]

# =========================
# KPIs PRINCIPALES
# =========================

valor_total = df_filtrado["VALOR"].sum()

cantidad_facturas = df_filtrado["factura"].nunique()

cantidad_prestadores = df_filtrado["nombre proveedor"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Valor Total Pagado",
    f"${valor_total:,.0f}"
)

col2.metric(
    "Cantidad Facturas",
    f"{cantidad_facturas:,}"
)

col3.metric(
    "Cantidad Prestadores",
    f"{cantidad_prestadores:,}"
)

# =========================
# VALOR PAGADO POR PROVEEDOR
# =========================

st.subheader("Valor Pagado por Proveedor")

valor_proveedor = (
    df_filtrado
    .groupby("nombre proveedor", as_index=False)["VALOR"]
    .sum()
    .sort_values("VALOR", ascending=False)
)

fig_valor = px.bar(
    valor_proveedor,
    x="nombre proveedor",
    y="VALOR",
    text_auto='.2s',
    title="Valores Pagados por Institución"
)

fig_valor.update_layout(
    xaxis_title="Proveedor",
    yaxis_title="Valor"
)

st.plotly_chart(fig_valor, use_container_width=True)

# =========================
# FACTURAS POR PRESTADOR

st.subheader("Cantidad de Facturas por Prestador")

facturas_prestador = (
    df_filtrado
    .groupby("nombre proveedor", as_index=False)["factura"]
    .count()
    .rename(columns={"factura": "Cantidad Facturas"})
    .sort_values("Cantidad Facturas", ascending=False)
)

fig_facturas = px.bar(
    facturas_prestador,
    x="nombre proveedor",
    y="Cantidad Facturas",
    text_auto=True
)

st.plotly_chart(fig_facturas, use_container_width=True)

# =========================
# FACTURAS POR FECHA
# =========================

st.subheader("Cantidad de Facturas por Fecha de Radicación")

facturas_fecha = (
    df_filtrado
    .groupby("FECHA RADICACION", as_index=False)["factura"]
    .count()
    .rename(columns={"factura": "Cantidad Facturas"})
)

fig_fecha = px.line(
    facturas_fecha,
    x="FECHA RADICACION",
    y="Cantidad Facturas",
    markers=True
)

st.plotly_chart(fig_fecha, use_container_width=True)

# =========================
# TABLA DETALLE
# =========================

st.subheader("Detalle de Facturas")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=500
)

# =========================
# DESCARGA CSV
# =========================

csv = df_filtrado.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Descargar Información",
    data=csv,
    file_name="facturacion_filtrada.csv",
    mime="text/csv"
)
