# Transcribe el audio editado tramo por tramo. Escribe palabras.json y marca errores de toma.
# Whisper sobre el audio entero junta las frases repetidas y corre palabras. Tramo por tramo, no.
# Uso: python3 transcribir.py carpeta [--idioma es] [--guion guion.txt]
# Marca:
#   REPITE    un tramo arranca con palabras que ya dijo uno de los dos tramos anteriores.
#   ARRANQUE  un tramo corto es el comienzo del tramo siguiente ("para- / parafraseando").
#   CORTA     un tramo de menos de 0,35 s con voz puede partir una palabra.
#   FALTA     una frase del guion no aparece en el audio.
import argparse, json, os, re, tempfile, unicodedata
from comun import correr, modelo

p = argparse.ArgumentParser()
p.add_argument('carpeta')
p.add_argument('--idioma', default='es')
p.add_argument('--guion')
a = p.parse_args()
m = modelo()
if not m:
    raise SystemExit('Falta el modelo de whisper. Corré revisar_entorno.py.')
with open(os.path.join(a.carpeta, 'cortes.json')) as f:
    cortes = json.load(f)
audio = os.path.join(a.carpeta, 'editado16k.wav')
dtw = ['-dtw', 'large.v3.turbo'] if 'large-v3-turbo' in m else []
tmp = tempfile.mkdtemp()
norm = lambda w: ''.join(c for c in unicodedata.normalize('NFD', w.lower()) if c.isalnum())
# Whisper inventa estas frases sobre los silencios.
INVENTADO = r'[\W]*(gracias.*|subt[ií]tulos.*|cc .*|música|\[.*\])?[\W]*'

palabras, tr = [], []
for i, c in enumerate(cortes):
    wav = os.path.join(tmp, 't.wav')
    correr(['ffmpeg', '-v', 'error', '-y', '-ss', f"{c['ed_a']:.3f}", '-t', f"{c['ed_b'] - c['ed_a']:.3f}", '-i', audio,
            '-af', 'apad=pad_dur=0.4', wav])
    base = os.path.join(tmp, 't')
    correr(['whisper-cli', '-m', m, '-l', a.idioma, '-f', wav, '-ojf', '-ml', '1', '-sow', '-np', '-of', base] + dtw,
           capture_output=True)
    with open(base + '.json', errors='replace') as f:
        seg = json.load(f)['transcription']
    texto = ' '.join(' '.join(s['text'] for s in seg).split())
    if re.fullmatch(INVENTADO, texto.lower()):
        seg, texto = [], ''
    for s in seg:
        w = s['text'].strip()
        if not w or w.startswith('['):
            continue
        ini = c['ed_a'] + s['offsets']['from'] / 1000
        fin = min(c['ed_b'], c['ed_a'] + s['offsets']['to'] / 1000)
        palabras.append({'p': w, 'a': round(ini, 3), 'b': round(max(fin, ini + .03), 3), 'tramo': i})
    crudo_a, crudo_b = c['ed_a'] + c['off'], c['ed_b'] + c['off']
    tr.append((crudo_a, crudo_b, texto, [norm(w) for w in texto.split() if norm(w)]))
    print(f'{i:2d} crudo {crudo_a:7.2f}–{crudo_b:7.2f} ({crudo_b - crudo_a:4.2f} s)  {texto}')
with open(os.path.join(a.carpeta, 'palabras.json'), 'w') as f:
    json.dump(palabras, f, ensure_ascii=False, indent=0)

print()
alertas = 0
for i in range(1, len(tr)):
    x, y, t, w = tr[i]
    if not w:
        continue
    hecho = False
    for j in (i - 1, i - 2):
        if j < 0 or hecho:
            continue
        pw = tr[j][3]
        for n in range(min(6, len(w)), 1, -1):
            if any(pw[k:k + n] == w[:n] for k in range(len(pw) - n + 1)):
                print(f'REPITE   tramo {i} repite "{" ".join(w[:n])}" del tramo {j} → probá --quitar {tr[j][0]:.2f}-{tr[i][0]:.2f}')
                alertas += 1
                hecho = True
                break
    if i + 1 < len(tr) and len(w) <= 3 and y - x < 1.3 and tr[i + 1][3]:
        nx = tr[i + 1][3]
        pref = lambda u, v: len(os.path.commonprefix([u, v]))
        if pref(''.join(w), nx[0]) >= 4 or all(u == v or v.startswith(u) for u, v in zip(w, nx)):
            print(f'ARRANQUE tramo {i} ("{t}") es el comienzo del tramo {i + 1} → probá --quitar {x:.2f}-{tr[i + 1][0]:.2f}')
            alertas += 1
    if y - x < .35:
        print(f'CORTA    tramo {i} dura {y - x:.2f} s con "{t}"')
        alertas += 1
if a.guion:
    with open(a.guion) as f:
        guion = f.read()
    dicho = [norm(x) for x in ' '.join(x[2] for x in tr).split()]
    for frase in re.split(r'[.:?!]\s+', guion):
        fw = [norm(x) for x in frase.split() if norm(x)]
        if len(fw) < 4:
            continue
        mejor = max(sum(1 for x in fw if x in set(dicho[k:k + len(fw) + 4])) / len(fw)
                    for k in range(max(1, len(dicho) - len(fw))))
        if mejor < .6:
            print(f'FALTA    "{frase.strip()[:70]}" ({mejor:.0%} de las palabras)')
            alertas += 1
print(f'{alertas} alertas')
