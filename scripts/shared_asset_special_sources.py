"""Read-only adapter for finite NEWSHF authoring contracts.

These are metadata views, not new source authority or generator entry points.
Frozen inputs are deliberately never reported as current editable inputs.
"""
import build_newshf_hd as newshf
from check_newshf_phase_a import SOFT168_POLICY

def records(root):
    result = []
    for destination, row in newshf.load(root).items():
        frozen = row['record'] == SOFT168_POLICY['record']
        result.append(dict(
            family='newshf', identity=row['identity'], density=8, role=210,
            status='frozen-reproducer' if frozen else 'current-selected-input',
            editable_inputs=[] if frozen else [row['source_png']],
            source_inputs=[row['source_png']],
            recipe=['scripts/build_newshf_hd.py', newshf.INPUT + '/manifest.json'],
            derived_outputs=[row['source_path']],
            declared_consumers=[dict(destination=destination, record=row['record'],
                                     base=row['base'], evidence=newshf.MANIFEST)],
            rebuild_commands=['python3 scripts/build_newshf_hd.py check',
                              'python3 scripts/build_newshf_hd.py build'],
            notes=['One of nine independent normalized pose PNGs, not one master per aircraft.',
                   'Default-off finite NEWSHF compositor; no global registry eligibility.',
                   'No current stage/apply workflow: changes require coherent manifest/provenance and full validation.',
                   'NEWSHF168 selected PNG hashes are frozen by SOFT168_POLICY; do not repin to accept edits.'
                   if frozen else 'Selected normalized input; not an automatic master-to-pose authoring loop.']))

    return result
