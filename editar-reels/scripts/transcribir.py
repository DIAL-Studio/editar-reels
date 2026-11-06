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
p.add_argument('--motor', choices=['python', 'cpp'], default='python')
p.add_argument('--modelo', help='Modelo de Whisper Python o ruta al modelo GGML de whisper.cpp')
p.add_argument('--model-dir', help='Directorio de modelos de Whisper Python')
p.add_argument('--device', default='cpu', help='Dispositivo de Whisper Python (por defecto: cpu)')
a = p.parse_args()
if a.motor == 'python':
    try:
        import whisper
    except ImportError as exc:
        raise SystemExit('Falta openai-whisper. Ejecutá este script con el Python donde está instalado.') from exc
    whisper_model = whisper.load_model(a.modelo or 'small', device=a.device, download_root=a.model_dir)
else:
    m = a.modelo or modelo()
    if not m or not os.path.isfile(os.path.expanduser(m)):
        raise SystemExit('Falta el modelo GGML de whisper.cpp. Usá --modelo o WHISPER_MODEL.')
    m = os.path.expanduser(m)
with open(os.path.join(a.carpeta, 'cortes.json')) as f:
    cortes = json.load(f)
audio = os.path.join(a.carpeta, 'editado16k.wav')
dtw = ['-dtw', 'large.v3.turbo'] if a.motor == 'cpp' and 'large-v3-turbo' in m else []
tmp = tempfile.mkdtemp()
norm = lambda w: ''.join(c for c in unicodedata.normalize('NFD', w.lower()) if c.isalnum())
# Whisper inventa estas frases sobre los silencios.
INVENTADO = r'[\W]*(gracias.*|subt[ií]tulos.*|cc .*|música|\[.*\])?[\W]*'

palabras, tr = [], []
for i, c in enumerate(cortes):
    wav = os.path.join(tmp, 't.wav')
    correr(['ffmpeg', '-v', 'error', '-y', '-ss', f"{c['ed_a']:.3f}", '-t', f"{c['ed_b'] - c['ed_a']:.3f}", '-i', audio,
            '-af', 'apad=pad_dur=0.4', wav])
    if a.motor == 'python':
        result = whisper_model.transcribe(wav, language=a.idioma, word_timestamps=True,
                                          fp16=a.device != 'cpu', verbose=False)
        texto = ' '.join(result['text'].split())
        items = [{'text': word['word'], 'start': word['start'], 'end': word['end']}
                 for segment in result['segments'] for word in segment.get('words', [])]
    else:
        base = os.path.join(tmp, 't')
        correr(['whisper-cli', '-m', m, '-l', a.idioma, '-f', wav, '-ojf', '-ml', '1', '-sow', '-np', '-of', base] + dtw,
               capture_output=True)
        with open(base + '.json', errors='replace') as f:
            segments = json.load(f)['transcription']
        texto = ' '.join(' '.join(segment['text'] for segment in segments).split())
        items = [{'text': segment['text'], 'start': segment['offsets']['from'] / 1000,
                  'end': segment['offsets']['to'] / 1000} for segment in segments]
    if re.fullmatch(INVENTADO, texto.lower()):
        items, texto = [], ''
    for item in items:
        w = item['text'].strip()
        if not w or w.startswith('['):
            continue
        ini = max(c['ed_a'], c['ed_a'] + item['start'])
        fin = min(c['ed_b'], c['ed_a'] + item['end'])
        if ini >= c['ed_b']:
            continue
        palabras.append({'p': w, 'a': round(ini, 3),
                         'b': round(min(c['ed_b'], max(fin, ini + .03)), 3), 'tramo': i})
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
