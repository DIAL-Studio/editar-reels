# Funciones que comparten los scripts.
import json, os, subprocess

MODELOS = [
    '~/whisper.cpp/models/ggml-large-v3-turbo.bin',
    '~/whisper-modelos/ggml-large-v3-turbo.bin',
    '~/whisper.cpp/models/ggml-medium.bin',
    '~/whisper-modelos/ggml-medium.bin',
]


def correr(args, **k):
    return subprocess.run(args, check=True, **k)


def modelo():
    # WHISPER_MODEL gana sobre las rutas conocidas.
    env = os.environ.get('WHISPER_MODEL')
    if env and os.path.exists(os.path.expanduser(env)):
        return os.path.expanduser(env)
    for m in MODELOS:
        if os.path.exists(os.path.expanduser(m)):
            return os.path.expanduser(m)
    return None


def sondear(archivo):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', archivo],
                       check=True, capture_output=True, text=True)
    return json.loads(r.stdout)


def duracion(archivo):
    return float(sondear(archivo)['format']['duration'])


def cuadros(archivo):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', archivo],
                       check=True, capture_output=True, text=True)
    return int(r.stdout.strip().split(',')[0])
