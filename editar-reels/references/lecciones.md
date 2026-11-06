# Lecciones de edición

Estos errores aparecieron editando reels reales. Valen para cualquier creador.

## Voz y cortes

- Whisper sobre el audio entero junta las frases repetidas. Transcribí tramo por tramo. `transcribir.py` ya lo hace.
- Whisper inventa texto sobre los silencios. Antes de sacar una toma, medí la energía del audio en ese tramo.
- Una frase dicha en voz baja puede caer debajo del umbral. Compará cada frase con el guion.
- Un corte puede comerse el final de una palabra. Medí el volumen en ventanas de 50 ms después del corte. Si sigue alto, alargá el tramo.
- Una persona a veces repite solo el remate o una pregunta corta. Escuchá esas frases aunque no haya alerta.
- Whisper ubica mal las palabras después de un silencio largo. Transcribí el audio editado, no el crudo.
- Un plano a cámara cerca de un corte puede mostrar un destello de otra toma. Mové el borde del plano al corte.
- El final del crudo suele mostrar a la persona yendo a apagar la cámara. Mirá siempre `cola.jpg`.

## Pantalla

- Una zona negra o vacía grande es un error. Revisá cada plano en la hoja de cuadros.
- Una captura más ancha que alta no llena el 9:16. Pegala sobre una página alta o acercá la parte que nombra la voz.
- Muchos clips 4:3 traen bandas negras dentro de un 16:9. Medí el área útil y recortá.
- Un resalte debajo del subtítulo no se lee. Subí el contenido antes de armar.
- Elegí el momento de un clip por su diálogo, no por el nombre del archivo.

## Subtítulos

- La letra blanca se pierde sobre fondos claros y ropa con rayas. Probá el borde sobre esos cuadros.
- Un borde muy marcado también molesta. Mostrá alternativas sobre cuadros reales.
- Whisper pone tilde de más en cómo, qué, cuándo y dónde. Leé cada línea.
- Whisper entiende mal marcas y nombres. Guardalos en `correcciones` de `estilo.json`.
- Una palabra sola y breve parpadea. Juntala con la anterior.

## Imagen de la cámara

- Una grabación HDR de celular sale lavada o quemada si la tratás como SDR. `cortar_silencios.py` la convierte.
- Un color medido para una cámara no sirve para otra.
- Una cámara puede repetir o congelar cuadros. Si la cara se traba, tapá ese tramo con un inserto o pedí regrabar la frase.

## Audio

- Instagram no publica una cifra de volumen. Las guías para Reels y TikTok usan −14 LUFS como referencia.
- Subir solo la ganancia satura los picos. Nivelá con `armar.py`.

## Render

- Dos procesos en la misma carpeta de trabajo pueden chocar. Corré un armado por vez.
- En animaciones, un índice negativo en JavaScript rompe un solo cuadro. Normalizá con `((n % m) + m) % m`.
- Cambiá el nombre de la salida en cada versión. Una corrección nunca pisa lo ya entregado.
