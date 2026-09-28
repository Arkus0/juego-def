# B0 motion coverage

Demand: `Docs/design/FIRST_KEEPER_BLOCK_B0.md`. Admission is motion-level on regular male/female source bodies; final civilian outfits/proportions and NPC composition belong to CHAR-01 / ANIM-02.

254 source clips classified into all seven required families. 45 clips sampled in Play Mode on both bodies (90 retarget evaluations, 6,728 pose samples). **19 ADMIT** across five families, **233 ADAPT** (including unreviewed indexed motions), **2 REJECT** reference poses. Six explicit capability gaps are in the machine catalogue. No duplicate walk from UAL2 is counted toward useful admitted vocabulary.

| B0 need / place | Admitted source IDs | Remaining gap or adaptation |
| --- | --- | --- |
| Walk/explore/follow, L–A–S–E–P and upper return | `ual1:idle_loop`, `ual1:walk_loop`, `ual1:walk_formal_loop` | Consumer movement must match gait; slopes, stairs and navigation are unproved here. UAL2 `walk_fwd_loop` remains an alternative equivalent source. |
| Run/chase support, E–P–Q–O choice | `ual1:jog_fwd_loop`, `ual1:sprint_loop` | Start/stop blends, navigation and elevation transitions remain runtime integration. These are in-place motion assets. |
| Turn to face a witness / route bend | None admitted as an autonomous turn | `Turn90_L/R` and `Turn180_L/R` retarget, but the in-place files only reposition feet; world facing must be synchronized. Retained `ADAPT`. |
| Shop/witness conversation | `ual1:idle_talking_loop`, `ual2:yes`, `ual2:idle_no_loop` | Yes is an outward affirmative hand gesture, not a pure nod. Listening can use neutral idle/folded arms; no dedicated standing-listen clip is asserted. |
| Point toward place/object | Generic `Interact` reach is available, without certified pointing semantics | No dedicated neutral pointing clip. `Counter_Show` requires a counter and is `ADAPT`. |
| Wait, look, resting / mercado and public muelle | `ual1:idle_lookaround_loop`, `ual1:idle_tired_loop`, `ual2:idle_foldarms_loop`, `ual1:groundsit_idle_loop` | Look-around includes hand-to-brow action; tired is a bent fatigue stance. Ground-sit is a flat-ground idle only. |
| Sit/stand on chair; lean at quay rail | No furniture-contact motion admitted | Sitting enter/exit/idle/talk/nod and rail idle/call were sampled and visually checked. Seat/rail height, placement and contact are not proven; all `ADAPT`. |
| Market/shop/port work; carry/handle | No complete contact-bound work action admitted | Counter idle/give, kneeling repair, push and carry gait retarget on both bodies. Counter support, object sockets, tool/contact placement and task timing remain explicit adaptation. Sorting, weighing, wrapping, mooring still lack a demonstrated clip/prop solution. |
| Inspect/use | `ual1:interact` | Admitted only as a contact-free generic reach/inspect gesture. Pickup/table/kneeling, chest opening, drinking and consuming need prop/hand alignment and timing. Door open/close/handle is a true gap. |
| Light surprise/recoil | `ual2:surprise`; `ual1:hit_chest`, `hit_head`, `hit_shoulder_l`, `hit_shoulder_r`, `hit_stomach` | Full-body reactions need consumer blend-out. `Hit_Knockback` is a fall ending down, not a light recoil; remains `ADAPT`. |
| Special/minigame/combat | Indexed only | No combat controller, fishing/minigame authority, cinematic system or mass NPC runtime vocabulary is implemented. |

The factory has useful coverage now and exposes concrete production work where motion alone is insufficient. A source name or successful import is never treated as evidence of hand-object contact or final keeper art.

## Reproduce discovery

```powershell
python Tools/anim_catalog.py search --status ADMIT --family conversation_acting
python Tools/anim_catalog.py search --status ADMIT --query muelle
python Tools/anim_catalog.py search --family work_activity
python Tools/anim_catalog.py search --status GAP
```

Stable IDs resolve to source FBX **and** exact imported clip local ID, source/provenance, tags, root/loop preset, measured compatible bodies, diagnostics and constraints. The native Motion Preview uses the same identities.
