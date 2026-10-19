"""Analiza el Excel descargado desde /resultados/excel.

Uso:
    python analisis/analizar_respuestas.py respuestas_turismax_AAAAMMDD_HHMM.xlsx

Genera resumen.json (frecuencias, porcentajes y promedios por pregunta),
que es la entrada de los gráficos y del capítulo de análisis.
"""
import json
import sys

import pandas as pd

if len(sys.argv) != 2:
    sys.exit("Uso: python analisis/analizar_respuestas.py <archivo.xlsx>")

df = pd.read_excel(sys.argv[1])
texto = [c for c in df.columns if not c.startswith(("P8_", "P9_", "P12_")) and c != "ID"]
df[texto] = df[texto].astype(object).where(df[texto].notna(), "")
print(f"Respuestas leídas: {len(df)}")


def freq(col, orden, base=None):
    s = df[col] if base is None else df.loc[base, col]
    s = s[s.astype(str).str.strip() != ""]
    c = s.astype(str).str.replace(r"\.0$", "", regex=True).value_counts()
    extra = [k for k in c.index if k not in orden]  # categorías no previstas, al final
    c = c.reindex(list(orden) + extra, fill_value=0)
    n = int(c.sum())
    return [(str(k), int(v), round(100 * v / n, 1) if n else 0.0) for k, v in c.items()], n


def multi(col, opciones, base):
    s = df.loc[base, col].astype(str)
    n = len(s)
    out = [(o, int(s.apply(lambda x: o in x.split("; ")).sum())) for o in opciones]
    out = [(o, v, round(100 * v / n, 1) if n else 0.0) for o, v in out]
    out.sort(key=lambda t: -t[1])
    return out, n


def media(col, base=None):
    s = pd.to_numeric(df[col] if base is None else df.loc[base, col], errors="coerce").dropna()
    return round(float(s.mean()), 2) if len(s) else None


agencia = df["P5_Contrato_agencia"] == "Sí"
moto = df["P14_Viajes_moto"] == "Sí"
todos = pd.Series(True, index=df.index)
esc = ["1", "2", "3", "4", "5"]

res = {
    "N": len(df),
    "P1": freq("P1_Edad", ["18-25", "26-35", "36-45", "46-55", "Más de 55"]),
    "P2": freq("P2_Frecuencia_viaje", ["1 vez", "2 a 3 veces", "4 o más veces"]),
    "P3": freq("P3_Con_quien", ["Solo", "Pareja", "Familia", "Amigos / grupo"]),
    "P4": freq("P4_Medio_preferido", ["Avión", "Bus", "Carro", "Moto"]),
    "P5": freq("P5_Contrato_agencia", ["Sí", "No"]),
    "P6": freq("P6_Canal_info", ["WhatsApp", "Correo", "Llamada", "Documento impreso", "Otro"], agencia),
    "P7": multi("P7_Problemas", ["Retrasos", "No lo recogieron", "Error en hotel", "Falta de información", "Ninguno"], agencia),
    "P8": freq("P8_Claridad_info", esc, agencia),
    "P9": freq("P9_Acompanamiento", esc, agencia),
    "P8_media": media("P8_Claridad_info", agencia),
    "P9_media": media("P9_Acompanamiento", agencia),
    "P10": freq("P10_Itinerario_celular", ["Sí", "Tal vez", "No"]),
    "P11": multi("P11_Funciones", ["Hora de vuelo y recogida", "Ubicación del hotel en mapa",
                                   "Datos del conductor o supervisor", "Notificaciones", "Chat con asistencia",
                                   "Botón de emergencia", "Documentos sin internet", "Promociones"], todos),
    "P12": freq("P12_Importancia_supervisor", esc),
    "P12_media": media("P12_Importancia_supervisor"),
    "P13": freq("P13_Pagaria_mas", ["Sí", "Depende del precio", "No"]),
    "P14": freq("P14_Viajes_moto", ["Sí", "No"]),
    "P15": freq("P15_Preocupacion", ["Seguridad", "Clima y estado de las vías", "Mecánica / varada",
                                     "Dónde dormir", "Perderse en la ruta"], moto),
    "P16": freq("P16_Grupo_guiado", ["Sí", "Tal vez", "No"], moto),
    "comentarios": [c for c in df["P17_Comentario"].astype(str) if c.strip()],
}

with open("resumen.json", "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)

for k, v in res.items():
    print(k, v)
print("\nListo: resumen.json")
