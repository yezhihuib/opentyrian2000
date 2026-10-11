import bpy,math,json,os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough;return m
silver=mat('Brushed steel',(.55,.57,.59),.65,.26);dark=mat('Dark steel sides',(.075,.085,.095),.6,.43);red=mat('Red painted shoulders',(.50,.018,.008),.35,.36);highlight=mat('Central silver face',(.55,.58,.59),.65,.32)
def mesh(n,vs,fs,mats,mis=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
 for m in mats:o.data.materials.append(m)
 if mis:
  for p,i in zip(o.data.polygons,mis):p.material_index=i
 return o
# Coordinates expressed in original24x28 canvas. Geometry uses world y upward.
cx,cy=12.0,13.0
pivot=bpy.data.objects.new('Rigid arc pair pivot',None);bpy.context.collection.objects.link(pivot);pivot.location=(cx,28-cy,0)
profile=[(7.4,-.35),(10.2,-.35),(10.2,.12),(9.8,.62),(9.15,.92),(8.35,.82),(7.75,.5),(7.4,.12)]
K=len(profile)
for side in range(2):
 vs=[];N=80
 for j in range(N+1):
  t=math.radians(22.5+135*j/N+side*180)
  for r,z in profile:vs.append((r*math.sin(t),r*math.cos(t),z))
 fs=[];mis=[]
 for j in range(N):
  for k in range(K):fs.append((j*K+k,j*K+(k+1)%K,(j+1)*K+(k+1)%K,(j+1)*K+k));mis.append(0 if k in (2,3,4,5,6) else 1)
 fs+=[tuple(range(K-1,-1,-1)),tuple(N*K+k for k in range(K))];mis +=[1,1]
 o=mesh('Rigid arc'+str(side),vs,fs,[silver,dark],mis);o.parent=pivot
 for face in o.data.polygons:face.use_smooth=True
 bevel=o.modifiers.new('Minute edge rounding','BEVEL');bevel.width=.07;bevel.segments=2
 o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
bpy.ops.object.camera_add(location=(12,14,40));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=28;camera.rotation_euler=(0,0,0);bpy.context.scene.camera=camera
for n,loc,power,size in [('Key',(-12,40,35),28000,18),('Fill',(30,0,28),6000,22)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=n;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((12,15,0))-l.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=False;s.world.color=(.35,.35,.35);s.render.film_transparent=True;s.render.resolution_x=192;s.render.resolution_y=224;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
(P/'arc-renders8x').mkdir(exist_ok=True)
pose=bpy.data.objects.new('Original per-phase whole-object placement',None);bpy.context.collection.objects.link(pose)
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.parent is None:ob.parent=pose
pivot.parent=pose
centers=[(12.5,12.5),(11.5,13.5),(11.5,13.5),(12.5,12.5),(12.5,13.5),(12.5,13.5),(12.5,13.5),(11.5,13.5)]
for i,base in enumerate(range(229,244,2)):
 pose.location=(centers[i][0]-cx,-(centers[i][1]-cy),0)
 pivot.rotation_euler[2]=-math.radians(i*22.5);s.render.filepath=str(P/f'arc-renders8x/newsh2-base-{base}-192x224.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'rotor-family.blend'))
(P/'geometry.json').write_text(json.dumps({'logical_size':[24,28],'anchor':[6,7],'visual_pivot':[cx,cy],'outer_radius':10.2,'inner_radius':7.4,'arc_degrees':135,'gap_degrees':45,'clockwise_angles':[i*22.5 for i in range(8)],'fixed_body':True,'original_phase_centers_pixel_corner_coordinates':centers,'source':'single model, fixed world lighting, no bitmap-painted phases'},indent=2))
