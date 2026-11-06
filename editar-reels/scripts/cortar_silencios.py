# Saca los silencios de la grabación. Escribe editado.mp4, editado16k.wav y cortes.json.
# Uso: python3 cortar_silencios.py grabacion.mp4 carpeta [--min 0.25] [--aire 0.10] [--quitar 12.0-15.5,40-41]
# --min: silencio más corto que se corta. --aire: silencio que queda a cada lado del corte.
# --quitar: tramos de la grabación que se sacan enteros, por ejemplo tomas malas.
# Reencuadra a 9:16 sin bandas. Si la grabación es HDR, la pasa a SDR.
import argparse, array, json, os, subprocess, wave
from comun import correr, sondear

p = argparse.ArgumentParser()
p.add_argument('grabacion')
p.add_argument('carpeta')
p.add_argument('--min', type=float, default=.25)
p.add_argument('--aire', type=float, default=.10)
p.add_argument('--quitar', default='')
p.add_argument('--ancho', type=int, default=1080)
p.add_argument('--alto', type=int, default=1920)
p.add_argument('--fps', type=int, default=30)
a = p.parse_args()
os.makedirs(a.carpeta, exist_ok=True)

# Energía del audio en ventanas de 20 ms.
crudo = os.path.join(a.carpeta, 'grabacion16k.wav')
correr(['ffmpeg', '-v', 'error', '-y', '-i', a.grabacion, '-ar', '16000', '-ac', '1', crudo])
with wave.open(crudo) as w:
    m = array.array('h')
    m.frombytes(w.readframes(w.getnframes()))
SR, VENTANA = 16000, 320
dur = len(m) / SR
e = []
for i in range(0, len(m) - VENTANA, VENTANA):
    e.append((sum(x * x for x in m[i:i + VENTANA]) / VENTANA) ** .5 / 32768)
if not e:
    raise SystemExit('La grabación no tiene audio.')
orden = sorted(e)
umbral = min(max(.006, orden[int(len(orden) * .3)] * 1.6), orden[-1] * .25)

# Silencios más largos que --min. El silencio del comienzo se saca siempre.
silencios, inicio = [], None
for i, valor in enumerate(e + [1.0]):
    if valor < umbral and inicio is None:
        inicio = i
    if valor >= umbral and inicio is not None:
        x, y = inicio * .02, i * .02
        if y - x >= a.min or x == 0:
            silencios.append((x, y))
        inicio = None

# Tramos que quedan.
tramos, t = [], 0.0
for x, y in silencios:
    if x == 0:
        t = max(0, y - .05)
        continue
    tramos.append((t, min(dur, x + a.aire)))
    t = max(x + a.aire, y - a.aire)
# Sin cola al final: evita mostrar a la persona yendo a apagar la cámara.
if not silencios or silencios[-1][1] < dur - .05:
    tramos.append((t, dur))
elif tramos:
    tramos[-1] = (tramos[-1][0], min(dur, silencios[-1][0] + .35))

for desde, hasta in (tuple(map(float, r.split('-'))) for r in a.quitar.split(',') if r):
    nuevos = []
    for x, y in tramos:
        if y <= desde or x >= hasta:
            nuevos.append((x, y))
            continue
        if x < desde:
            nuevos.append((x, desde))
        if y > hasta:
            nuevos.append((hasta, y))
    tramos = nuevos

# Cada corte cae en un cuadro. Así el video y el audio miden lo mismo en cada tramo.
FPS = a.fps
tramos = [(round(x * FPS) / FPS, round(y * FPS) / FPS) for x, y in tramos]
tramos = [(x, y) for x, y in tramos if y - x > .06]
if not tramos:
    raise SystemExit('No quedó ningún tramo con voz.')

cortes, ed = [], 0.0
for x, y in tramos:
    cortes.append({'ed_a': round(ed, 3), 'ed_b': round(ed + y - x, 3), 'off': round(x - ed, 3)})
    ed += y - x
with open(os.path.join(a.carpeta, 'cortes.json'), 'w') as f:
    json.dump(cortes, f, indent=1)

# HDR de celular: se pasa a SDR una sola vez.
video = next(s for s in sondear(a.grabacion)['streams'] if s['codec_type'] == 'video')
hdr = ''
if video.get('color_transfer') in ('arib-std-b67', 'smpte2084'):
    print('HDR detectado: paso la grabación a SDR.')
    hdr = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,'
           'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,')

eps = 1 / (2 * FPS)
sel = '+'.join(f'gte(t,{x - eps:.4f})*lt(t,{y - eps:.4f})' for x, y in tramos)
n = len(tramos)
grafo = [f"[0:v]fps={FPS},select='{sel}',setpts=N/{FPS}/TB,{hdr}"
         f"scale={a.ancho}:{a.alto}:force_original_aspect_ratio=increase,crop={a.ancho}:{a.alto},setsar=1[v]"]
salidas = ''.join(f'[s{i}]' for i in range(n))
grafo.append(f'[0:a]aresample=48000,asplit={n}{salidas}' if n > 1 else '[0:a]aresample=48000[s0]')
for i, (x, y) in enumerate(tramos):
    grafo.append(f'[s{i}]atrim={x:.4f}:{y:.4f},asetpts=PTS-STARTPTS[b{i}]')
entradas = ''.join(f'[b{i}]' for i in range(n))
grafo.append(f'{entradas}concat=n={n}:v=0:a=1[a]')
editado = os.path.join(a.carpeta, 'editado.mp4')
correr(['ffmpeg', '-v', 'error', '-y', '-i', a.grabacion, '-filter_complex', ';'.join(grafo), '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-crf', '16', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', editado])
correr(['ffmpeg', '-v', 'error', '-y', '-i', editado, '-ar', '16000', '-ac', '1', os.path.join(a.carpeta, 'editado16k.wav')])
os.remove(crudo)
print(f'{n} tramos, {dur:.2f} s crudos → {ed:.2f} s editados')
