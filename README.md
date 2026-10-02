# Avisos SAS por Telegram

Vigila la página de Enfermero/a del Concurso de Traslado 2025 del SAS y avisa por Telegram cuando aparece un PDF nuevo.

## Configuración rápida

1. Crea un repositorio en GitHub y sube todos estos archivos.
2. En `Settings -> Secrets and variables -> Actions -> New repository secret`, crea:
   - `TELEGRAM_BOT_TOKEN`: el token de BotFather.
   - `TELEGRAM_CHAT_ID`: tu chat_id.
3. Ve a `Actions` → `Vigilar documentos SAS` → `Run workflow` y ejecútalo una vez.
4. La primera ejecución crea la línea base y no avisa de los documentos que ya existen.
5. Después, el workflow comprueba la página cada 15 minutos y avisa si aparece un PDF nuevo.

**Nunca pongas el token directamente en un archivo del repositorio.**

Página vigilada:
https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/profesionales/traslados/cuadro-de-evolucion-del-concurso-de-traslado-2025/enfermeroa
