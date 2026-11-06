# editar-reels

Skill para editar reels con Codex, con perfiles separados por creador o marca. Incluye configuración, correcciones, lecciones y análisis de referencias. La primera versión integra los scripts del proyecto de Alan Daitch y amplía el flujo con perfiles, controles de HDR y revisión de movimiento y audio.

## Instalación para Codex

Copia la carpeta `editar-reels` de este repositorio a `.agents/skills/editar-reels` dentro de tu proyecto. Abre Codex en ese proyecto y pide «Configura editar-reels para mi marca». La skill crea perfiles locales en `.editar-reels/perfiles/`. Excluye esa carpeta de Git si contiene información privada. Cada perfil guarda sus preferencias, estilo y correcciones.

Los scripts originales requieren FFmpeg, FFprobe, Python y whisper.cpp con su modelo. Las animaciones HTML requieren Node y Playwright. El flujo puede adaptarse a Whisper Python y Remotion, pero los scripts incluidos no proporcionan esa integración automáticamente. Revisa las dependencias con `python3 .agents/skills/editar-reels/scripts/revisar_entorno.py`.

Para cambiar de marca indica «Edita este reel con el perfil nombre-de-marca». Para aprender de una corrección, indica si debe guardarse como preferencia permanente o solo para el proyecto. Revisa nombres, precios, subtítulos y resultados antes de publicar.

## Créditos

Basado en [editar-mis-reels de Alan Daitch](https://github.com/alandaitch/editar-mis-reels), que aporta el flujo inicial, scripts, plantillas y referencias. Sus archivos se distribuyen bajo la licencia MIT incluida. Esta adaptación añade orientación para Codex y perfiles separados. No incluye material privado de DC ni del video de San Blas.

La compatibilidad y documentación para Claude Code y OpenCode se añadirá posteriormente.
