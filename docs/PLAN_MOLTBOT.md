# Plan MoltBot

## Objetivo
Conectar dos PCs Ubuntu con OpenClaw para que ambos puedan controlarse entre sí, con permisos elevados, app móvil, estado visual, automejora 24/7 e integraciones Drive/Gmail/GitHub.

## PCs
PC 1:
- Nombre futuro: enrique-pc
- Usuario: pendiente
- IP Tailscale: pendiente

PC 2:
- Nombre futuro: miki-pc
- Usuario: pendiente
- IP Tailscale: pendiente

## Estados app móvil
- Verde: terminado/libre
- Azul: trabajando
- Rojo: error
- Negro: apagado/no responde

## La app móvil debe mostrar
- Estado de cada PC
- Porcentaje real de mejora
- Qué está haciendo ahora
- Qué ha hecho
- Qué tiene pendiente
- Logs
- Botón activar automejora 24/7
- Botón pausar
- Botón forzar ciclo ahora

## Integraciones
Cuenta Google:
moltbot14@gmail.com

Debe poder:
- Leer Drive
- Subir archivos a Drive
- Borrar archivos de Drive con registro
- Leer Gmail
- Organizar Gmail
- Leer GitHub
- Subir cambios a GitHub
- Borrar archivos de GitHub solo con commit claro

## Reglas de seguridad
- No borrar credenciales.
- No borrar archivos importantes sin copia.
- No desactivar Tailscale.
- No desactivar SSH.
- No desactivar OpenClaw.
- No inventar porcentajes.
- Todo cambio debe quedar registrado.