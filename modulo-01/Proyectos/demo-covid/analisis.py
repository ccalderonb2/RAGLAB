"""Análisis reproducible de casos positivos de COVID-19 en Boyacá.

Ejecutar desde la raíz del repositorio:
    python modulo-01/proyectos/demo-covid/analisis.py

Lee el CSV indicado en datos/casos_covid.csv. Si todavía no existe, usa como
alternativa el CSV local de origen en modulo-01/Proyectos, sin copiarlo.
Genera un tablero HTML y dos PNG dentro de docs/proyectos/demo-covid/.
"""

from __future__ import annotations

import html
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


RAIZ = Path(__file__).resolve().parents[3]
RUTA_SOLICITADA = Path(__file__).resolve().parent / "datos" / "casos_covid.csv"
RUTA_ORIGEN = (
    RAIZ
    / "modulo-01"
    / "Proyectos"
    / "Casos_positivos_de_COVID-19_en_Colombia._20261110.csv"
)
RUTA_TABLERO = RAIZ / "docs" / "proyectos" / "demo-covid" / "index.html"
RUTA_GRAFICOS = RUTA_TABLERO.parent / "graficos"
FUENTE = (
    "https://www.datos.gov.co/Salud-y-Protecci-n-Social/"
    "Casos-positivos-de-COVID-19-en-Colombia-/gt2j-8ykr/about_data"
)
DEPARTAMENTO = "BOYACA"


def normalizar_nombre(valor: object) -> str:
    """Normaliza acentos/caja para comparar encabezados y categorías."""
    texto = unicodedata.normalize("NFKD", str(valor))
    return "".join(c for c in texto if not unicodedata.combining(c)).strip().casefold()


def leer_csv(ruta: Path) -> pd.DataFrame:
    """Prueba codificaciones comunes y falla con un mensaje comprensible."""
    errores: list[str] = []
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(ruta, encoding=encoding, low_memory=False)
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            errores.append(f"{encoding}: {exc}")
    raise RuntimeError("No se pudo leer el CSV. " + " | ".join(errores))


def buscar_columna(df: pd.DataFrame, nombre: str) -> str:
    objetivo = normalizar_nombre(nombre)
    for columna in df.columns:
        if normalizar_nombre(columna) == objetivo:
            return str(columna)
    raise ValueError(
        f"Falta la columna requerida {nombre!r}. Columnas disponibles: "
        + ", ".join(map(str, df.columns))
    )


def construir_tablero() -> None:
    if RUTA_SOLICITADA.exists():
        ruta_csv = RUTA_SOLICITADA
    elif RUTA_ORIGEN.exists():
        ruta_csv = RUTA_ORIGEN
        print(
            "Aviso: no existe datos/casos_covid.csv; se leerá el CSV de origen "
            f"sin copiarlo: {ruta_csv}"
        )
    else:
        raise FileNotFoundError(
            "No se encontró el CSV de entrada. Colócalo en "
            f"{RUTA_SOLICITADA} o proporciona el CSV local esperado en {RUTA_ORIGEN}."
        )

    df = leer_csv(ruta_csv)
    col_departamento = buscar_columna(df, "Nombre departamento")
    col_fecha = buscar_columna(df, "fecha reporte web")
    col_id = buscar_columna(df, "ID de caso")
    col_sexo = buscar_columna(df, "Sexo")

    # Valores ISO (YYYY-MM-DD); no aplicar dayfirst para evitar interpretar
    # ambiguamente fechas que ya vienen en formato año-mes-día.
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce", dayfirst=False)
    fechas_invalidas = int(df[col_fecha].isna().sum())
    seleccion = df[
        df[col_departamento].astype("string").map(normalizar_nombre).eq("boyaca")
    ].copy()
    seleccion = seleccion.dropna(subset=[col_fecha, col_id])
    seleccion[col_id] = seleccion[col_id].astype("string").str.strip()
    seleccion = seleccion[seleccion[col_id].ne("")]

    duplicados_id = int(seleccion[col_id].duplicated(keep=False).sum())
    # Un caso repetido se asigna al primer reporte web válido para evitar contar
    # varias veces el mismo ID o distribuirlo en distintos meses.
    casos = seleccion.sort_values(col_fecha).drop_duplicates(col_id, keep="first")
    casos["mes"] = casos[col_fecha].dt.to_period("M")
    mensual = casos.groupby("mes").size().sort_index()
    if mensual.empty:
        raise ValueError(
            "No hay casos de Boyacá con fecha de reporte e ID de caso válidos; "
            "no se puede generar un análisis mensual."
        )

    meses = pd.period_range(mensual.index.min(), mensual.index.max(), freq="M")
    mensual = mensual.reindex(meses, fill_value=0)
    sexo = (
        casos[col_sexo]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
        .fillna("Sin dato")
        .value_counts()
        .sort_values(ascending=False)
    )
    total = int(mensual.sum())
    pico_mes = mensual.idxmax()
    pico_casos = int(mensual.max())
    periodo = f"{mensual.index.min()} a {mensual.index.max()}"

    RUTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(11, 5.2))
    plt.plot(mensual.index.astype(str), mensual.values, marker="o", linewidth=2)
    plt.title("Casos reportados por mes — Boyacá")
    plt.xlabel("Mes de fecha de reporte web")
    plt.ylabel("Casos (ID únicos)")
    plt.xticks(rotation=55, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICOS / "casos-mensuales.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5.2))
    sexo.sort_values().plot.barh(color="#2b7a78")
    plt.title("Casos reportados por sexo — Boyacá")
    plt.xlabel("Casos (ID únicos)")
    plt.ylabel("Sexo (incluye faltantes)")
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICOS / "casos-por-sexo.png", dpi=150)
    plt.close()

    cambio = mensual.pct_change() * 100
    cambio_valido = cambio.replace([float("inf"), -float("inf")], pd.NA).dropna()
    if not cambio_valido.empty:
        mayor_cambio = cambio_valido.abs().idxmax()
        hallazgo = (
            f"El mes con más casos fue {pico_mes} ({pico_casos}). La mayor "
            f"variación porcentual mensual en valor absoluto ocurrió en "
            f"{mayor_cambio} ({cambio_valido.loc[mayor_cambio]:+.1f}%)."
        )
    else:
        hallazgo = f"El mes con más casos fue {pico_mes} ({pico_casos}). No hay dos meses comparables para calcular variación porcentual."

    indicadores = [
        ("Casos únicos en el periodo", f"{total:,}"),
        ("Mes pico", f"{pico_mes}: {pico_casos:,} casos"),
    ]
    tarjetas = "\n".join(
        f'<article class="card"><span>{html.escape(titulo)}</span>'
        f'<strong>{html.escape(valor)}</strong></article>'
        for titulo, valor in indicadores
    )
    advertencias = [
        "El conteo usa IDs de caso únicos; si un ID aparece repetido, se asigna al primer mes con fecha de reporte válida.",
        f"Se excluyeron {fechas_invalidas:,} filas del archivo con fecha de reporte vacía o inválida, además de registros sin ID válido o sin fecha tras filtrar Boyacá.",
        f"Se detectaron {duplicados_id:,} filas de Boyacá implicadas en IDs repetidos antes de deduplicar.",
        "La fecha usada es fecha reporte web (publicación en el sitio web), no fecha de diagnóstico ni fecha de inicio de síntomas.",
        "Los reportes pueden tener retrasos, correcciones y cambios en la vigilancia/pruebas; los conteos no equivalen necesariamente a incidencia real.",
        "La descripción del portal advierte incertidumbre epidemiológica y actualizaciones/correcciones de la publicación.",
        "Los meses sin registros válidos se muestran como cero; esto no demuestra ausencia real de casos.",
    ]
    lista_limitaciones = "\n".join(f"<li>{html.escape(x)}</li>" for x in advertencias)
    fuente = html.escape(FUENTE, quote=True)
    html_final = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>COVID-19 en Boyacá — análisis mensual</title>
<style>
body{{font:16px/1.6 system-ui,sans-serif;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#203333;background:#f5f8f7}}h1,h2{{color:#164e50}}.cards{{display:flex;gap:1rem;flex-wrap:wrap}}.card{{background:white;border-radius:10px;padding:1rem 1.3rem;box-shadow:0 2px 12px #153b3b18;min-width:220px}}.card span,.card strong{{display:block}}.card strong{{font-size:1.4rem;margin-top:.4rem}}figure{{background:white;padding:1rem;border-radius:10px}}figure img{{max-width:100%;height:auto}}.note{{border-left:4px solid #d79a32;padding:.6rem 1rem;background:#fff8e9}}footer{{margin-top:2rem;border-top:1px solid #ccd8d5;padding-top:1rem}}
</style></head><body>
<h1>Casos positivos de COVID-19 en Boyacá</h1>
<p><b>Pregunta:</b> ¿Cómo evolucionó mes a mes el número de casos reportados durante el periodo seleccionado?</p>
<p><b>Departamento:</b> Boyacá · <b>Periodo:</b> {html.escape(periodo)} · <b>Fecha analizada:</b> fecha reporte web · <b>Conteo:</b> IDs de caso únicos</p>
<section class="cards" aria-label="Indicadores">{tarjetas}</section>
<h2>Hallazgo</h2><p>{html.escape(hallazgo)}</p>
<h2>Evolución mensual</h2><figure><img src="graficos/casos-mensuales.png" alt="Gráfico de línea de casos únicos reportados por mes"></figure>
<h2>Distribución por sexo</h2><p>Gráfico categórico de otra columna disponible en el CSV; los faltantes se muestran como “Sin dato”.</p><figure><img src="graficos/casos-por-sexo.png" alt="Gráfico de barras horizontales de casos únicos por sexo"></figure>
<h2>Limitaciones y limpieza</h2><ul>{lista_limitaciones}</ul>
<p>El filtro departamental ignora diferencias de acentos, caja y espacios. Las fechas no interpretables y los registros sin fecha o ID válido no entran al conteo. Los datos faltantes de sexo se conservan como categoría “Sin dato”.</p>
<footer><b>Fuente:</b> <a href="{fuente}" rel="noopener noreferrer">Portal Nacional de Datos Abiertos — INS, Casos positivos de COVID-19 en Colombia</a>.<br>
CSV leído: <code>{html.escape(str(ruta_csv.relative_to(RAIZ)))}</code>. Tablero generado localmente por <code>analisis.py</code>.</footer>
</body></html>"""
    RUTA_TABLERO.parent.mkdir(parents=True, exist_ok=True)
    RUTA_TABLERO.write_text(html_final, encoding="utf-8")

    print(f"CSV leído: {ruta_csv}")
    print(f"Departamento: Boyacá | Periodo: {periodo}")
    print(f"Casos con ID único: {total:,} | Mes pico: {pico_mes} ({pico_casos:,})")
    print(f"Tablero: {RUTA_TABLERO}")
    print(f"Gráficos: {RUTA_GRAFICOS}")


if __name__ == "__main__":
    construir_tablero()