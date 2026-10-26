"""Path checks shared by the controlled launchers (no downloads or builds)."""
from pathlib import Path


def dependency(parser, value, default, kind):
    path = Path(value if value is not None else default).resolve()
    if (kind == 'exe' and not path.is_file()) or (kind != 'exe' and not path.is_dir()):
        parser.error(f'--{kind}: existing {"file" if kind == "exe" else "directory"} required: {path}')
    if kind == 'data' and not (path / 'tyrian1.lvl').is_file():
        parser.error(f'--data: missing tyrian1.lvl in {path}')
    return path
