"""Read-only presence preflight for source preview's fixed authoring tools.

This does not run/import a producer, verify tool versions, or validate a pack.
A successful check never replaces the original builder's complete validation.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import sys

DECLARATIONS = (
    ('scripts/current_missile_compatibility.py', 'MAGICK', True),
    ('scripts/current_rear_p7_compatibility.py', 'NODE', True),
    ('scripts/current_rear_p7_compatibility.py', 'SHARP', False),
)


def declared_path(source, name):
    tree = ast.parse(source)
    stores = [node for node in ast.walk(tree)
              if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
              and node.id == name]
    declarations = [node for node in tree.body if isinstance(node, ast.Assign)
                    and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == name]
    # Finite direct binding checks, not an interpreter for arbitrary globals().
    def rebound(nodes):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == name:
                    return True
                continue  # Their bodies have a separate binding scope.
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if any((alias.asname or alias.name.split('.')[0]) == name
                       for alias in node.names):
                    return True
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Del) and node.id == name:
                return True
            if rebound(ast.iter_child_nodes(node)):
                return True
        return False
    if len(stores) != 1 or len(declarations) != 1 or rebound(tree.body):
        raise ValueError('Expected one fixed authoring declaration: ' + name)
    value = declarations[0].value
    if not isinstance(value, ast.Constant) or not isinstance(value.value, str) or not value.value or '\x00' in value.value:
        raise ValueError('Expected literal authoring path: ' + name)
    return value.value


def check(root):
    sources = {}
    dependencies = []
    for relative, name, executable in DECLARATIONS:
        if relative not in sources:
            sources[relative] = (root / relative).read_text(encoding='utf-8')
        raw = declared_path(sources[relative], name)
        path = Path(raw)
        present = path.is_file()
        usable = present and os.access(path, os.R_OK) and (not executable or os.access(path, os.X_OK))
        dependencies.append(dict(name=name, path=raw, executable_required=executable,
                                 available=usable))
    missing = [row for row in dependencies if not row['available']]
    if missing:
        detail = '; '.join(row['name'] + '=' + row['path'] for row in missing)
        raise ValueError('Source preview authoring prerequisites unavailable: ' + detail +
                         '. These fixed authoring paths are not a portable Windows toolchain. '
                         'Use an already prepared compatible pack with start-manual-hd.ps1 '
                         '-AssetsDirectory or start-asset-debug.ps1 -Assets, or the distributed '
                         'packaging/start-hd.ps1 runtime pack. No pack was built. '
                         'Do not substitute tool versions; original authoring validation remains required.')
    return dict(status='PRESENCE_ONLY_PASS', dependencies=dependencies,
                versions_verified=False, pack_validated=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = check(args.root)
    except (OSError, ValueError, SyntaxError) as exc:
        print('Preview dependency preflight: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
