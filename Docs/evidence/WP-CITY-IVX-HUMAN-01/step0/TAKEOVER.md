# Paso 0 — toma de control técnica (2026-10-03)

Worker: Claude (Opus 5.5), worktree `C:\Users\Usuario\juego-def-wt\city`, rama `worker/city-skeleton-00`, Unity
`JuegoDef@bcca777e` (`Application.dataPath` = `C:/Users/Usuario/juego-def-wt/city/Unity/JuegoDef/Assets`).

## Cadena completada

| Paso | Resultado |
|---|---|
| `python Tools/city_ivanix/tools/dc_textures.py` | `{'ok': 56} of 56` |
| `CityDcPlus.Convert()` | `materials=250 (new 0) renderers=34530 missing_painted_textures=0` (quita la viñeta del volumen, como manda el estilo) |
| `CityPaving.Apply()` | `map=4320x2680 classes=11 renderers=143` |
| `CityIvanixNav.BakeAndProbe(true)` | `tris=12076 bake=5.2s complete=18/18` → `step0/NAV_PROBE.json` |
| `CityIvanixLint.Run()` | `clean` → `step0/LINT.json` |

## Verificación del WIP `bca8d27`

Auditorías escritas de nuevo para medir lo que motivó cada arreglo (muestreo OBB sobre los bounds locales de malla):

| Arreglo | Antes (auditoría del paseo 2026-10-02) | Ahora |
|---|---|---|
| Barandillas laterales de balcón contra esquinales | 50 | 46 laterales; 12 tocan esquinal, **todas en el anclaje a la pared** (11 a ≤ 0,1 m del muro, 1 a 0,1–0,2 m: la barandilla se fija contra el saliente de la piedra). 0 cortes a más de 0,2 m. |
| Barandillas laterales contra el balcón de hierro vecino | 11 | 2, ambas en `R0156` (fuera del corte) → `FUERA_DEL_CORTE.md` |
| Piezas de barandilla del paseo contra sillería o papeleras | 71 | 708 barras / 356 postes; **0 contra sillería**; 7 barras tocan mobiliario (3 papeleras, 2 bancos, 2 juegos de terraza), ninguna dentro del corte → `FUERA_DEL_CORTE.md` |
| Añadidos de fachada bajo rótulos, banderolas o toldos | (motivo del arreglo) | 336 rótulos/banderolas/toldos, 338 añadidos: **0 intersecciones** |

## Congelado

- `.gitattributes`: `Scenes/CITY_IVX/*.unity` y `CITY_IVX_NavMesh.asset` en LFS (como `ENV01_AUTHORED.unity`).
- `CityIvanixSeed.Frozen` + `RefuseIfFrozen`: `Seed`, `Dress` y `CityShopfronts.Apply` lanzan `JD_CITY_IVX_FROZEN`
  aunque se borren las escenas (comprobado en el editor: los tres se niegan).
- Nota de guardia en `Tools/city_ivanix/README.md` (sección *Frozen*).
- Todo asset propio que referencian las escenas está versionado; lo no versionado son GC2 y Quaternius provisionados
  (igual que `ENV01_AUTHORED`).

SHA-256 de las escenas congeladas:

```
8c4d06d8c3777ece3bfe4df8eb3715fb43e006c329102f055bc06f5de5a73fad  CITY_IVX_Base.unity
ce2de70bdf25fec4790fe904286849b8226c01068ff6567aa6161ec905967dac  CITY_IVX_Buildings.unity
70d912308557e2cc4b6c87d0b4cddfb44dde8e1fba62938d9c3b2d9cb25535b4  CITY_IVX_Props.unity
6b674ea08bf117028d85ee132c7305bec00e79de22b32e194094b159855a32aa  CITY_IVX_NavMesh.asset
```

Fuera del commit, a propósito: el ruido de reserialización de `Derived/ENV/*` y `Authored/ENV01/*` y `Scenes/CITY/*`
(esqueleto del track Mapa F1, no de este WP).
