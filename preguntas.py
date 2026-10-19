"""Definición única de la encuesta. La usan el formulario, la validación y la exportación.

Los nombres de columna (campo "col") coinciden con los que usa el script de análisis,
así el Excel exportado se puede analizar directamente.
"""

SECCIONES = [
    {"id": "A", "titulo": "Datos generales", "mostrar_si": None},
    {"id": "B", "titulo": "Experiencia con agencias de viaje", "mostrar_si": ("P5_Contrato_agencia", "Sí")},
    {"id": "C", "titulo": "Interés en una aplicación de viaje", "mostrar_si": None},
    {"id": "D", "titulo": "Viajeros en moto", "mostrar_si": ("P14_Viajes_moto", "Sí")},
    {"id": "E", "titulo": "Para terminar", "mostrar_si": None},
]

PREGUNTAS = [
    # --- A ---
    {"col": "P1_Edad", "sec": "A", "n": 1, "texto": "Edad", "tipo": "uno",
     "opciones": ["18-25", "26-35", "36-45", "46-55", "Más de 55"]},
    {"col": "P2_Frecuencia_viaje", "sec": "A", "n": 2, "texto": "¿Con qué frecuencia viaja al año?", "tipo": "uno",
     "opciones": ["1 vez", "2 a 3 veces", "4 o más veces"]},
    {"col": "P3_Con_quien", "sec": "A", "n": 3, "texto": "¿Con quién suele viajar?", "tipo": "uno",
     "opciones": ["Solo", "Pareja", "Familia", "Amigos / grupo"]},
    {"col": "P4_Medio_preferido", "sec": "A", "n": 4, "texto": "¿Cómo prefiere viajar a otras ciudades?", "tipo": "uno",
     "opciones": ["Avión", "Bus", "Carro", "Moto"]},
    {"col": "P5_Contrato_agencia", "sec": "A", "n": 5, "texto": "¿Ha contratado un plan de viaje con una agencia?",
     "tipo": "uno", "opciones": ["Sí", "No"]},
    # --- B (solo si P5 = Sí) ---
    {"col": "P6_Canal_info", "sec": "B", "n": 6,
     "texto": "¿Cómo recibió la información de su viaje (horarios, hotel, recogida)?", "tipo": "uno",
     "opciones": ["Correo", "WhatsApp", "Llamada", "Documento impreso", "Otro"]},
    {"col": "P7_Problemas", "sec": "B", "n": 7, "texto": "¿Ha tenido problemas durante un viaje?",
     "ayuda": "Puede marcar varias opciones.", "tipo": "varios", "exclusiva": "Ninguno",
     "opciones": ["Retrasos", "No lo recogieron", "Error en hotel", "Falta de información", "Ninguno"]},
    {"col": "P8_Claridad_info", "sec": "B", "n": 8, "texto": "Califique la claridad de la información recibida",
     "tipo": "escala", "extremos": ("Muy mala", "Excelente")},
    {"col": "P9_Acompanamiento", "sec": "B", "n": 9, "texto": "Califique el acompañamiento de la agencia durante el viaje",
     "tipo": "escala", "extremos": ("Muy malo", "Excelente")},
    # --- C ---
    {"col": "P10_Itinerario_celular", "sec": "C", "n": 10, "texto": "¿Le gustaría ver su itinerario completo en el celular?",
     "tipo": "uno", "opciones": ["Sí", "No", "Tal vez"]},
    {"col": "P11_Funciones", "sec": "C", "n": 11, "texto": "Marque las funciones más importantes para usted",
     "ayuda": "Máximo 4.", "tipo": "varios", "maximo": 4,
     "opciones": ["Hora de vuelo y recogida", "Ubicación del hotel en mapa", "Datos del conductor o supervisor",
                  "Notificaciones", "Chat con asistencia", "Botón de emergencia", "Documentos sin internet",
                  "Promociones"]},
    {"col": "P12_Importancia_supervisor", "sec": "C", "n": 12,
     "texto": "En viajes por carretera, ¿qué tan importante es que un supervisor vea su ubicación y le dé apoyo?",
     "tipo": "escala", "extremos": ("Nada importante", "Muy importante")},
    {"col": "P13_Pagaria_mas", "sec": "C", "n": 13,
     "texto": "¿Pagaría un poco más por un plan con acompañamiento y seguimiento en vivo?", "tipo": "uno",
     "opciones": ["Sí", "No", "Depende del precio"]},
    {"col": "P14_Viajes_moto", "sec": "C", "n": 14, "texto": "¿Ha realizado viajes largos en moto?", "tipo": "uno",
     "opciones": ["Sí", "No"]},
    # --- D (solo si P14 = Sí) ---
    {"col": "P15_Preocupacion", "sec": "D", "n": 15, "texto": "¿Qué es lo que más le preocupa?", "tipo": "uno",
     "opciones": ["Seguridad", "Clima y estado de las vías", "Mecánica / varada", "Dónde dormir", "Perderse en la ruta"]},
    {"col": "P16_Grupo_guiado", "sec": "D", "n": 16, "texto": "¿Viajaría en grupo guiado con supervisor y moto de apoyo?",
     "tipo": "uno", "opciones": ["Sí", "No", "Tal vez"]},
    # --- E ---
    {"col": "P17_Comentario", "sec": "E", "n": 17, "texto": "Comentario o sugerencia", "tipo": "texto",
     "opcional": True},
]

COLUMNAS = [p["col"] for p in PREGUNTAS]
NO_APLICA = "No aplica"
