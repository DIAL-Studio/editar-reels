# Medir un video de referencia

Convertí un gusto en números. Medí el estilo. No copies el contenido.

Pedile al usuario el archivo o un link. El usuario responde por el permiso de uso.

## Subtítulos

1. Sacá cuadros donde se vea un subtítulo, con un ancho real de 1080 px si podés.
2. Probá varias fuentes del sistema con el mismo texto. Superponé cada prueba con el cuadro y compará la coincidencia, palabra por palabra.
3. Medí el tamaño con el ancho de la tinta en tres textos distintos.
4. Medí la altura de la línea de base.
5. Medí el color con el promedio de los píxeles del texto.
6. Medí la sombra y el borde. Restá un cuadro vacío de un cuadro con texto.
7. Medí cuándo entra y sale cada subtítulo, en cuadros, contra la voz.
8. Contá las palabras por subtítulo. Anotá mayúsculas, puntuación y palabras marcadas.

Guardá los resultados en `estilo.json`.

Antes de armar un reel, mostrá 3 a 5 alternativas sobre cuadros difíciles: fondo claro, fondo oscuro y ropa con rayas. Así el usuario elige sin esperar un render completo.

## Ritmo

```bash
ffmpeg -i referencia.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -c pts_time
```

- Ese número es la cantidad de cortes de plano. Dividilo por los minutos del video.
- Medí cuánto dura cada plano a cámara.
- Calculá qué parte del video muestra la cara.

## Audio

```bash
ffmpeg -i referencia.mp4 -af loudnorm=print_format=json -f null - 2>&1 | tail -12
```

`input_i` es el volumen en LUFS.

## Estructura

1. Transcribí el video con whisper.
2. Marcá el gancho, los pasos o partes, los cortes a cámara y el cierre, con segundos.
3. Guardá esa estructura como un formato en `preferencias.md`.

Mostrale al usuario una tabla con lo medido. Preguntá qué quiere copiar. El usuario decide.
