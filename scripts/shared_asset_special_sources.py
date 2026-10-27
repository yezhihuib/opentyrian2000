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
    import current_turret_newshf_compatibility as turret
    for destination,row in turret.load(root).items():
        sources=[turret.INPUT_ROOT+'/cold-master.png',turret.INPUT_ROOT+'/hot-overlay.png']
        result.append(dict(family='newshf-turret',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sources+[turret.INPUT_ROOT+'/'+n for n in ('native-hot-mask.png','pod-composition-mask8x.png','native-peripheral-source.png')],
            selection=turret.SELECTION,
            recipe=['scripts/build_current_turret_newshf.py','scripts/current_turret_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=record,base=row['base'],evidence=turret.MAPPING) for record in turret.RECORDS],
            rebuild_commands=['python3 scripts/build_current_turret_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>',
                              'python3 scripts/build_current_turret_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['One generated pod master composed over exact original peripheral ground; hot overlay is limited to original22 native changed cells.',
                   'Records162/840 preserve separate original shooting and launch behavior; seven native slots map to two images.',
                   'Full brown backplate remains opaque; no animation clock or gameplay changes.']))
    import current_large_newshi_compatibility as large
    for destination,row in large.load(root).items():
        sources=[large.INPUT_ROOT+'/'+n for n in ('normal-generated-v1.png','open-center-generated-v1.png','registration-recipe.json')]
        result.append(dict(family='newshi-large',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sorted(large.input_paths(root)-{large.SELECTION}),selection=large.SELECTION,
            recipe=['scripts/build_current_large_newshi.py','scripts/current_large_newshi_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path'],large.INPUT_ROOT+'/derived/normal-master-v2.png'],
            declared_consumers=[dict(destination=destination,record=record,base=row['base'],evidence=large.MAPPING) for record in row['records']],
            rebuild_commands=['python3 scripts/build_current_large_newshi.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_large_newshi.py --root . apply --destination <external-stage-dir>'],
            notes=['One 96x84 master with seven independent 24x28 native parts; three separate nose-state masks. No fused actor or clock.',
                   'Deterministic V1 registration then four local V2 alpha mattes; retained RGB unchanged and newly transparent RGB zero-normalized.',
                   'NEWSHI bank13 is independent from NEWSHF bank10; original unchanged-cell masks constrain all damaged nose states.']))
    import current_scout164_newshf_compatibility as scout164
    for destination,row in scout164.load(root).items():
        sources=[scout164.INPUT_ROOT+'/'+n for n in scout164.MASTER_NAMES]
        result.append(dict(family='newshf-scout164',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sorted(scout164.input_paths(root)-{scout164.SELECTION}),selection=scout164.SELECTION,
            recipe=['scripts/build_current_scout164_newshf.py','scripts/current_scout164_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=164,base=row['base'],evidence=scout164.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_scout164_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_scout164_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['Three registered 24x28 poses retain original bank10 bases11/9/13 and anchor6/7.',
                   'Smooth alpha remains inside immutable original support; every transparent pixel is RGBA0.',
                   'Natural straight-pose and controlled bank-pose coverage are distinct; no animation, movement or gameplay changes.']))
    import current_fighter165_newshf_compatibility as fighter165
    for destination,row in fighter165.load(root).items():
        sources=[fighter165.INPUT_ROOT+'/'+n for n in fighter165.MASTER_NAMES]
        result.append(dict(family='newshf-fighter165',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sorted(fighter165.input_paths(root)-{fighter165.SELECTION}),selection=fighter165.SELECTION,
            recipe=['scripts/build_current_fighter165_newshf.py','scripts/current_fighter165_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=165,base=row['base'],evidence=fighter165.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_fighter165_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_fighter165_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['Three registered 24x28 poses retain original bank10 bases49/47/51 and anchor6/7.',
                   'Smooth alpha remains inside immutable original support; every transparent pixel is RGBA0.',
                   'Natural three-pose evidence is kept distinct from controlled diagnostics; no animation, movement or gameplay changes.']))
    import current_interceptor166_newshf_compatibility as interceptor166
    for destination,row in interceptor166.load(root).items():
        sources=[interceptor166.INPUT_ROOT+'/'+n for n in interceptor166.MASTER_NAMES]
        result.append(dict(family='newshf-interceptor166',identity=row['identity'],density=8,role=210,
            status='current-editable',editable_inputs=sources,source_inputs=sorted(interceptor166.input_paths(root)-{interceptor166.SELECTION}),selection=interceptor166.SELECTION,
            recipe=['scripts/build_current_interceptor166_newshf.py','scripts/current_interceptor166_newshf_compatibility.py'],
            derived_outputs=[row['source_png'],row['source_path']],
            declared_consumers=[dict(destination=destination,record=166,base=row['base'],evidence=interceptor166.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_interceptor166_newshf.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_interceptor166_newshf.py --root . apply --destination <external-stage-dir>'],
            notes=['Three registered 24x28 poses retain original bank10 bases87/85/89 and anchor6/7.',
                   'Smooth alpha remains inside immutable original support; every transparent pixel is RGBA0.',
                   'Natural three-pose evidence is kept distinct from controlled diagnostics; no animation, movement or gameplay changes.']))
    import current_shapesy_cyan_compatibility as cyan
    for destination,row in cyan.load(root).items():
        result.append(dict(family='shapesy-cyan',identity=row['identity'],density=8,role=203,
            status='current-editable',editable_inputs=[cyan.INPUT_ROOT+'/raw-generated.png',cyan.INPUT_ROOT+'/registration-recipe.json'],
            source_inputs=sorted(cyan.input_paths(root)-{cyan.SELECTION}),selection=cyan.SELECTION,
            recipe=['scripts/current_shapesy_cyan_compatibility.py','scripts/build_current_shapesy_cyan.py'],
            derived_outputs=[row['source_png'],row['source_path'],cyan.INPUT_ROOT+'/derived/master-384x448.png'],
            declared_consumers=[dict(destination=destination,base=row['base'],layer=2,evidence=cyan.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_shapesy_cyan.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_shapesy_cyan.py --root . apply --destination <external-stage-dir>'],
            notes=['One generated static 48x56 cloud master split into four independently placed 24x28 tiles; no animation.',
                   'Original index0 cells remain transparent RGBA0. Two boundary source cells deliberately move fully inward.',
                   'Only verified ShapesY layer2 palette5 normal internal8; other palettes, blend, and true4 stay classic.']))
    import current_shapesy_cyan_secondary_compatibility as cyan_secondary
    for destination,row in cyan_secondary.load(root).items():
        result.append(dict(family='shapesy-cyan-secondary',identity=row['identity'],density=8,role=203,
            status='current-editable',editable_inputs=[cyan_secondary.INPUT_ROOT+'/raw-generated.png',cyan_secondary.INPUT_ROOT+'/registration-recipe.json'],
            source_inputs=sorted(cyan_secondary.input_paths(root)-{cyan_secondary.SELECTION}),selection=cyan_secondary.SELECTION,
            recipe=['scripts/current_shapesy_cyan_secondary_compatibility.py','scripts/build_current_shapesy_cyan_secondary.py'],
            derived_outputs=[row['source_png'],row['source_path'],cyan_secondary.INPUT_ROOT+'/derived/master-384x672.png'],
            declared_consumers=[dict(destination=destination,base=row['base'],layer=2,evidence=cyan_secondary.MAPPING)],
            rebuild_commands=['python3 scripts/build_current_shapesy_cyan_secondary.py --root . stage --selection <candidate.json> --destination <new-external-stage-dir>','python3 scripts/build_current_shapesy_cyan_secondary.py --root . apply --destination <external-stage-dir>'],
            notes=['One generated static 48x84 cloud master split into five independently placed 24x28 tiles; no animation.',
                   'Original index0 cells remain transparent RGBA0. Thirty-eight boundary source cells deliberately move fully inward.',
                   'Only verified ShapesY layer2 palette5 normal internal8; other palettes, blend, and true4 stay classic.']))
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
