# Saca fotos del reel para revisarlo: una hoja por cada 24 fotos y una hoja con los últimos cuadros.
# Uso: python3 hoja_cuadros.py reel.mp4 carpeta [--cada 3] [--cola 15] [--plan plan.json] [--tiempos 3.2,8.1]
# Saca una foto después de cada corte de cortes.json, en cada borde de inserto y cada --cada segundos.
# Escribe hoja-01.jpg, cola.jpg y hoja.txt. hoja.txt dice qué segundo muestra cada foto.
import argparse, glob, json, math, os, shutil, tempfile
from comun import correr, cuadros, duracion, sondear

p = argparse.ArgumentParser()
p.add_argument('reel')
p.add_argument('carpeta')
p.add_argument('--cada', type=float, default=3)
p.add_argument('--cola', type=int, default=15)
p.add_argument('--plan')
p.add_argument('--tiempos', default='')
a = p.parse_args()
dur = duracion(a.reel)
v = next(s for s in sondear(a.reel)['streams'] if s['codec_type'] == 'video')
num, den = map(int, v['r_frame_rate'].split('/'))
fps = num / den
t = [i * a.cada for i in range(int(dur / a.cada) + 1)]
cj = os.path.join(a.carpeta, 'cortes.json')
if os.path.exists(cj):
    with open(cj) as f:
        t += [c['ed_a'] + .1 for c in json.load(f)]
if a.plan:
    with open(a.plan) as f:
        for x in json.load(f).get('insertos', []):
            t += [x['desde'] + .05, x['hasta'] + .05]
t += [float(x) for x in a.tiempos.split(',') if x]
t = sorted(x for x in t if 0 <= x < dur - 1 / fps)
fotos = []
for x in t:
    if not fotos or x - fotos[-1] >= .25:
        fotos.append(x)

tmp = tempfile.mkdtemp()
for i, x in enumerate(fotos):
    correr(['ffmpeg', '-v', 'error', '-y', '-ss', f'{x:.3f}', '-i', a.reel, '-frames:v', '1', '-vf', 'scale=216:-2',
            '-q:v', '3', os.path.join(tmp, f'f{i:04d}.jpg')])
POR_HOJA, COL = 24, 6
for vieja in glob.glob(os.path.join(a.carpeta, 'hoja-*.jpg')):
    os.remove(vieja)
indice = []
for h in range(math.ceil(len(fotos) / POR_HOJA)):
    desde = h * POR_HOJA
    n = min(POR_HOJA, len(fotos) - desde)
    filas = math.ceil(n / COL)
    salida = os.path.join(a.carpeta, f'hoja-{h + 1:02d}.jpg')
    correr(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-start_number', str(desde), '-i', os.path.join(tmp, 'f%04d.jpg'),
            '-frames:v', '1', '-vf', f'tile={COL}x{filas}:padding=6:margin=6:color=white', '-q:v', '3', salida])
    for k in range(n):
        indice.append(f'hoja-{h + 1:02d} fila {k // COL + 1} columna {k % COL + 1}: {fotos[desde + k]:.2f} s')
filas = math.ceil(a.cola / 5)
desde_cola = max(0, cuadros(a.reel) - a.cola)
correr(['ffmpeg', '-v', 'error', '-y', '-i', a.reel, '-vf',
        f"select='gte(n,{desde_cola})',scale=216:-2,tile=5x{filas}:padding=6:margin=6:color=white", '-frames:v', '1', '-q:v', '3',
        os.path.join(a.carpeta, 'cola.jpg')])
with open(os.path.join(a.carpeta, 'hoja.txt'), 'w') as f:
    f.write('\n'.join(indice) + '\n')
shutil.rmtree(tmp)
print(f'{len(fotos)} fotos en {math.ceil(len(fotos) / POR_HOJA)} hojas. Últimos {a.cola} cuadros en cola.jpg.')
