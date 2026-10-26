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
    import current_dualmissile_newshf_compatibility as dualmissile
    for destination,row in dualmissile.load(root).items():
        sources=[dualmissile.INPUT_ROOT+'/single-master.png']
        result.append(dict(family='newshf-dualmissile',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sources+[dualmissile.INPUT_ROOT+'/native-mask.png'],
            selection=dualmissile.SELECTION,
            recipe=['scripts/build_current_dualmissile_newshf.py','scripts/current_dualmissile_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=record,base=169,evidence=dualmissile.MAPPING) for record in dualmissile.RECORDS],
            rebuild_commands=['python3 scripts/build_current_dualmissile_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>',
                              'python3 scripts/build_current_dualmissile_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['One canonical single missile bitmap copied exactly twice; static NEWSHF bank10 quartet169/170/188/189.',
                   'Separate records2/500 retain distinct movement and native type6 white-smoke effects; artwork does not alter gameplay.',
                   'Alpha is smooth only inside immutable original support; palette5 identity remains runtime guarded.']))
    import current_shapesy_platform_compatibility as shapesy
    for destination,row in shapesy.load(root).items():
        sources=sorted(shapesy.input_paths(root)-{shapesy.SELECTION,shapesy.RECIPE_MODULE})
        result.append(dict(family='shapesy-platform',identity=row['identity'],density=8,role=202,
            status='current-editable',editable_inputs=[shapesy.INPUT_ROOT+'/master-platform.png'],
            source_inputs=sources,selection=shapesy.SELECTION,
            recipe=[shapesy.RECIPE_MODULE,'scripts/current_shapesy_platform_compatibility.py','scripts/build_current_shapesy_platform.py'],
            derived_outputs=[row['source_png']]+['assets/hd/packs/'+pack+'/'+shapesy.name(row['base']) for pack in shapesy.PACKS],
            declared_consumers=[dict(destination=destination,base=row['base'],evidence=shapesy.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_shapesy_platform.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>',
                              'python3 scripts/build_current_shapesy_platform.py --root . apply --destination <external-stage-dir>'],
            notes=['One shared generated five-component material master, exact28 deterministic semantic/UV recipes.',
                   'Immutable water cells use native RGB/classic ownership at runtime; transparent PNG is not standalone native passthrough.',
                   'Only verified shapesY Layer1 palette5 normal8x; unknown contexts remain classic.']))
    return result
