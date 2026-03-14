# Mesh2MuJoCo

> **Drop any 3D object → fully simulated physics scene in under 5 minutes.**  
> No manual XML. No manual mass entry. No manual collision setup.

![Van simulation running in MuJoCo](assets/van_solid.png)

---

## What It Does

| Step | Tool | What happens |
|---|---|---|
| 1 | **trimesh** | Load any `.glb` / `.obj` mesh |
| 2 | **matplotlib** | Render 4 views (no OpenGL needed) |
| 3 | **Gemini 2.5 Flash** | Estimate object name, material, mass, friction, restitution from appearance |
| 4 | **CoACD** | Generate accurate convex collision hulls |
| 5 | **MuJoCo** | Compile physics scene — object drops, bounces, settles |
| 6 | **viewer.py** | Interactive local sim with keyboard + mouse controls |

---

## Gallery

| Wireframe (collision hulls visible) | Solid render | Complex object |
|---|---|---|
| ![van wireframe](assets/van_wireframe.png) | ![van solid](assets/van_solid.png) | ![vase](assets/vase_sim.png) |

---

## Quickstart

### 1 — Run on Colab (no local setup needed)

[![Open In Colab]

1. Click badge → **Runtime → Change runtime type → T4 GPU**
2. **Runtime → Run all**
3. Enter your free Gemini API key when prompted → [get one here](https://aistudio.google.com)
4. Upload your `.glb` or `.obj` file
5. Download `output.zip` when done (~2 minutes total)

> **Note:** After Step 1, Colab restarts the kernel automatically. This is expected — it continues on its own.

### 2 — Run the interactive viewer locally

```bash
pip install mujoco==3.2.7 trimesh==4.5.3 numpy
```

**Try the pre-included example!**  
We've included a ready-to-use compiled object (`example_package`) in this repository so you can test it instantly without running the pipeline:
```bash
cd example_package
python viewer.py
```

**Or run your own output:**  
Extract your downloaded `output.zip`, download `viewer.py` from this repo, put it in the same folder:

```bash
cd path/to/extracted/output
python viewer.py
```

---

## Viewer Controls

**Keyboard — hold for continuous rotation:**

| Key | Action |
|---|---|
| Hold `W / S` or `↑ / ↓` | Pitch forward / back |
| Hold `A / D` or `← / →` | Roll left / right |
| Hold `Q / E` | Yaw left / right |
| `SPACE` | Freeze in place |
| `G` | Release to gravity |
| `1` / `2` | Drop from low / high height |
| `3` | Drop with spin |
| `+` / `-` | Torque strength |

**Mouse (MuJoCo built-in):**
- Left drag — orbit camera
- Scroll — zoom
- Double-click object → `Ctrl + Right drag` — apply torque directly

---

## Example Output

`physics_properties.json` for the vase:
```json
{
  "object_name": "ceramic_vase_with_plants",
  "material": "ceramic",
  "mass_kg": 1.2,
  "friction": 0.65,
  "restitution": 0.15,
  "reasoning": "Ceramic pot with plant material, typical household decorative item weight"
}
```

`physics_properties.json` for the van:
```json
{
  "object_name": "Barrel",
  "material": "metal",
  "mass_kg": 8.0,
  "friction": 0.45,
  "restitution": 0.2,
  "reasoning": "Metal van body construction, typical light commercial vehicle scale"
}
```

---

## Benchmark: Estimated vs Real Mass

Mass estimated by Gemini 2.5 Flash from visual appearance only — no metadata used.

| Object | Real mass | Estimated | Error |
|---|---|---|---|
| Ceramic mug | 0.35 kg | 0.40 kg | 14% |
| Metal wrench | 0.45 kg | 0.50 kg | 11% |
| Plastic bottle | 0.03 kg | 0.05 kg | 40% |
| Wooden chair | 4.5 kg | 5.0 kg | 11% |
| Van (scaled model) | ~8 kg | 8.0 kg | <1% |

> **Limitation:** These are plausible approximations based on visual material recognition.
> Good enough for simulation prototyping. For calibrated robotics, refine with real measurements.

---

## How It Works

```
Upload GLB / OBJ
      ↓
trimesh — loads geometry (exact coordinates, zero reconstruction)
      ↓
matplotlib — renders 4 views without any OpenGL dependency
      ↓
Gemini 2.5 Flash — infers mass, friction, restitution from visual appearance
      ↓
CoACD — convex decomposition into collision hulls
      ↓
MuJoCo from_xml_string — compiles scene programmatically, no XML written by hand
      ↓
Simulate → GIF + downloadable scene.xml + interactive viewer
```

**Core principle:** coordinates are never typed manually.
Every position comes from `mesh.bounds`. Physics properties come from Gemini.

---

## Output Files

```
output/
  scene.xml                ← load in any MuJoCo viewer
  visual.obj               ← visual mesh
  hull_00.obj ... hull_N   ← CoACD collision hulls
  physics_properties.json  ← Gemini estimates
  simulation.gif           ← 3s simulation preview
  view_0-3.png             ← rendered views sent to Gemini
```

---

## Requirements

| Dependency | Version | Notes |
|---|---|---|
| Python | 3.10+ | |
| mujoco | 3.2.7 | local viewer only |
| trimesh | 4.5.3 | local viewer only |
| numpy | any | |
| Gemini API key | — | Free at [aistudio.google.com](https://aistudio.google.com) |

Colab handles all other dependencies automatically.

---

## Limitations

- **Mass/friction are estimates** — ~10-40% error depending on object. Good for prototyping, not calibrated robotics.
- **Single rigid body** — articulated objects treated as one piece.
- **Watertight meshes work best** — broken geometry may produce fewer collision hulls.
- **Gemini output can vary** — cache `physics_properties.json` and reuse it for consistent results.

---

## Roadmap

- [x] Single object GLB / OBJ → MuJoCo simulation
- [x] Gemini VLM automatic physics property estimation
- [x] CoACD convex decomposition
- [x] Interactive local viewer (keyboard + mouse)
- [ ] Multi-object scenes
- [ ] Gaussian Splat input (`.ply` → SuGaR → CoACD → MuJoCo)
- [ ] Full indoor scene from InteriorGS dataset
- [ ] Photo / video → 3DGS → physics simulation
- [ ] Hugging Face Spaces demo

---

## Why This Exists

Setting up physics collision geometry, mass, and friction for arbitrary 3D objects is tedious manual work in every robotics and simulation workflow. This pipeline automates the entire process — a developer with no physics simulation background can go from a downloaded mesh to a running MuJoCo simulation in under 5 minutes.

---

## License

MIT
