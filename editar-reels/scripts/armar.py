# Arma el reel desde plan.json: insertos, subtítulos y volumen.
# Uso: python3 armar.py plan.json [--final] [--pisar]
# Sin opciones comprime rápido para revisar. --final comprime mejor. --pisar permite reescribir una versión.
# Las rutas de plan.json son relativas a su carpeta. Formato:
# {
#   "base": "editado.mp4",
#   "salida": "reel-v1.mp4",
#   "subtitulos": "subtitulos.ass",
#   "fuentes": "carpeta/opcional",
#   "lufs": -14,
#   "insertos": [
#     {"desde": 3.2, "hasta": 6.1, "archivo": "animacion.mp4"},
#     {"desde": 8.0, "hasta": 10.5, "archivo": "clip.mp4", "t0": 12.0},
#     {"desde": 14.0, "hasta": 17.0, "archivo": "captura.png", "zoom": 1.08, "foco": [0.5, 0.3]}
#   ]
# }
import argparse, json, os, re, subprocess
from comun import correr, cuadros, duracion, sondear

p = argparse.ArgumentParser()
p.add_argument('plan')
p.add_argument('--final', action='store_true')
p.add_argument('--pisar', action='store_true')
a = p.parse_args()
os.chdir(os.path.dirname(os.path.abspath(a.plan)))
with open(os.path.basename(a.plan)) as f:
    P = json.load(f)
salida = P['salida']
if os.path.exists(salida) and not a.pisar:
    raise SystemExit(f'{salida} ya existe. Cambiá el nombre: -v2, -v3. Así no se pisa una versión entregada.')

v = next(s for s in sondear(P['base'])['streams'] if s['codec_type'] == 'video')
W, H = v['width'], v['height']
num, den = map(int, v['r_frame_rate'].split('/'))
FPS = round(num / den)
dur = duracion(P['base'])
IMAGENES = ('.png', '.jpg', '.jpeg', '.webp')

entradas = ['-i', P['base']]
grafo, previo = [], '[0:v]'
insertos = sorted(P.get('insertos', []), key=lambda x: x['desde'])
for i, x in enumerate(insertos, 1):
    largo = x['hasta'] - x['desde']
    if largo <= 0 or x['hasta'] > dur + .05:
        raise SystemExit(f"Inserto {x['archivo']}: tiempos fuera del reel ({x['desde']}–{x['hasta']}, reel {dur:.2f} s).")
    n = round(largo * FPS)
    if x['archivo'].lower().endswith(IMAGENES):
        entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f'{largo:.3f}', '-i', x['archivo']]
        z = x.get('zoom', 1.06)
        fx, fy = x.get('foco', [.5, .5])
        # Escala al doble para que el zoom lento no tiemble.
        filtro = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                  f"zoompan=z='1+{z - 1:.4f}*on/{n}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d=1:s={W}x{H}:fps={FPS}")
    else:
        entradas += ['-ss', f"{x.get('t0', 0):.3f}", '-t', f'{largo:.3f}', '-i', x['archivo']]
        filtro = f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}'
    grafo.append(f"[{i}:v]{filtro},setsar=1,format=yuv420p,setpts=PTS-STARTPTS+{x['desde']:.3f}/TB[i{i}]")
    grafo.append(f"{previo}[i{i}]overlay=eof_action=pass:repeatlast=0:enable='between(t,{x['desde']:.3f},{x['hasta'] - 1 / (2 * FPS):.3f})'[v{i}]")
    previo = f'[v{i}]'
if P.get('subtitulos'):
    extra = f":fontsdir={P['fuentes']}" if P.get('fuentes') else ''
    grafo.append(f"{previo}ass={P['subtitulos']}{extra}[vfin]")
    previo = '[vfin]'
elif not grafo:
    grafo.append('[0:v]null[vfin]')
    previo = '[vfin]'

# Volumen en dos pasadas: mide y después aplica.
L = P.get('lufs', -14)
norma = f'loudnorm=I={L}:TP=-1.5:LRA=11'
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', P['base'], '-af', norma + ':print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
m = json.loads(re.findall(r'\{[^{}]*\}', r)[-1])
grafo.append(f"[0:a]{norma}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
             f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000[a]")

temporal = salida + '.parcial.mp4'
correr(['ffmpeg', '-v', 'error', '-y'] + entradas + ['-filter_complex', ';'.join(grafo), '-map', previo, '-map', '[a]',
        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium' if a.final else 'veryfast', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', temporal])
os.replace(temporal, salida)

esperados, reales = cuadros(P['base']), cuadros(salida)
print(f'{salida}: {reales} cuadros, {duracion(salida):.2f} s')
if esperados != reales:
    print(f'CUADROS: esperaba {esperados} y salieron {reales}. Revisá la sincronía.')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', salida, '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
print(f"Volumen: {json.loads(re.findall(r'{[^{}]*}', r)[-1])['input_i']} LUFS, pedido {L}")
