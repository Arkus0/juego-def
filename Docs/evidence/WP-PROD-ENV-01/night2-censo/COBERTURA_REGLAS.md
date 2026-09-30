# Lote C — cobertura regla vs ojo (censo final 356 imgs)

Metodo: un defecto del censo (ojo) queda 'cazado' si existe un hallazgo de la regla dentro del cono de vision de su captura (42 grados, 34 m).

| regla | clase del ojo | caza | cobertura | nota |
|---|---|---|---|---|
| PAVE_MISSING | SUELO_PAVE_MISSING | 12/146 | 8% | regla muestrea eje + bordes de calle y plazas; el ojo tambien lee como falta pavimento las transiciones a hierba en salidas y patios |
| GROUND_DIRT_IN_STREET | SUELO_DIRT | 0/177 | 0% | regla solo caza decals ENV_Stain_Quad planos (0 hoy: las manchas que ve el ojo viven en las TEXTURAS de pavimento viejo, no en quads) |
| TEX_WRONG_SURFACE | TEX_WRONG | 0/215 | 0% | regla caza material ENV_Pave_* fuera del suelo (0 hoy: los 215 del ojo son estirados UV / lectura, no material equivocado) |
| VEG_CLIP | VEG_CLIP | 104/307 | 34% | regla caza interseccion fisica vegetacion-estructura; el ojo suma clones y plantas pegadas a muro sin tocar |
| SEAM_NO_KERB | SUELO_SEAM | 214/318 | 67% | regla caza todo cambio de material pavimento-pavimento sin pieza de borde; franja central de la espina incluida (por diseno alli, kerb opcional) |
| PROP_LOGIC | PROP_LOGIC | 137/298 | 46% | regla caza asiento-mirando-muro, prop-dentro-de-prop y parasol sin mesa |
| WALL_PURPOSE | ESTRUCTURA | 24/164 | 15% | regla caza extremos sueltos de muros/parapets/rails; ESTRUCTURA del ojo es mas ancha (escalera al agua, aros, agua-muro) |

Conclusion: las reglas mecanicas cazan bien SEAM (67%), PROP_LOGIC (~50%) y VEG_CLIP (~35%); PAVE/TEX/DIRT quedan clases de-ojo: su senal no es material ni quad sino textura/UV/lectura. El censo visual manda; las reglas son el segundo par de ojos.