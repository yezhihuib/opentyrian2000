# Native GEGL tile-seamless operation; no synthesized raster art.
import gi
from pathlib import Path
gi.require_version('Gegl','0.4')
from gi.repository import Gegl
Gegl.init(None)
R=Path(__file__).resolve().parent
root=Gegl.Node.new()
load=root.create_child('gegl:load');load.set_property('path',str(R/'core54.png'))
seamless=root.create_child('gegl:tile-seamless')
save=root.create_child('gegl:png-save');save.set_property('path',str(R/'core-periodic.png'))
load.link(seamless);seamless.link(save);save.process()
print('Native GEGL periodic cloud substrate exported')
