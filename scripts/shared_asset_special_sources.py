"""Read-only finite NEWSHF contracts; canonical masters are not derived PNGs.

163 and 167 each use one authored three-pose source, not generated bank angles.
The accepted 168 V4 three-pose selection remains a frozen reproducer.
"""
import build_newshf_hd as legacy
import current_newshf_compatibility as newshf
from check_newshf_phase_a import SOFT168_POLICY


def records(root):
    result = []
    for destination, row in newshf.load(root).items():
        frozen = row['record'] == SOFT168_POLICY['record']
        master = f"authoring-inputs/newshf-current/master-{row['record']}.png"
        sources = [row['source_png']] if frozen else [master]
        result.append(dict(
            family='newshf', identity=row['identity'], density=8, role=210,
            status='frozen-reproducer' if frozen else 'current-editable',
            editable_inputs=[] if frozen else sources,
            source_inputs=sources,
            selection=legacy.INPUT+'/manifest.json' if frozen else newshf.SELECTION,
            recipe=['scripts/build_newshf_hd.py', legacy.INPUT+'/manifest.json'] if frozen else
                   ['scripts/build_current_newshf.py', 'authoring-inputs/newshf-current/recipe.json'],
            derived_outputs=[row['source_path']] if frozen else [row['source_png'], row['source_path']],
            declared_consumers=[dict(destination=destination, record=row['record'],
                                     base=row['base'], evidence=legacy.MANIFEST if frozen else newshf.MAPPING)],
            rebuild_commands=['python3 scripts/build_newshf_hd.py check'] if frozen else
                ['python3 scripts/build_current_newshf.py stage --selection <candidate.json> --stage <new-external-stage-dir>',
                 'python3 scripts/build_current_newshf.py apply --stage <new-external-stage-dir>',
                 'python3 scripts/build_current_newshf.py check'],
            notes=['Default-off finite NEWSHF compositor; no global registry eligibility.',
                   'Physical bank/base slots are fixed; authored columns do not prove runtime left/right handedness.',
                   'NEWSHF168 selected PNG hashes are frozen by SOFT168_POLICY; do not repin to accept edits.'
                   if frozen else 'One canonical three-pose master per aircraft, fixed crop/resize recipe; each level uses the same declared resource. Not an automatic animation or a generated tilt from one front pose.']))
    import current_linked_newshf_compatibility as linked
    for destination,row in linked.load(root).items():
        sources=[linked.INPUT_ROOT+'/cold-whole.png']
        if row['base']==83: sources.append(linked.INPUT_ROOT+'/alternate-middle-overlay.png')
        if row['base']==121: sources.append(linked.INPUT_ROOT+'/hot-bottom-overlay.png')
        result.append(dict(family='newshf-linked',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sources,
            selection=linked.SELECTION,
            recipe=['scripts/build_current_linked_newshf.py','scripts/current_linked_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=row['record'],base=row['base'],evidence=linked.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_linked_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>',
                              'python3 scripts/build_current_linked_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['Shared whole cold master with fixed slices at y224/448; unchanged game masks and anchors.',
                   'Top43/45 identical; middle83 latent mechanical extension, not firing; observed firing is43/81/121.',
                   'Overlays replace only immutable original state-difference cells; transparent pixels inherit cold.']))
    return result
