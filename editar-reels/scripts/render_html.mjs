// Renderiza una animación HTML a MP4, cuadro por cuadro. Retoma desde los cuadros que ya existen.
// Uso: node render_html.mjs animacion.html salida.mp4 [ancho alto fps]
// El HTML define window.duracion (segundos) y window.dibujar(t). Cada cuadro depende solo de t.
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { existsSync, mkdirSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
let chromium;
try {
  ({ chromium } = createRequire(AQUI + '/')('playwright'));
} catch {
  console.error(`Falta Playwright. Instalalo con: cd "${AQUI}" && npm install && npx playwright install chromium`);
  process.exit(1);
}
const [html, mp4, W = 1080, H = 1920, FPS = 30] = process.argv.slice(2);
const dir = mp4 + '.cuadros';
mkdirSync(dir, { recursive: true });
const abrir = async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +W, height: +H } });
  await page.goto(pathToFileURL(path.resolve(html)).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  return { browser, page };
};
let { browser, page } = await abrir();
const N = Math.round((await page.evaluate(() => window.duracion)) * FPS);
if (!N) throw new Error('El HTML no define window.duracion.');
for (let i = 0; i < N; i++) {
  const salida = path.join(dir, String(i).padStart(5, '0') + '.png');
  if (existsSync(salida)) continue;
  for (let intento = 1; ; intento++) {
    try {
      await page.evaluate((t) => window.dibujar(t), i / FPS);
      await page.screenshot({ path: salida });
      break;
    } catch (e) {
      if (intento >= 4) throw e;
      try { await browser.close(); } catch {}
      ({ browser, page } = await abrir());
    }
  }
}
await browser.close();
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, '%05d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', mp4]);
rmSync(dir, { recursive: true });
console.log(`${mp4}: ${N} cuadros`);
