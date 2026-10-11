from PIL import Image
from pathlib import Path
P=Path(__file__).parent;a=Image.open(P/'readability-atlas.png');(P/'frames8x').mkdir(exist_ok=True)
for i,sid in enumerate([112,113]):
 a.crop((112+i*815,117,688+i*815,789)).resize((96,112),Image.Resampling.LANCZOS).save(P/f'frames8x/bank8-id{sid}-96x112.png')
