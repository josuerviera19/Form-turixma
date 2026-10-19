# Encuesta Turismax

Formulario web para la encuesta a clientes y viajeros del proyecto Turismax (Ingeniería de Sistemas, Unicomfacauca).

- 17 preguntas con saltos: la sección B solo aparece si la persona respondió «Sí» en la pregunta 5, y la sección D solo si respondió «Sí» en la 14.
- Las respuestas se guardan en PostgreSQL y no se pierden cuando el servidor se reinicia.
- En `/resultados` (con usuario y clave) se ve el conteo y se descarga el Excel con todas las respuestas.

## Estructura

```
app.py                         aplicación Flask (rutas, validación, base de datos, exportación)
preguntas.py                   las 17 preguntas: si cambias una, cámbiala solo aquí
templates/                     páginas HTML (formulario, gracias, resultados)
static/estilo.css              estilos (diseñado primero para celular)
analisis/analizar_respuestas.py  convierte el Excel descargado en resumen.json para el informe
render.yaml                    configuración de Render (web + base de datos gratis)
requirements.txt               dependencias
```

## 1. Subir el código a GitHub

1. En el repositorio, borra `Index.py` (era el generador de respuestas de prueba; no es parte de la encuesta).
2. Sube todos los archivos de esta carpeta respetando las subcarpetas `templates/`, `static/` y `analisis/`.
   Desde la web de GitHub: **Add file → Upload files**, arrastra la carpeta completa y haz **Commit changes**.

## 2. Desplegar en Render (opción recomendada: Blueprint)

El archivo `render.yaml` crea automáticamente la base de datos y el servicio web.

1. Entra a <https://dashboard.render.com> e inicia sesión con GitHub.
2. **New → Blueprint**.
3. Elige el repositorio `Form-turixma`.
4. Render lee `render.yaml` y muestra dos recursos: `encuesta-turismax-db` (base de datos) y `encuesta-turismax` (web). Haz clic en **Apply** / **Deploy Blueprint**.
5. Espera a que la web diga **Live** (la primera vez tarda unos minutos).
6. Tu enlace queda como `https://encuesta-turismax.onrender.com` (si el nombre está ocupado, Render agrega letras al final; el enlace exacto aparece arriba en la página del servicio).

### Ver la clave de resultados

Render genera la clave automáticamente:

1. Abre el servicio `encuesta-turismax` → pestaña **Environment**.
2. Copia el valor de `ADMIN_PASSWORD` (puedes cambiarlo por uno tuyo y guardar).
3. Entra a `https://TU-ENLACE.onrender.com/resultados` con usuario `admin` y esa clave.

## 2b. Desplegar a mano (si no usas Blueprint)

**Base de datos:** New → Postgres → Name `encuesta-turismax-db`, Plan **Free** → Create. Cuando esté lista, copia la **Internal Database URL**.

**Servicio web:** New → Web Service → elige el repositorio y llena:

| Campo | Valor |
|---|---|
| Name | `encuesta-turismax` |
| Language / Runtime | Python 3 |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |

En **Environment Variables** agrega:

| Key | Value |
|---|---|
| `DATABASE_URL` | la Internal Database URL que copiaste |
| `ADMIN_USER` | `admin` |
| `ADMIN_PASSWORD` | una clave tuya |
| `PYTHON_VERSION` | `3.12.7` |

Luego **Create Web Service**.

## 3. Recolectar las respuestas

- Prueba el enlace tú mismo una vez y revisa en `/resultados` que el contador sube. Luego **borra esa prueba**: lo más simple es responder con datos reales tuyos o descontarla al analizar (es la fila con ID 1).
- Comparte el enlace por WhatsApp, Instagram y grupos de viajeros y moteros. Meta: 30 respuestas.
- Cada dispositivo puede responder una sola vez (se guarda una cookie para evitar duplicados accidentales).

## 4. Analizar

1. En `/resultados`, haz clic en **Descargar Excel**.
2. En tu computador:
   ```bash
   pip install pandas openpyxl
   python analisis/analizar_respuestas.py respuestas_turismax_AAAAMMDD_HHMM.xlsx
   ```
3. Se genera `resumen.json` con frecuencias, porcentajes y promedios por pregunta.

## Límites del plan gratuito de Render

- El servicio web se duerme tras 15 minutos sin visitas; la siguiente persona espera alrededor de un minuto mientras arranca.
- **La base de datos gratuita vence 30 días después de crearla** (Render da 14 días más antes de borrarla). **Descarga el Excel antes de que venza.**
- Solo se permite una base de datos gratuita por cuenta.

## Probar en tu computador

```bash
pip install -r requirements.txt
ADMIN_PASSWORD=prueba flask --app app run
```

Abre <http://127.0.0.1:5000>. Sin `DATABASE_URL`, las respuestas se guardan en `respuestas.db` (SQLite).
