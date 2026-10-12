"""Rebuild the coordinated matte sand artwork in a new external directory."""
from pathlib import Path
import argparse,subprocess,sys
r=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if a.output.is_symlink() or out.exists() or out==r or r in out.parents:p.error('Choose a new directory outside the repository')
subprocess.run([sys.executable,str(r/'assets/hd/artwork/sand-road-grass21-v1/rebuild.py'),str(out)],check=True)
