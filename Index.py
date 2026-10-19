import random
import json
import pandas as pd

SEMILLA = 2026
N = 30
rng = random.Random(SEMILLA)


def uno(opciones, pesos):
    return rng.choices(opciones, weights=pesos, k=1)[0]


def varios(opciones, pesos, maximo, minimo=1):
    k = rng.randint(minimo, maximo)
    elegidas = []
    pool = list(zip(opciones, pesos))
    for _ in range(k):
        ops, ps = zip(*pool)
        e = rng.choices(ops, weights=ps, k=1)[0]
        elegidas.append(e)
        pool = [(o, p) for o, p in pool if o != e]
    return [o for o in opciones if o in elegidas]


filas = []
for i in range(1, N + 1):
    f = {"ID": f"S{i:02d}"}
    f["P1_Edad"] = uno(["18-25", "26-35", "36-45", "46-55", "Más de 55"], [8, 10, 6, 4, 2])
    f["P2_Frecuencia_viaje"] = uno(["1 vez", "2 a 3 veces", "4 o más veces"], [8, 14, 8])
    f["P3_Con_quien"] = uno(["Solo", "Pareja", "Familia", "Amigos / grupo"], [4, 8, 10, 8])
    f["P4_Medio_preferido"] = uno(["Avión", "Bus", "Carro", "Moto"], [11, 5, 6, 8])
    f["P5_Contrato_agencia"] = uno(["Sí", "No"], [20, 10])
    if f["P5_Contrato_agencia"] == "Sí":
        f["P6_Canal_info"] = uno(["Correo", "WhatsApp", "Llamada", "Documento impreso"], [5, 11, 3, 1])
        prob = varios(["Retrasos", "No lo recogieron", "Error en hotel", "Falta de información", "Ninguno"],
                      [9, 4, 4, 11, 4], maximo=2)
        if "Ninguno" in prob and len(prob) > 1:
            prob = ["Ninguno"]
        f["P7_Problemas"] = "; ".join(prob)
        f["P8_Claridad_info"] = uno([1, 2, 3, 4, 5], [2, 6, 7, 4, 1])
        f["P9_Acompanamiento"] = uno([1, 2, 3, 4, 5], [3, 6, 6, 4, 1])
    else:
        f["P6_Canal_info"] = "No aplica"
        f["P7_Problemas"] = "No aplica"
        f["P8_Claridad_info"] = None
        f["P9_Acompanamiento"] = None
    f["P10_Itinerario_celular"] = uno(["Sí", "No", "Tal vez"], [23, 2, 5])
    funciones = ["Hora de vuelo y recogida", "Ubicación del hotel en mapa", "Datos del conductor o supervisor",
                 "Notificaciones", "Chat con asistencia", "Botón de emergencia", "Documentos sin internet",
                 "Promociones"]
    f["P11_Funciones"] = "; ".join(varios(funciones, [12, 9, 7, 8, 6, 7, 6, 3], maximo=4, minimo=2))
    f["P12_Importancia_supervisor"] = uno([1, 2, 3, 4, 5], [1, 2, 6, 10, 11])
    f["P13_Pagaria_mas"] = uno(["Sí", "No", "Depende del precio"], [11, 4, 15])
    moto_pesos = [3, 1] if f["P4_Medio_preferido"] == "Moto" else [2, 5]
    f["P14_Viajes_moto"] = uno(["Sí", "No"], moto_pesos)
    if f["P14_Viajes_moto"] == "Sí":
        f["P15_Preocupacion"] = uno(["Seguridad", "Clima y estado de las vías", "Mecánica / varada",
                                     "Dónde dormir", "Perderse en la ruta"], [9, 5, 5, 2, 2])
        f["P16_Grupo_guiado"] = uno(["Sí", "No", "Tal vez"], [7, 2, 4])
    else:
        f["P15_Preocupacion"] = "No aplica"
        f["P16_Grupo_guiado"] = "No aplica"
    f["P17_Comentario"] = ""
    filas.append(f)

df = pd.DataFrame(filas)
df.to_csv("respuestas_simuladas.csv", index=False, encoding="utf-8-sig")


# ---------- Resumen estadístico ----------
def freq(col, orden=None, base=None):
    s = df[col]
    if base is not None:
        s = s[base]
    c = s.value_counts()
    if orden:
        c = c.reindex(orden, fill_value=0)
    n = int(c.sum())
    return [(str(k), int(v), round(100 * v / n, 1)) for k, v in c.items()], n


def multi(col, opciones, base):
    s = df.loc[base, col]
    n = len(s)
    out = []
    for o in opciones:
        v = int(s.apply(lambda x: o in x.split("; ")).sum())
        out.append((o, v, round(100 * v / n, 1)))
    out.sort(key=lambda t: -t[1])
    return out, n


agencia = df["P5_Contrato_agencia"] == "Sí"
moto = df["P14_Viajes_moto"] == "Sí"
todos = df["ID"].notna()

res = {}
res["P1"] = freq("P1_Edad", ["18-25", "26-35", "36-45", "46-55", "Más de 55"])
res["P2"] = freq("P2_Frecuencia_viaje", ["1 vez", "2 a 3 veces", "4 o más veces"])
res["P3"] = freq("P3_Con_quien", ["Solo", "Pareja", "Familia", "Amigos / grupo"])
res["P4"] = freq("P4_Medio_preferido", ["Avión", "Bus", "Carro", "Moto"])
res["P5"] = freq("P5_Contrato_agencia", ["Sí", "No"])
res["P6"] = freq("P6_Canal_info", ["WhatsApp", "Correo", "Llamada", "Documento impreso"], agencia)
res["P7"] = multi("P7_Problemas", ["Retrasos", "No lo recogieron", "Error en hotel", "Falta de información", "Ninguno"], agencia)
res["P8"] = freq("P8_Claridad_info", [1, 2, 3, 4, 5], agencia)
res["P9"] = freq("P9_Acompanamiento", [1, 2, 3, 4, 5], agencia)
res["P8_media"] = round(float(df.loc[agencia, "P8_Claridad_info"].mean()), 2)
res["P9_media"] = round(float(df.loc[agencia, "P9_Acompanamiento"].mean()), 2)
res["P10"] = freq("P10_Itinerario_celular", ["Sí", "Tal vez", "No"])
res["P11"] = multi("P11_Funciones", ["Hora de vuelo y recogida", "Ubicación del hotel en mapa",
                                     "Datos del conductor o supervisor", "Notificaciones", "Chat con asistencia",
                                     "Botón de emergencia", "Documentos sin internet", "Promociones"], todos)
res["P12"] = freq("P12_Importancia_supervisor", [1, 2, 3, 4, 5])
res["P12_media"] = round(float(df["P12_Importancia_supervisor"].mean()), 2)
res["P13"] = freq("P13_Pagaria_mas", ["Sí", "Depende del precio", "No"])
res["P14"] = freq("P14_Viajes_moto", ["Sí", "No"])
res["P15"] = freq("P15_Preocupacion", ["Seguridad", "Clima y estado de las vías", "Mecánica / varada",
                                       "Dónde dormir", "Perderse en la ruta"], moto)
res["P16"] = freq("P16_Grupo_guiado", ["Sí", "Tal vez", "No"], moto)

# Cruce: de quienes contrataron agencia, % con calificación <=2 en claridad
res["claridad_baja"] = int((df.loc[agencia, "P8_Claridad_info"] <= 2).sum())
res["acomp_baja"] = int((df.loc[agencia, "P9_Acompanamiento"] <= 2).sum())
res["sup_alta"] = int((df["P12_Importancia_supervisor"] >= 4).sum())

with open("resumen.json", "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)

for k, v in res.items():
    print(k, v)
