# PSX DEMO — handoff para el equipo (2026-10-06)

**Qué es:** la demo jugable del pueblo (CITY_B) con acabado PS1+/Dreamcast, lista para enseñar.
**Dónde:** proyecto Unity del worktree `city` (`C:/Users/Usuario/juego-def-wt/city`), rama `worker/psx-demo-01`.

## Cómo abrirla (2 minutos)

1. Abrir el proyecto `city` en Unity.
2. Abrir la escena `Assets/JuegoDef/Scenes/CITY_B/CITY_B_PS1_DEMO.unity`.
3. Dar a **Play**. El bootstrap carga solo las capas `CITY_B_Buildings` (269 fachadas) y `CITY_B_Props` (mercado, mobiliario, vecinos).
4. WASD para andar, ratón para orbitar la cámara. El spawn es la entrada sur de la Plaza Mayor.

Si la escena demo no existiera (es artefacto local, la carpeta `Scenes/CITY_B/` está excluida de git por decisión del Owner), se regenera con el menú **JuegoDef/CITY/PSX Demo: build demo scene** (crea la copia de `CITY_B_Base` y aplica toda la configuración: raster, luz, cámara, bootstrap, spawn).

## Qué se arregló (la escena "era una mierda" por tres causas apiladas)

1. **Pueblo fantasma:** CITY_B es un stack multi-escena (Base + Buildings + Props). Con solo `CITY_B_Base` abierta se ve el terreno y los muros, sin pueblo. El demo-bootstrap carga las capas al Play.
2. **Cámara bajo el terreno:** el solucionador de colisión del shot GC2, con calles estrechas, empujaba la cámara **bajo el suelo de la plaza** (y = −0,5); desde ahí los suelos muestran backfaces y se ve el cielo → "suelo blanco". Sustituido por `PSXDemoCamera` (órbita 3ª persona con sphere-cast y clamp de suelo). El shot GC2 sigue intacto en `CITY_B_Base`.
3. **Luz sobreexpuesta:** sol 0,92 × sunGain 1,12 + ambiente cielo 1,18 superaba 1,0 y el RT LDR (ARGB32, sin tonemapping) recortaba a blanco puro toda superficie al sol. Rebalanceada a rango LDR (sol 0,82 ámbar elev 24° az 238°; CityLook sunGain 1,0, cielo 0,98, rebote 0,58; Suelo `_SunScale` 0,72). La fog de escena quedó desactivada: los materiales PSX ya traen su bruma Atlántica por material.

Además: raster nítido 480×360 con point filtering y sin MSAA (el 640×480 bilinear leía a VGA borroso), y el player spawneaba/teletransportaba mal porque el pivot del Character GC2 es el **centro de la cápsula** (suelo + 0,98 m), no los pies.

## Ficheros (rama `worker/psx-demo-01`)

- `Runtime/City/PSXDemoCamera.cs` — cámara 3ª persona orbital con colisión y auto-alineado.
- `Runtime/City/PSXDemoBootstrap.cs` — carga aditiva de Buildings+Props al Play (idempotente).
- `Runtime/City/PSXDemoWalkTest.cs` — auto-walk de verificación (W anda a mano). Herramienta dev.
- `Editor/City/PSXDemoBuild.cs` — menú que construye/configura la escena demo desde `CITY_B_Base`.
- `City/StyleB/Materials/Suelo.mat` — `_SunScale` 0,86 → 0,72 (balance LDR; afecta también a Base, es intencional).

## Estado de la escena privada (local)

- `CITY_B_PS1_DEMO.unity` creada y verificada (spawn, 3 capas, cámara, luz).
- Backup previo: tag git `backup/city-b-pre-ps1-20261005` (HEAD 7c8c575) + copia física en `Backup/CITY_B_pre_PS1_20261005/` (escenas + diff del working tree, 295 ficheros de otro trabajo que NO se han tocado).
- `CITY_B_Base.unity` y las capas Buildings/Props: **sin modificar**.

## Verificado en Play Mode

- Spawn en plaza asentado (y estable 10,70), 3 escenas cargadas, cámara sigue con colisión.
- Caminata real 17 m por la Calle Mayor cuesta abajo (blend de andar activo, colisión y pendiente OK).
- Capturas del recorrido en `Assets/Screenshots/` (gitignored, evidencia local): plaza, fuente, mercado, Calle Mayor con mar al fondo.

## Siguientes pasos sugeridos (no hechos aquí a propósito)

- NPCs adicionales con `CityNPC` en el paseo de muralla y el muelle (la plaza ya tiene vida de la capa Props).
- Variante noche (hay exploración de look nocturno en el worktree principal, `night-20260931`).
- Si algún día la demo sale de local: añadir las 3 escenas a Build Settings (el bootstrap ya contempla el fallback por nombre).
