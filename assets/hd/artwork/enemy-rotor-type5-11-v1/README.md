# Physical rotor enemy types5/11

Eight generated192×224 RGBA frames represent original24×28 composites, newsh2 bases229,231,233,235,237,239,241,243, anchor6,7. Type11 uses the reverse original sequence. The engine still draws four original12×14 quadrants with the same filter, positions and ordering. No directional/tween or damage frame is invented.

One shared Blender arc mesh, fixed lighting and calculated22.5° phases keep the solid metal body coherent. A single generated fixed center carries red accents. Original measured per-phase placement is metadata only; no original pixels or game files are included. The original phase237's widened arc gap is deliberately not copied, preserving rigid geometry. This physical enemy retains a solid silhouette; the soft-energy-edge convention does not apply to its metal body.

Run `python prototype/build-rotor-art.py --output NEW_EXTERNAL_DIRECTORY` with Blender4.3.2 and Pillow. The script generates the arc renders and assembles the eight final frames, then verifies every committed PNG and decoded RGBA byte. The .blend project and split-tile duplicates are unnecessary generated outputs, not formal inputs. Original game data is not required for this source rebuild.

See docs/ROTOR_ENEMY_VALIDATION.md for finite runtime coverage and limitations.
