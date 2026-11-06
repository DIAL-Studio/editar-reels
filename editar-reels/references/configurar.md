# Configurar el skill

Entrevistá al usuario. Completá `preferencias.md` y `estilo.json` con sus respuestas.

## Reglas de la entrevista

- Hacé un bloque por mensaje, con 3 preguntas como máximo.
- Ofrecé opciones concretas y un valor sugerido.
- Aceptá "no sé" o "elegí vos". Usá el valor sugerido y marcalo "(sugerido)".
- Guardá cada bloque al terminarlo. Así la entrevista se puede cortar y retomar.
- Copiá la frase del usuario cuando exprese un gusto fuerte.
- Reemplazá cada `[COMPLETAR]`. No dejes campos sin responder.
- Si el usuario pide "hacelo igual", usá los valores sugeridos y pasá a la prueba.

## Bloques

### 1. Contenido

- ¿De qué hablan tus reels, y en qué idioma?
- ¿Cómo grabás: celular, cámara, teleprompter o improvisado?

### 2. Referencia

Este bloque responde muchos de los siguientes.

- Pedí hasta 3 videos que el usuario quiera igualar.
- Medilos con `references/medir-referencia.md`.
- Mostrale lo que encontraste. Preguntá qué quiere copiar y qué no.

### 3. Formatos

- ¿Qué tipos de reel hacés? Ejemplos: tutorial, noticia, opinión, reseña.
- Por cada tipo, ¿cómo es el gancho, el cuerpo y el cierre?

Guardá de 1 a 4 formatos. Si el usuario no sabe, empezá con uno solo.

### 4. Cortes

Ofrecé tres ritmos:

| Ritmo | `--min` | `--aire` |
|---|---|---|
| Tranquilo | 0,60 | 0,20 |
| Medio | 0,35 | 0,15 |
| Picado | 0,25 | 0,10 |

- ¿Qué muletillas se sacan?
- ¿Qué pausas o muletillas son parte de tu estilo y quedan?

### 5. Subtítulos

- ¿Llevan subtítulos?
- ¿Qué fuente, tamaño, color y altura? Si hay un video medido, proponé esos valores.
- ¿Cuántas palabras por subtítulo? ¿Mayúsculas o minúsculas? ¿Marcan una palabra del gancho?

Guardá los valores exactos en `estilo.json`.

### 6. Imagen en pantalla

- ¿Qué lleva cada formato: capturas, clips, animaciones o memes?
- ¿Cuánto se ve tu cara? ¿Cómo es el plano del cierre?
- ¿Qué colores y tipografías usás? ¿Qué no querés ver nunca?

### 7. Audio

- ¿Volumen? Sugerí −14 LUFS.
- ¿Música? ¿Efectos de sonido?

### 8. Autonomía y entrega

- ¿Dónde está el material de cada reel? ¿Dónde va el reel terminado?
- ¿Qué puede hacer Claude sin preguntar? ¿Qué tiene que consultar siempre?
- ¿Cómo marcás los cambios? ¿Cuánto detalle querés en el mensaje de entrega?

Preguntá siempre por el material de terceros. El usuario decide qué tiene permiso de usar.

## Prueba

1. Pedí una grabación de unos 30 segundos.
2. Editala con el flujo de `SKILL.md`. Dejá las animaciones para más adelante.
3. Avisale al usuario: "La primera versión va a tener errores. Marcá cada uno. Cada error se vuelve una regla."
4. Seguí el paso "Corregir y aprender" de `SKILL.md`.
