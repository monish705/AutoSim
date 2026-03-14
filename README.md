# Auto-MuJoCo-Compiler

A blazingly fast, fully automated Photo-to-Sim or Object-to-Sim compiler that turns any `.glb` or `.obj` 3D model into a highly accurate, physically-simulated package ready for MuJoCo and Reinforcement Learning (RL) agents.

## Why this exists

Setting up arbitrary 3D objects in a physics simulator like MuJoCo is a notorious bottleneck. Researchers typically have to:
1. Manually compute sizes and coordinates
2. Run convex hull decomposition algorithms (V-HACD or CoACD) manually
3. Guess the mass, friction, and restitution coefficients based on the object
4. Hand-write complicated MuJoCo XML files

The **Auto-MuJoCo-Compiler** automates this entirely into a seamless, zero-friction pipeline. 

### How it works: 
1. The pipeline creates 4 isometric renders of the object using `matplotlib` (zero complex OpenGL/pyrender setup).
2. It queries **Gemini 2.5 Flash** (a state-of-the-art VLM) to estimate the object's mass, typical material, friction, and restitution **purely based on its visual appearance**. 
3. It performs convex collision hull decomposition via `coacd`.
4. It dynamically generates an interactive simulation `.xml` file and zips everything into a ready-to-run package!

---

## 🚀 Quick Start Guide

### 1. The Physics Pipeline (Creating the Object Package)
We have provided a fully self-contained Jupyter Notebook (`Auto_MuJoCo_Compiler.ipynb`) that handles everything.

**Requirements**:
You can run this notebook locally, or simply drop it into Google Colab (Recommended for zero setup). 

1. Open `Auto_MuJoCo_Compiler.ipynb` in [Google Colab](https://colab.research.google.com/) or Jupyter.
2. Run **Step 1** to install the required Python packages (`trimesh`, `coacd`, `mujoco`, `google-genai`). The notebook kernel will automatically restart after this.
3. Run **Step 2** to import dependencies.
4. When prompted, enter your **Gemini API Key**. Get one for free at [Google AI Studio](https://aistudio.google.com/). 
5. Run the remaining cells. You will be prompted to upload your `.glb` or `.obj` file.
6. The pipeline will render the object, guess the physics via VLM, calculate collision geometry, and **download a ready-to-use ZIP file!**

### 2. Verify with the Viewer Script (`viewer.py`)
Once you have the generated ZIP file containing your new `.obj` visuals, collision hulls, and `physics_properties.json`, you can immediately verify how it looks and behaves in an interactive MuJoCo window!

**Requirements for viewer:**
- Ensure you have python installed.
- `pip install mujoco numpy`

**Usage:**
1. Extract the ZIP file downloaded from the pipeline into a new folder.
2. Place the `viewer.py` script from this repository into the same folder as the extracted files (`visual.obj`, `hull_*.obj`, `physics_properties.json`).
3. Run the script:
   ```bash
   python viewer.py
   ```

### 🎮 Viewer Controls

The viewer script uses best practices (`xfrc_applied` torque controls) instead of hacking `qvel`, meaning the object behaves physically properly!

**Keyboard (Hold for continuous rotation):**
- **W / S** : Pitch forward / back
- **A / D** : Roll left / right
- **Q / E** : Yaw left / right
- **SPACE** : Freeze the object in mid-air (zero velocity/force)
- **G** : Release to gravity from the current position
- **1 / 2** : Drop low / high while retaining rotation
- **3** : Drop with an extreme spin
- **+ / -** : Increase/Decrease torque strength

**Mouse (Built-in MuJoCo Controls):**
- **Left drag**: Orbit camera
- **Right drag**: Pan camera
- **Scroll**: Zoom in/out
- **Ctrl + Left drag**: Apply mouse FORCE to object
- **Ctrl + Right drag**: Apply mouse TORQUE to object

---

## Use Cases

* **Robotics Sim-to-Real**: Easily ingest scanned meshes (e.g. from SAM3D) into simulation for robotic grasping and manipulation tasks.
* **RL Practitioners**: Auto-generate thousands of diverse objects with semantically accurate weights and frictions without lifting a finger.

## License
MIT
