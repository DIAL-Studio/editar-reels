---
name: editar-reels
description: Edita reels, TikToks y Shorts verticales desde una grabación cruda. Corta silencios y tomas repetidas, pone subtítulos, inserta planos y animaciones, nivela el audio y revisa cada corte. Guarda el gusto del usuario en preferencias.md y suma cada corrección como regla. Usar SIEMPRE que el usuario pase una grabación y pida editarla, por ejemplo "editá este reel", "cortá los silencios" o "poné subtítulos". Usar también para corregir un reel editado con este skill y para "configurá mi skill de edición". NO usar para escribir guiones.
---

# Editar reels

Este skill edita un reel vertical de punta a punta.

`scripts/`, `assets/`, `references/`, `estilo.json` y los `.md` están en la carpeta de este skill. `trabajo` es la carpeta de trabajo del reel.

## Perfiles independientes

Usá el perfil elegido por el usuario. Guardá perfiles privados fuera de la instalación de la skill, en `.editar-reels/perfiles/<nombre>/` dentro del proyecto del usuario. Creá el directorio copiando las plantillas `preferencias.md`, `correcciones.md` y `estilo.json` de esta skill. No sobrescribas un perfil existente. Los recursos privados y los videos no deben subirse al repositorio público.

Antes de editar, resolvé el perfil pedido, leé sus tres archivos y ejecutá la configuración desde `references/configurar.md` si está incompleto. Cuando las instrucciones siguientes mencionan `preferencias.md`, `correcciones.md` o `estilo.json`, usá los archivos del perfil activo. Si el perfil no está claro y hay varios, preguntá cuál corresponde. Nunca mezcles decisiones de perfiles distintos.

Al recibir una corrección, aplicala al video y registrala en el historial del perfil. Promové al perfil las preferencias permanentes autorizadas, dejá los cambios puntuales en el proyecto y agregá a las lecciones generales solo reglas técnicas verificadas. No cambies otras marcas. Al cambiar de proyecto, volvé a resolver el perfil.

Para títulos, medí referencias visuales y creá pruebas cortas con subtítulos legibles, palabras o cifras protagonistas, jerarquía y entradas sincronizadas. Revisá fondos claros, rostros, zonas seguras y lectura en móvil. Para HDR a SDR compará con el original y revisá altas luces y saturación antes de extender la conversión. Al recortar drone en vertical, revisá la fluidez cuadro a cuadro y el seguimiento del pin. Reducí oleaje y tráfico desde la voz original y contrastá claridad antes de mezclar música. Verificá precios y datos con el usuario.

Remotion y HyperFrames pueden usarse si ya están instalados. Los scripts incluidos usan FFmpeg, whisper.cpp y opcionalmente Playwright, como el proyecto original. Adaptá la transcripción a Whisper Python si es el motor local disponible y verificá las marcas de tiempo. No supongas que los scripts del proyecto original aceptan automáticamente Whisper Python.

## 1. Antes de editar

1. Leé `preferencias.md` y `correcciones.md`. No preguntes lo que ya responden.
2. Buscá `[COMPLETAR]` en `preferencias.md`. Si aparece, seguí `references/configurar.md` antes de editar.
3. Corré `python3 scripts/revisar_entorno.py`. Instalá lo que falte, con el OK del usuario.
4. Creá `trabajo` al lado de la grabación, con el nombre `edicion-<tema>`. No la crees dentro del skill. Las correcciones necesitan sus archivos.

## 2. Material

- Pedí la grabación y el guion, si existe.
- Pedí imágenes, capturas y clips, si existen. Usá solo material con permiso.
- Seguí las reglas de autonomía de `preferencias.md`.
- Trabajá sobre una copia. Nunca modifiques la grabación original.

## 3. Cortar

```bash
python3 scripts/cortar_silencios.py grabacion.mp4 trabajo --min 0.25 --aire 0.10
```

- El script deja `editado.mp4`, `editado16k.wav` y `cortes.json`.
- Tomá `--min` y `--aire` de `preferencias.md`.
- Si el tamaño es otro, pasá `--ancho`, `--alto` y `--fps`.
- Una grabación HDR de celular se pasa sola a SDR. El log lo avisa.

## 4. Transcribir y buscar tomas repetidas

```bash
python3 scripts/transcribir.py trabajo [--guion guion.txt]
```

- El script transcribe cada tramo por separado y deja `palabras.json`.
- Marca `REPITE`, `ARRANQUE`, `CORTA` y `FALTA`, y propone el rango por sacar.
- Corregí con `--quitar` en `cortar_silencios.py`. Conservá la última toma.
- Repetí los pasos 3 y 4 hasta llegar a 0 alertas o justificar cada alerta.
- Compará cada frase con el guion. Whisper entiende mal nombres y marcas.

## 5. Planificar

1. Elegí el formato en la tabla de `preferencias.md`.
2. Escribí una lista de planos con tiempos del video editado. Anclá cada plano a una palabra de `palabras.json`.
3. Mostrale la lista al usuario si el formato es nuevo. Si pide "hacelo completo", seguí sin esperar.

Reglas por defecto. `preferencias.md` manda sobre estas reglas:

- La pantalla acompaña la voz. No repite lo que dice la voz.
- Cada plano llena la pantalla de borde a borde.
- Cada plano empieza en la primera sílaba de una palabra.
- Una imagen quieta lleva un zoom lento.
- El cierre va sin animaciones. El remate necesita la cara.

## 6. Animaciones (opcional)

Empezá sin animaciones si el usuario recién arranca. Sumalas cuando los cortes y los subtítulos estén aprobados.

1. Copiá `assets/animacion-ejemplo.html`.
2. Definí `window.duracion` y `window.dibujar(t)`. Cada cuadro depende solo de `t`. Sin `setTimeout`, animaciones CSS ni azar sin semilla.
3. Sacá fotos de la animación y corregí antes del render final.
4. La primera vez, instalá Playwright: `cd scripts && npm install && npx playwright install chromium`.
5. Renderizá:

```bash
node scripts/render_html.mjs animacion.html trabajo/animacion.mp4 1080 1920
```

## 7. Subtítulos

```bash
python3 scripts/subtitulos.py trabajo <ruta-del-perfil>/estilo.json
```

- `estilo.json` guarda fuente, tamaño, color, posición y agrupado.
- El script lista cada subtítulo. Leé cada línea entera antes de armar.
- Corregí tildes, nombres y marcas con `correcciones` en `estilo.json`.
- Si el usuario pide copiar un estilo, seguí `references/medir-referencia.md`.

## 8. Armar

Escribí `trabajo/plan.json`:

```json
{
  "base": "editado.mp4",
  "salida": "reel-v1.mp4",
  "insertos": [
    {"desde": 3.2, "hasta": 6.1, "archivo": "animacion.mp4"},
    {"desde": 7.0, "hasta": 8.5, "archivo": "clip.mp4", "t0": 12.0},
    {"desde": 9.0, "hasta": 12.0, "archivo": "captura.png", "zoom": 1.08, "foco": [0.5, 0.3]}
  ],
  "subtitulos": "subtitulos.ass",
  "lufs": -14
}
```

```bash
python3 scripts/armar.py trabajo/plan.json
```

- Las rutas de `plan.json` son relativas a `trabajo`.
- `t0` es el segundo del clip donde arranca el inserto. `foco` es el punto del zoom, de 0 a 1.
- Cambiá `salida` en cada versión: `-v2`, `-v3`. El script no pisa una versión anterior.
- Cuando el usuario apruebe, corré con `--final`. Comprime mejor.
- El script nivela el audio y verifica la cantidad de cuadros.

## 9. Revisar antes de mostrar

```bash
python3 scripts/hoja_cuadros.py trabajo/reel-v1.mp4 trabajo --plan trabajo/plan.json
```

Mirá cada `hoja-NN.jpg` y `cola.jpg`. `hoja.txt` dice qué segundo muestra cada foto. Para sumar fotos en palabras clave, pasá `--tiempos 3.2,8.1`.

Respondé cada pregunta:

- ¿Algún plano deja zonas vacías o negras?
- ¿Algún corte muestra un destello de otra toma?
- ¿El subtítulo tapa la cara o algo importante?
- ¿El subtítulo se lee sobre fondos claros?
- ¿Los últimos 15 cuadros muestran al usuario yendo a apagar la cámara?

Corregí lo que encuentres. Mostrá el reel después de esta revisión.

## 10. Entregar

Seguí la sección "Entrega" de `preferencias.md`. Escribí un mensaje corto: qué cambió y qué hay que revisar. Dejá el video al final del mensaje.

## 11. Corregir y aprender

Esta es la regla más importante del skill. Cada corrección del usuario se aplica dos veces:

1. Corregí el reel.
2. Escribí la regla en `correcciones.md`, con este formato:

```markdown
## AAAA-MM-DD · <reel>
- Dijo: "<la frase del usuario>"
- Por qué: <qué problema causaba>
- Regla: <qué hacer de ahora en más>
```

- Mové a `preferencias.md` cada regla sobre gusto.
- Si un script puede chequear la regla, sumá el chequeo al script.
- Antes de cerrar, decile al usuario qué regla sumaste. Usá una línea.

Mirá `references/lecciones.md` cuando algo falle. Trae errores comunes de edición.
