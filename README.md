# 📁 Organizador Inteligente de Archivos (Python)

Una herramienta de automatización diseñada para organizar tus descargas de forma mágica, moviendo los archivos a tus carpetas personales (OneDrive, Documentos, etc.) basándose tanto en la **extensión** del archivo como en su **contexto** (palabras clave en el nombre).

---

## ✨ Características Principales

1. **🧠 Enrutamiento Inteligente por Palabras Clave (Keyword Routing)**
   El motor analiza el nombre de cada archivo para entender su contexto antes de moverlo. Usa expresiones regulares (`RegEx`) para ser súper preciso y no confundir palabras (por ejemplo, "ia" no coincidirá por error con "historia"):
   - *Ejemplo:* Si el nombre contiene `"calculo"`, lo mueve a `UNIVERSIDAD\Calculo Multivariado`.
   - *Ejemplo:* Si contiene `"stream"`, lo mueve a `Consterna\STREAM`.
   - *Ejemplo:* Si contiene `"factura"`, va directo a `Facturas`.

2. **📦 Clasificación Automática por Extensiones (Fallback)**
   Si el archivo no contiene palabras clave conocidas, se clasifica por su tipo:
   - 🖼️ **Imágenes:** `.jpg`, `.png`, `.webp`, etc.
   - 📄 **Documentos:** `.pdf`, `.docx`, `.xlsx`, `.log`, etc.
   - 🎮 **Juegos y Mods:** `.jar` (Neoforge/Fabric), etc.
   - 📦 **Comprimidos:** `.zip`, `.rar`, `.mrpack`, `.tar.gz`.
   - ⚙️ **Instaladores:** `.exe`, `.msi`, `.iso`.
   - 💻 **Código:** `.py`, `.js`, `.html`, etc.

3. **🛡️ Seguridad y Control (Cero Pérdidas)**
   - **Simulación (`Dry-Run`):** Puedes ver un resumen de dónde irá cada archivo antes de tocar nada.
   - **Deshacer (`Undo`):** El sistema guarda un registro (`.organizer_history.json`) de la última limpieza. Si te equivocaste, puedes deshacer los movimientos con 1 clic.
   - **Resolución de Colisiones:** Si ya existe un archivo con ese nombre, no lo sobrescribe. Le añade un sufijo respetando extensiones dobles (ej. `archivo (1).tar.gz`).
   - **Detección y Eliminación de Duplicados Exactos:** Si descargas el mismo archivo dos veces, el sistema compara su tamaño y hash (SHA-256). Si son idénticos, **elimina la copia suelta** de tus descargas automáticamente para ahorrar espacio (configurable desde `config.json`).
   - **Exclusión de Temporales:** Ignora automáticamente descargas incompletas (`.crdownload`, `.tmp`).

---

## 🚀 Cómo Usarlo

El programa cuenta con un menú interactivo. Simplemente abre tu terminal en esta carpeta y ejecuta:

```bash
python main.py
```

### Opciones del menú:
1. **[1] Analizar y simular:** Ejecuta una corrida de prueba (Dry-Run). No mueve nada, solo te muestra un reporte de qué archivos detectó y a qué carpeta irán.
2. **[2] Organizar archivos ahora:** Mueve todos los archivos desde la carpeta de Origen a sus carpetas correctas en el Destino.
3. **[3] Deshacer (Undo):** Revierte la última organización devolviendo los archivos a su lugar original y borrando las carpetas vacías que se hayan creado.
4. **[4] Crear Sandbox:** Crea una carpeta de prueba con archivos falsos para que puedas practicar sin miedo.

También puedes ejecutarlo de forma **silenciosa y automática** mediante comandos, ideal para tareas programadas (Cron/Task Scheduler):
```bash
python main.py --run -y
```

---

## ⚙️ Configuración (`config.json`)

El corazón del programa es el archivo `config.json`. Desde ahí puedes controlar:
1. **`source_directory`**: La ruta absoluta donde el programa buscará los archivos desordenados (por defecto, tus *Descargas*).
2. **`target_directory`**: La ruta absoluta hacia donde se enviarán los archivos (por defecto, tu *OneDrive*).
3. **`keyword_rules`**: Diccionario donde mapeas *rutas de carpetas* a *listas de palabras clave*.
4. **`categories`**: Diccionario de extensiones predeterminadas.

¡Puedes abrir el `config.json` en cualquier momento y añadir una nueva materia de la universidad o un nuevo tipo de archivo!
