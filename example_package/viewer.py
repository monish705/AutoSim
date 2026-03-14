"""
Interactive MuJoCo Viewer — Proper Physics Controls
====================================================
Uses xfrc_applied (MuJoCo's documented external force API) for rotation.
This applies torque THROUGH the physics engine, not by hacking qvel directly.

Put in same folder as visual.obj, hull_*.obj, physics_properties.json
Run: python viewer.py

Keyboard (HOLD for continuous rotation):
    W / S           pitch forward / back
    A / D           roll left / right
    Q / E           yaw left / right
    SPACE           freeze (zero velocity + zero applied forces)
    G               release to gravity from current position
    1 / 2           drop from low / high height (keeps orientation)
    3               drop with spin
    + / -           torque strength

Mouse (MuJoCo built-in — always available):
    Left drag               orbit camera
    Right drag              pan camera
    Scroll                  zoom
    Ctrl + Left drag        apply FORCE to selected body
    Ctrl + Right drag       apply TORQUE to selected body
    Double-click body       select it for perturbation
"""

import json, time, threading
import numpy as np
import mujoco
import mujoco.viewer
from pathlib import Path

HERE = Path(__file__).parent

# ── Physics properties ────────────────────────────────────────────────────────
with open(HERE / 'physics_properties.json') as f:
    props = json.load(f)

mass = float(props['mass_kg'])
fric = float(props['friction'])
print(f"Object  : {props['object_name']}")
print(f"Material: {props['material']}")
print(f"Mass    : {mass} kg  |  Friction: {fric}")

# ── Build assets ──────────────────────────────────────────────────────────────
assets = {}
assets['visual.obj'] = (HERE / 'visual.obj').read_bytes()
hull_files = sorted(HERE.glob('hull_*.obj'))
hull_names = []
for hp in hull_files:
    assets[hp.name] = hp.read_bytes()
    hull_names.append(hp.stem)
print(f"Hulls   : {len(hull_names)}")

mesh_assets = '<mesh name="vis_mesh" file="visual.obj"/>\n    '
mesh_assets += '\n    '.join(
    f'<mesh name="{nm}" file="{nm}.obj"/>' for nm in hull_names
)
mass_per_hull = mass / max(len(hull_names), 1)

col_geoms = '\n      '.join(
    f'<geom name="col_{i:02d}" type="mesh" mesh="{nm}" '
    f'mass="{mass_per_hull:.6f}" '
    f'friction="{fric} 0.005 0.0001" '
    f'margin="0.001" '
    f'rgba="0 0 0 0"/>'
    for i, nm in enumerate(hull_names)
)

xml = f"""<mujoco model="{props['object_name'].replace(' ','_')}">
  <compiler angle="radian"/>
  <option gravity="0 0 -9.81" timestep="0.002" integrator="implicitfast"
          cone="elliptic" noslip_iterations="5"/>
  <visual>
    <headlight diffuse="0.8 0.8 0.8" ambient="0.3 0.3 0.3" specular="0.1 0.1 0.1"/>
    <rgba haze="0.15 0.25 0.35 1"/>
  </visual>
  <asset>
    {mesh_assets}
    <texture name="grid" type="2d" builtin="checker"
             width="512" height="512"
             rgb1="0.85 0.85 0.85" rgb2="0.65 0.65 0.65"/>
    <material name="floor_mat" texture="grid" texrepeat="4 4" reflectance="0.1"/>
  </asset>
  <worldbody>
    <light name="top"   pos="0 0 5"  dir="0 0 -1"  castshadow="true"/>
    <light name="front" pos="3 -3 3" dir="-1 1 -1" castshadow="false"
           diffuse="0.4 0.4 0.4"/>
    <geom name="floor" type="plane" size="8 8 0.1"
          material="floor_mat"
          friction="{fric} 0.005 0.0001"/>
    <body name="object" pos="0 0 0.8">
      <freejoint name="free"/>
      <geom name="visual" type="mesh" mesh="vis_mesh"
            contype="0" conaffinity="0" rgba="0.78 0.70 0.55 1"/>
      {col_geoms}
    </body>
  </worldbody>
</mujoco>"""

model = mujoco.MjModel.from_xml_string(xml, assets)
data  = mujoco.MjData(model)

# Get body id for xfrc_applied
body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'object')

qp = model.jnt_qposadr[0]   # freejoint qpos: [x,y,z, w,qx,qy,qz]
qv = model.jnt_dofadr[0]    # freejoint qvel: [vx,vy,vz, wx,wy,wz]

# ── Hold state — proper threading.Event per key ───────────────────────────────
# key_callback fires on press only. We use a dict of Events.
# Press = set event. We clear it after KEY_HOLD_TIMEOUT with a timer thread.
# This correctly handles held keys: OS key-repeat keeps resetting the timer.
KEY_HOLD_TIMEOUT = 0.10   # seconds — OS key repeat ~30ms, so 100ms is safe
held = {}
hold_timers = {}

def press_key(keycode):
    """Called on each key press (including OS repeats while held)."""
    if keycode not in held:
        held[keycode] = threading.Event()
    held[keycode].set()
    # Reset the auto-clear timer
    if keycode in hold_timers and hold_timers[keycode] is not None:
        hold_timers[keycode].cancel()
    t = threading.Timer(KEY_HOLD_TIMEOUT, lambda k=keycode: held[k].clear())
    hold_timers[keycode] = t
    t.daemon = True
    t.start()

def is_held(keycode):
    return keycode in held and held[keycode].is_set()

# ── Torque control ────────────────────────────────────────────────────────────
# xfrc_applied[body_id] = [fx, fy, fz, tx, ty, tz] in world frame
# This is the documented MuJoCo way to apply external forces/torques.
# It gets zeroed each step unless we keep setting it.
TORQUE = 1.5   # Nm — scaled for typical object mass

def apply_xfrc_torques():
    """
    Set xfrc_applied torques for currently held keys.
    Uses world-frame axes so rotation feels consistent regardless of object pose.
    xfrc_applied is zeroed by MuJoCo after each step — must be set every step.
    """
    tx = ty = tz = 0.0
    t = TORQUE * mass   # scale torque by mass so lighter objects aren't over-spun

    if is_held(87)  or is_held(265): ty += t   # W / UP    pitch fwd
    if is_held(83)  or is_held(264): ty -= t   # S / DOWN  pitch back
    if is_held(65)  or is_held(263): tx -= t   # A / LEFT  roll left
    if is_held(68)  or is_held(262): tx += t   # D / RIGHT roll right
    if is_held(81):                  tz += t   # Q         yaw left
    if is_held(69):                  tz -= t   # E         yaw right

    # xfrc_applied[body_id] = [fx, fy, fz, tx, ty, tz]
    data.xfrc_applied[body_id, 3] = tx
    data.xfrc_applied[body_id, 4] = ty
    data.xfrc_applied[body_id, 5] = tz

def clear_xfrc():
    data.xfrc_applied[body_id, :] = 0.0

def freeze():
    """Zero velocity and applied forces — object stays exactly where/how it is."""
    data.qvel[:] = 0.0
    clear_xfrc()
    mujoco.mj_forward(model, data)

def drop_from_height(height, extra_spin=None):
    """Lift to height preserving CURRENT orientation, then release."""
    cur_quat = data.qpos[qp+3:qp+7].copy()
    mujoco.mj_resetData(model, data)
    data.qpos[qp+0] = 0.0
    data.qpos[qp+1] = 0.0
    data.qpos[qp+2] = height
    data.qpos[qp+3:qp+7] = cur_quat   # restore — never forced upright
    data.qvel[:] = 0.0
    if extra_spin is not None:
        data.qvel[qv+3] = extra_spin[0]
        data.qvel[qv+4] = extra_spin[1]
        data.qvel[qv+5] = extra_spin[2]
    mujoco.mj_forward(model, data)

MOVEMENT_KEYS = {87, 83, 65, 68, 81, 69, 265, 264, 263, 262}

def key_callback(keycode):
    global TORQUE

    if keycode in MOVEMENT_KEYS:
        press_key(keycode)   # register hold
        return

    # One-shot actions
    if   keycode == 32:  freeze()                                 # SPACE
    elif keycode == 71:  data.qvel[:] = 0.0                       # G release
    elif keycode == 49:  drop_from_height(0.4)                    # 1 low
    elif keycode == 50:  drop_from_height(2.5)                    # 2 high
    elif keycode == 51:  drop_from_height(1.5, [0, 0, 12.0])      # 3 spin
    elif keycode == 61:                                            # + stronger
        TORQUE = min(TORQUE + 0.5, 10.0)
        print(f'Torque scale: {TORQUE:.1f}')
    elif keycode == 45:                                            # - weaker
        TORQUE = max(TORQUE - 0.5, 0.2)
        print(f'Torque scale: {TORQUE:.1f}')

print("\n── Keyboard Controls ─────────────────────────────────────────")
print("  HOLD W/S  or  ↑/↓    pitch forward / back")
print("  HOLD A/D  or  ←/→    roll left / right")
print("  HOLD Q / E           yaw left / right")
print("  SPACE                freeze in place")
print("  G                    release to gravity")
print("  1 / 2 / 3            drop low / high / with spin")
print("  + / -                torque strength")
print("\n── Mouse Controls (MuJoCo built-in) ──────────────────────────")
print("  Left drag            orbit camera")
print("  Right drag           pan camera")
print("  Scroll               zoom")
print("  Double-click object  select for mouse perturbation")
print("  Ctrl + Left drag     apply FORCE to selected object")
print("  Ctrl + Right drag    apply TORQUE to selected object")
print("──────────────────────────────────────────────────────────────")
print("Object starts in its captured orientation — nothing forced.")
print(f"Torque scale: {TORQUE}  |  Launching...")

with mujoco.viewer.launch_passive(model, data, key_callback=key_callback) as v:
    v.cam.lookat    = [0, 0, 0.3]
    v.cam.distance  = 2.5
    v.cam.elevation = -20
    v.cam.azimuth   = 135

    while v.is_running():
        apply_xfrc_torques()   # set xfrc each step (MuJoCo zeros it after step)
        mujoco.mj_step(model, data)
        v.sync()
