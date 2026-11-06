# Revisa lo que el skill necesita y explica cómo instalar lo que falta.
# Uso: python3 revisar_entorno.py
import argparse, importlib.util, shutil, subprocess, sys
from comun import modelo

parser = argparse.ArgumentParser()
parser.add_argument('--motor', choices=['python', 'cpp'], default='python')
args = parser.parse_args()

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
if args.motor == 'python':
    linea(importlib.util.find_spec('whisper') is not None, 'OpenAI Whisper para Python',
          'Instalá openai-whisper en este entorno de Python.')
    print('El modelo se descargará la primera vez si no está en caché.')
else:
    linea(bool(shutil.which('whisper-cli')), 'whisper-cli', 'Instalá whisper.cpp.')
    m = modelo()
    linea(bool(m), f'modelo GGML de whisper.cpp: {m}',
          'Configurá WHISPER_MODEL con la ruta a un modelo GGML.')
print('OPCIONAL: node y Playwright, solo para animaciones. En scripts/: npm install && npx playwright install chromium')
print('Todo listo.' if not faltan else f'Faltan {faltan}.')
sys.exit(1 if faltan else 0)
