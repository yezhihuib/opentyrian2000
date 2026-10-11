from pathlib import Path
import sys,struct,hashlib
p=Path(sys.argv[1])/'terrain-shapesz-101-8.hda';raw=p.read_bytes();expected='709c0ed19741ce90205a7fd1ad7f36bf65d37180e51c30a13a87f22fa993fc99';assert hashlib.sha256(raw).hexdigest()==expected,'Frozen101 mismatch: do not alter accepted dependency';assert raw[:4]==b'HDR1' and struct.unpack_from('<6I',raw,4)==(2010101,8,24,28,0,0) and len(raw)==172060;Path(sys.argv[2]).write_bytes(raw[28:])
