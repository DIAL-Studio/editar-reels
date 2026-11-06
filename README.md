# editar-reels

Skill para editar reels con Codex, con perfiles separados por creador o marca. Incluye configuración, correcciones, lecciones y análisis de referencias. La primera versión integra los scripts del proyecto de Alan Daitch y amplía el flujo con perfiles, controles de HDR y revisión de movimiento y audio.

## Instalación para Codex

Copia la carpeta `editar-reels` de este repositorio a `.agents/skills/editar-reels` dentro de tu proyecto. Abre Codex en ese proyecto y pide «Configura editar-reels para mi marca». La skill crea perfiles locales en `.editar-reels/perfiles/`. Excluye esa carpeta de Git si contiene información privada. Cada perfil guarda sus preferencias, estilo y correcciones.

Los scripts requieren FFmpeg, FFprobe y Python con `openai-whisper`. Por defecto se usa el modelo `small`, que se descarga la primera vez si falta. Las animaciones HTML requieren Node y Playwright. Para usar whisper.cpp, instalá `whisper-cli` y un modelo GGML, y añadí `--motor cpp` a los comandos de diagnóstico y transcripción. Remotion aún no está integrado en los scripts. Revisa las dependencias con `python3 .agents/skills/editar-reels/scripts/revisar_entorno.py`.

Para cambiar de marca indica «Edita este reel con el perfil nombre-de-marca». Para aprender de una corrección, indica si debe guardarse como preferencia permanente o solo para el proyecto. Revisa nombres, precios, subtítulos y resultados antes de publicar.

## Créditos

Basado en [editar-mis-reels de Alan Daitch](https://github.com/alandaitch/editar-mis-reels), que aporta el flujo inicial, scripts, plantillas y referencias. Sus archivos se distribuyen bajo la licencia MIT incluida. Esta adaptación añade orientación para Codex y perfiles separados. No incluye material privado de DC ni del video de San Blas.

La compatibilidad y documentación para Claude Code y OpenCode se añadirá posteriormente.

## Transcripción

Ejecuta el script con el Python del entorno que tenga instalado `openai-whisper`. La entrada es el directorio generado por `cortar_silencios.py`, que contiene `cortes.json` y `editado16k.wav`. Se genera `palabras.json` con tiempos por palabra y alertas de tomas.

```bash
python editar-reels/scripts/transcribir.py trabajo --modelo small --idioma es
# Modelo ya descargado en un directorio específico
python editar-reels/scripts/transcribir.py trabajo --modelo small --model-dir /ruta/a/modelos
# Alternativa whisper.cpp
python editar-reels/scripts/transcribir.py trabajo --motor cpp --modelo /ruta/ggml-model.bin
```

Los tiempos de Whisper son estimaciones. Comprueba palabras, nombres y sincronización antes de entregar.
