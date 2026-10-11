# Enemy-only orange/red energy orb112/113

Two generated96×112 RGBA images retain the original12×14 canvas and anchor0,0. The first visible phase is113, then112;113 is brighter. Both share a calibrated source grid and center. Normal alpha provides a warm core and diffuse edge, with no solid casing, hard glass rim or directional variants.

Only the surviving enemy-shot path binds these files. Player112/113/114, player shadows and animation semantics remain unchanged. Original enemy shots have no shadow/filter/blend sprite pass and draw at sx,sy without the player+1 offset. Their collision/explosion logic and timing are untouched.

Saved readability-atlas.png, readability-prompt.txt and extract_final.py are the complete authored inputs. No original game pixels are included. Run `python prototype/build-enemy-orb-art.py --output NEW_EXTERNAL_DIRECTORY` to reproduce both selected PNGs exactly with Pillow. See docs/ENEMY_ORB_VALIDATION.md for actual native motion and finite safety checks.
