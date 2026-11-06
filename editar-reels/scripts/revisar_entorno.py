# Revisa lo que el skill necesita y explica cómo instalar lo que falta.
# Uso: python3 revisar_entorno.py
import shutil, subprocess, sys
from comun import modelo

faltan = 0


def linea(ok, texto, ayuda=''):
    global faltan
    print(('OK    ' if ok else 'FALTA ') + texto + ('' if ok else f'\n      {ayuda}'))
    faltan += 0 if ok else 1


linea(sys.version_info >= (3, 8), 'Python 3.8 o más nuevo', 'Instalá Python desde python.org.')
ff = shutil.which('ffmpeg')
linea(bool(ff), 'ffmpeg', 'Mac: brew install ffmpeg. Windows: winget install Gyan.FFmpeg.')
if ff:
    filtros = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    linea(' ass ' in filtros, 'ffmpeg con subtítulos (libass)', 'Mac: brew install ffmpeg-full. Usá ese ffmpeg.')
    linea(' zscale ' in filtros, 'ffmpeg con zscale, para grabaciones HDR de celular', 'Mac: brew install ffmpeg-full.')
linea(bool(shutil.which('whisper-cli')), 'whisper-cli', 'Mac: brew install whisper-cpp. Otros: compilá whisper.cpp.')
m = modelo()
linea(bool(m), f'modelo de whisper: {m}',
      'Bajalo con: mkdir -p ~/whisper-modelos && curl -L -o ~/whisper-modelos/ggml-large-v3-turbo.bin '
      'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin')
print('OPCIONAL: node y Playwright, solo para animaciones. En scripts/: npm install && npx playwright install chromium')
print('Todo listo.' if not faltan else f'Faltan {faltan}.')
sys.exit(1 if faltan else 0)
