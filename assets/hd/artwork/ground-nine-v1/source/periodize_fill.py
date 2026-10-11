# Invoke native GEGL tile-seamless, no generated or painted pixels in Python.
import gi,sys
gi.require_version('Gegl','0.4')
from gi.repository import Gegl
Gegl.init(None)
root=Gegl.Node.new();load=root.create_child('gegl:load');load.set_property('path',sys.argv[1]);seamless=root.create_child('gegl:tile-seamless');save=root.create_child('gegl:png-save');save.set_property('path',sys.argv[2]);load.link(seamless);seamless.link(save);save.process()
