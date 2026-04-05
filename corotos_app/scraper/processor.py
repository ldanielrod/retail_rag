import pandas as pd
from ..core.config import FiltrosBusqueda

def aplicar_filtros(df: pd.DataFrame, filtros: FiltrosBusqueda) -> pd.DataFrame:
    if df.empty: return df
    original = len(df)
    if filtros.precio_min is not None:
        df = df[df["precio_num"].fillna(0) >= filtros.precio_min]
    if filtros.precio_max is not None:
        df = df[df["precio_num"].fillna(float("inf")) <= filtros.precio_max]
    if filtros.habitaciones_min is not None:
        df = df[df["habitaciones"].fillna(0) >= filtros.habitaciones_min]

    descartados = original - len(df)
    if descartados:
        print(f"  🔽 Filtros numéricos: {original} → {len(df)} ({descartados} descartados)")
    return df.reset_index(drop=True)

def exportar_datos(df: pd.DataFrame, csv_path: str = "apartamentos_corotos.csv", xlsx_path: str = "apartamentos_corotos.xlsx"):
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)
