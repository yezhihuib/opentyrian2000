#!/usr/bin/env python3
"""Generate a finite original-control state sequence; no engine launch."""
from pathlib import Path
root=Path(__file__).resolve().parent
keys={'RETURN':40,'ESC':41,'DOWN':81,'UP':82,'LEFT':80,'RIGHT':79,'F12':69}
(root/'smoke2.actions').write_text('# menu selected picker picker_selected input arg1 arg2 capture\n1 0 0 0 key 41 0 setup_native2\n')
menu=1;sel=0;picker=0;ps=0;scaler=1;mode=1;parent_sel=0;actions=[]
def act(kind,a=0,b=0,cap='-'):
 global menu,sel,picker,ps,scaler,mode,parent_sel
 actions.append((menu,sel,picker,ps,kind,a,b,cap))
 if kind=='key':
  name=next(k for k,v in keys.items() if v==a)
  if picker:
   n=[0,2,9,4][picker]
   if name in ('UP','DOWN'):ps=(ps+(1 if name=='DOWN' else -1))%n
   elif name=='ESC':picker=0
   elif name=='RETURN':
    if picker==2:scaler=ps
    if picker==3:mode=ps
    picker=0
  else:
   n=3 if menu==3 else 4
   if name in ('UP','DOWN'):sel=(sel+(1 if name=='DOWN' else -1))%n
   elif name=='ESC' or name=='RETURN' and sel==n-1:
    menu,sel=(0,0) if menu==1 else (1,parent_sel)
   elif name=='RETURN':
    if menu==1 and sel<2:parent_sel=sel;menu=sel+2;sel=0
    elif menu==2:picker=sel+1;ps=[0,0,scaler,mode][picker]
 elif kind=='right':menu,sel=1,parent_sel;picker=0
 elif kind in ('left','move') and 45<=a<275 and 37<=b<100:
  for row in range(3 if menu==3 else 4):
   if 37+21*row<=b<50+21*row:sel=row

def key(name,cap='-'):act('key',keys[name],0,cap)
key('DOWN','setup_native2');key('DOWN');key('DOWN');key('DOWN');key('RETURN');key('RETURN','graphics_native2');key('DOWN');key('ESC')
key('DOWN');key('RETURN');key('DOWN','scaler_picker_native2');key('RETURN');key('F12');key('RETURN','graphics_scale2x_classic');key('UP');key('RETURN');key('F12');key('RETURN');key('UP');key('UP');key('UP');key('RETURN');key('F12');key('RETURN','graphics_native4')
# Scaler picker remains live through fullscreen and resize transitions.
act('alt_enter');act('alt_enter');act('resize',1400,900);act('resize',1280,800);key('F12');key('ESC')
key('DOWN');key('RETURN');key('DOWN');key('RETURN');key('F12');key('RETURN','graphics_aspect_classic');key('UP');key('RETURN');key('F12');key('RETURN');key('ESC');key('DOWN');key('RETURN')
key('DOWN');key('RETURN');key('LEFT','sound_native4');key('RIGHT');key('RETURN');key('RETURN','sound_muted_native4');act('left',180,40);act('left',274,40,'sound_zero_native4')
for _ in range(8):key('LEFT')
act('move',140,8);act('move',45,40,'cursor_heading_native4');act('move',80,194);act('move',319,199);key('DOWN');act('left',180,61);act('left',274,61)
for _ in range(8):key('LEFT')
key('RETURN');key('RETURN');act('right',10,10);key('UP');key('RETURN');key('DOWN');key('RETURN');key('DOWN');key('DOWN');key('DOWN');key('RETURN');key('F12');key('ESC');key('ESC')
assert menu==0 and len(actions)<=128 and scaler==1 and mode==1
assert sum(a[-1]!='-' for a in actions)<=10
(root/'matrix2_to4.actions').write_text('# menu selected picker picker_selected input arg1 arg2 capture\n'+'\n'.join(' '.join(map(str,a)) for a in actions)+'\n')
print('Prepared',len(actions),'actions,',sum(a[-1]!='-' for a in actions),'named captures per side.')
