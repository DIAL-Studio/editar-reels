# Arma subtitulos.ass desde palabras.json y estilo.json. Lista cada subtítulo para leerlo.
# Uso: python3 subtitulos.py carpeta estilo.json [--alto 1920] [--ancho 1080]
import argparse, json, os, re

p = argparse.ArgumentParser()
p.add_argument('carpeta')
p.add_argument('estilo')
p.add_argument('--ancho', type=int, default=1080)
p.add_argument('--alto', type=int, default=1920)
a = p.parse_args()
with open(a.estilo) as f:
    E = json.load(f)
with open(os.path.join(a.carpeta, 'palabras.json')) as f:
    palabras = json.load(f)
CHICAS = set(E.get('chicas', []))
limpiar = lambda w: re.sub(r'^[^\wáéíóúüñ¿¡%"“]+|[^\wáéíóúüñ?!%"”]+$', '', w, flags=re.I)


def color(h, alfa=0):
    h = h.lstrip('#')
    return f'&H{alfa:02X}{h[4:6]}{h[2:4]}{h[0:2]}'.upper()


def texto(w):
    t = E.get('correcciones', {}).get(limpiar(w), limpiar(w)) if E.get('sacar_puntuacion', True) else w
    modo = E.get('mayusculas', 'normal')
    return t.upper() if modo == 'mayuscula' else t.lower() if modo == 'minuscula' else t


# Agrupa palabras. Corta después de una pausa de puntuación o al llegar al límite.
grupos, g = [], []
for i, w in enumerate(palabras):
    g.append(w)
    sig = palabras[i + 1] if i + 1 < len(palabras) else None
    letras = sum(len(x['p']) for x in g) + (len(sig['p']) + 1 if sig else 0)
    fin_frase = re.search(r'[,.;:?!]$', w['p']) is not None
    lleno = len(g) >= E.get('palabras', 3) or letras > E.get('letras', 23)
    cambio_tramo = sig is not None and sig.get('tramo') != w.get('tramo')
    if sig is None or fin_frase or lleno or cambio_tramo:
        # Una palabra chica va con la que sigue.
        if lleno and not fin_frase and sig is not None and len(g) > 1 and limpiar(g[-1]['p']).lower() in CHICAS:
            resto = [g.pop()]
            grupos.append(g)
            g = resto
        else:
            grupos.append(g)
            g = []
if g:
    grupos.append(g)

# Una palabra sola y breve se une al subtítulo anterior si entra.
unidos = []
for g in grupos:
    corta = len(g) == 1 and g[0]['b'] - g[0]['a'] < E.get('minimo', .5)
    if corta and unidos and sum(len(x['p']) for x in unidos[-1]) + len(g[0]['p']) < E.get('letras', 23) \
            and not re.search(r'[.?!]$', unidos[-1][-1]['p']):
        unidos[-1] = unidos[-1] + g
    else:
        unidos.append(g)


def hora(t):
    t = max(0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


d = E.get('destacar', {})
marcadas = {x.lower() for x in d.get('palabras', [])}
filas = []
for i, g in enumerate(unidos):
    ini = g[0]['a'] + E.get('retraso', .05)
    fin = g[-1]['b'] + .08
    if i + 1 < len(unidos):
        sig = unidos[i + 1][0]['a'] + E.get('retraso', .05)
        fin = sig if sig - fin < .2 else min(fin, sig)
    partes = []
    for w in g:
        t = texto(w['p'])
        if t.lower() in marcadas:
            t = '{\\c' + color(d.get('color', '#FF3B30')) + '&}' + t + '{\\r}'
        partes.append(t.replace('{\\c', '\0').replace('{', '').replace('\0', '{\\c'))
    filas.append((ini, fin, ' '.join(partes)))

margen = a.alto - E.get('base', 1168)
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {a.ancho}
PlayResY: {a.alto}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{E.get('fuente', 'Arial')},{E.get('tamano', 82)},{color(E.get('color', '#FFFFFF'))},&H000000FF,{color(E.get('borde_color', '#141416'))},{color(E.get('sombra_color', '#141416'), 96)},{-1 if E.get('negrita', True) else 0},0,0,0,100,100,{E.get('interletra', 0)},0,1,{E.get('borde', 3)},{E.get('sombra', 2)},2,60,60,{margen},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for ini, fin, t in filas:
    ass += f'Dialogue: 0,{hora(ini)},{hora(fin)},Base,,0,0,0,,{t}\n'
    print(f'{ini:6.2f}–{fin:6.2f}  {re.sub(r"{[^}]*}", "", t)}')
with open(os.path.join(a.carpeta, 'subtitulos.ass'), 'w') as f:
    f.write(ass)
print(f'{len(filas)} subtítulos. Leé cada línea antes de armar.')
