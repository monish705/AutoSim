# Auto-MuJoCo-Compiler

**Drop any 3D object file → get a fully simulated physics scene in minutes.**

No manual XML. No manual mass entry. No manual collision setup.  
Upload a `.glb` or `.obj`, run a Colab notebook, open an interactive sim.

![demo](assets/demo.gif)

---

## What It Does

1. **Loads** your 3D mesh (`.glb` / `.obj`)
2. **Renders** 4 views and sends them to **Gemini 2.5 Flash**
3. **Gemini estimates** — object name, material, mass (kg), friction, restitution — just from looking at it
4. **CoACD** generates accurate convex collision hulls
5. **MuJoCo** compiles a physics scene — object drops, bounces, settles
6. **Download** the output zip → run the interactive local viewer

---

## Quickstart

### Step 1 — Run on Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/monish705/Auto-MuJoCo-Compiler/blob/master/physics_pipeline.ipynb)

1. Click the badge above
2. Go to **Runtime → Change runtime type → T4 GPU**
3. Enter your Gemini API key when prompted (free key at [aistudio.google.com](https://aistudio.google.com))
4. **Runtime → Run all**
5. Upload your `.glb` or `.obj` when the upload box appears
6. Wait ~2 minutes → download `output.zip`

> ⚠️ **When Step 1 says "Your session crashed" — that is expected.**  
> It is a forced kernel restart so packages load correctly.  
> Colab will automatically continue from Step 2.

### Step 2 — Run Locally

```bash
pip install mujoco==3.2.7 trimesh==4.5.3 numpy
```

Extract your `output.zip`, put `viewer.py` in the same folder, then:

```bash
cd path/to/extracted/output
python viewer.py
```

---

## Viewer Controls

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
- Double-click object → `Ctrl + Right drag` — apply torque directly with mouse

---

## Example Output

```json
{
  "object_name": "Rocket Engine",
  "material": "metal",
  "mass_kg": 10.0,
  "friction": 0.5,
  "restitution": 0.3,
  "reasoning": "Metal construction typical of aerospace components"
}
```

---

## Requirements

| Tool | Version |
|---|---|
| Python | 3.10+ |
| mujoco | 3.2.7 |
| trimesh | 4.5.3 |
| numpy | any |
| Gemini API key | free at aistudio.google.com |

Colab handles all other dependencies automatically.

---

## How It Works

```
Upload GLB / OBJ
      ↓
trimesh — load geometry (exact coordinates, zero reconstruction)
      ↓
matplotlib — render 4 views (no OpenGL needed)
      ↓
Gemini 2.5 Flash — infer mass, friction, restitution from appearance
      ↓
CoACD — convex decomposition → collision hulls
      ↓
MuJoCo from_xml_string — compile scene programmatically
      ↓
Simulate → GIF + downloadable scene
```

**Key design principle:** coordinates are never manually typed or reconstructed.  
Everything comes directly from the mesh geometry.

---

## Roadmap

- [x] Single object GLB → MuJoCo simulation
- [x] Gemini VLM automatic physics property estimation  
- [x] Interactive local viewer with full rotation control
- [ ] Multi-object scenes (multiple GLBs in one sim)
- [ ] Gaussian Splat scene input (`.ply` → SuGaR → CoACD → MuJoCo)
- [ ] Full indoor scene from InteriorGS dataset
- [ ] Photo/video → 3DGS → physics simulation

---

## Why

Most robotics and simulation workflows require manually setting up collision geometry, mass, and friction for every object. This pipeline automates that entirely — a developer with no physics simulation experience can go from a downloaded 3D model to a running physics sim in under 5 minutes.

---

## License

MIT
