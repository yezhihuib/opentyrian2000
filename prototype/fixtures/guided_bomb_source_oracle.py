"""Independent source equations plus optional read-only audited table closure.
No original records are bundled or copied to the report. No game process starts.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess,tempfile

def sha(b):return hashlib.sha256(b).hexdigest()
def _equation_harness(source):
    begin=source.index('if (weapon->attack[shotMultiPos[bay_i]-1] > 99')
    end=source.index('\n\t\tif (del == 99 || del == 98)',begin)
    setup=source[begin:end]
    begin=source.index('JE_word sprite_frame = shot->shotGr + shot->shotAni')
    end=source.index('\n\t\t*out_shot_damage',begin)
    frame=source[begin:end]
    normal='draw_entity_sprite2(VGAScreen, *out_shotx+1, *out_shoty, spriteSheet8, sprite_frame, ENTITY_NORMAL, ENTITY_TILE);'
    shadow='draw_entity_sprite2(VGAScreen, *out_shotx+1, *out_shoty + shadowYDist, spriteSheet8, sprite_frame, ENTITY_SHADOW, ENTITY_TILE);'
    guard='background2 && *out_shoty + shadowYDist < 190 && tmp_shotXM < 100'
    assert source.count(normal)==source.count(shadow)==1 and source.count(guard)==2
    assert source.count('shot->shotAni = 0;')>=2
    assert 'shotAvail[shot_id]--;' in source
    return r'''
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
typedef int JE_integer;typedef unsigned char JE_byte;typedef unsigned short JE_word;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"SOURCE FAIL line %d: %s\n",__LINE__,#x);exit(3);}checks++;}while(0)
static unsigned long checks;static int shotAvail[1],shotMultiPos[1];
typedef struct {int attack[8],by[8],bx[8],sx[8],del[8],sg[8],shipblastfilter,acceleration,accelerationx,weapani;} Weapon;
typedef struct {int chainReaction,shotDmg,shotBlastFilter,shotX,shotY,shotYC,shotXC,shotXM,shotTrail,shotGr,shotAni,shotAniMax;} Shot;
static int draw_x,draw_y,draw_style,draw_frame,draw_count;
enum {ENTITY_NORMAL,ENTITY_SHADOW,ENTITY_TILE};static int VGAScreen,spriteSheet8;
static void draw_entity_sprite2(int screen,int x,int y,int bank,int frame,int style,int layout){(void)screen;(void)bank;(void)layout;draw_x=x;draw_y=y;draw_style=style;draw_frame=frame;draw_count++;}
static void run_setup(int lifetime,int damage,int animation,int id,int pos){
 Weapon w={0},*weapon=&w;Shot s={0},*shot=&s;int bay_i=0,shot_id=0,PX=90,PY=70;
 for(int i=0;i<8;i++){w.attack[i]=damage;w.del[i]=lifetime;w.sg[i]=id;w.bx[i]=i-4;w.by[i]=7-i;w.sx[i]=i*2;}
 w.shipblastfilter=208;w.acceleration=3;w.accelerationx=-2;w.weapani=animation;shotMultiPos[0]=pos;shot->shotTrail=98;
''' + setup + r'''
 CHECK(shot->chainReaction==((damage>=100&&damage<=249)?damage-100:0));CHECK(shot->shotDmg==((damage>=100&&damage<=249)?1:damage));CHECK(shot->shotBlastFilter==208);
 CHECK(shot->shotX==90+pos-5&&shot->shotY==78-pos);CHECK(shot->shotXC==-2&&shot->shotYC==-3&&shot->shotXM==(pos-1)*2);
 int life=lifetime==121?255:lifetime;CHECK(shotAvail[0]==(id?life:0));CHECK(shot->shotTrail==(lifetime==121?0:98));CHECK(shot->shotAniMax==((life>100&&life<120)?life-99:animation+1));
 if(id){int ani=0;for(int tick=0;tick<life;tick++){CHECK(shotAvail[0]>0);shotAvail[0]--;
''' + frame + r'''
 CHECK(sprite_frame==id+ani&&raw_frame==sprite_frame);ani++;if(ani==shot->shotAniMax)ani=0;CHECK(shot->shotAni==ani);if(tick==life-1)CHECK(shotAvail[0]==0);
 }}
}
static void run_origin(int x,int y,int distance,int velocity,bool back){
 int*out_shotx=&x,*out_shoty=&y,shadowYDist=distance,tmp_shotXM=velocity;bool background2=back;int sprite_frame=20;draw_count=0;
 if(''' + guard + r'''){''' + shadow + r'''CHECK(draw_x==x+1&&draw_y==y+distance&&draw_style==ENTITY_SHADOW&&draw_frame==20);}
 CHECK(draw_count==(int)(back&&y+distance<190&&velocity<100));
 ''' + normal + r'''
 CHECK(draw_x==x+1&&draw_y==y&&draw_style==ENTITY_NORMAL&&draw_frame==20);
}
int main(void){
 const int dels[]={0,1,4,8,98,99,100,101,119,120,121,122,255},attacks[]={0,99,100,101,112,114,128,249,250,255},ids[]={0,19,171,20,21,22};
 for(unsigned d=0;d<sizeof(dels)/sizeof(*dels);d++)for(unsigned a=0;a<sizeof(attacks)/sizeof(*attacks);a++)for(unsigned i=0;i<sizeof(ids)/sizeof(*ids);i++)for(int p=1;p<=8;p++)for(int ani=0;ani<3;ani++)run_setup(dels[d],attacks[a],ani,ids[i],p);
 for(int x=-3;x<4;x++)for(int y=170;y<=195;y++)for(int d=0;d<=20;d+=10)for(int v=99;v<=101;v++)for(int b=0;b<2;b++)run_origin(x,y,d,v,b!=0);
 printf("PASS: %lu source-equation assertions; active positions1..8; attack chain thresholds; TTL and animation edges; last admitted tick; spawn/draw/shadow origins and guards.\n",checks);return 0;
}
'''

def _run(source,work,label):
    code=_equation_harness(source);p=work/(label+'.c');p.write_text(code);exe=work/label
    result=subprocess.run([os.environ.get('CC','cc'),'-std=c99','-O1','-Wall','-Wextra','-Werror',str(p),'-o',str(exe)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    return subprocess.run([str(exe)],capture_output=True,text=True,timeout=90)

def source_equations(root,contract,closure_path=None,mutations=False):
    shots=(root/'src/shots.c').read_text();tyrian=(root/'src/tyrian2.c').read_text()
    assert sha((root/'src/shots.c').read_bytes())==contract['baseline_files']['src/shots.c']
    assert sha((root/'src/tyrian2.c').read_bytes())==contract['baseline_files']['src/tyrian2.c']
    sequence=['if (shotAvail[z] != 0)','player_shot_move_and_draw(z,','if (collided)','if (chain > 0)','shotMultiPos[SHOT_MISC] = 0;','b = player_shot_create(0, SHOT_MISC, tempShotX, tempShotY, mouseX, mouseY, chain, playerNum);','shotAvail[z] = 0;','goto draw_player_shot_loop_end;']
    start=tyrian.index('/* Player Shot Images */')
    for literal in sequence:start=tyrian.index(literal,start)+len(literal)
    work=Path(tempfile.mkdtemp(prefix='guided-source-equations-'));result=_run(shots,work,'equations');assert result.returncode==0,result.stderr
    killed=[]
    if mutations:
        for label,old,new in [('chain-off-by-one','weapon->attack[shotMultiPos[bay_i]-1] - 100','weapon->attack[shotMultiPos[bay_i]-1] - 99'),('animation-off-by-one','weapon->weapani + 1','weapon->weapani + 2'),('TTL121-wrong','del = 255;','del = 254;'),('spawn-recentered','shot->shotX = PX + weapon->bx','shot->shotX = PX + 1 + weapon->bx'),('advance-before-draw','JE_word sprite_frame = shot->shotGr + shot->shotAni;','JE_word sprite_frame = shot->shotGr + shot->shotAni + 1;')]:
            assert shots.count(old)==1,(label,shots.count(old));r=_run(shots.replace(old,new),work,label);assert r.returncode and 'SOURCE FAIL' in r.stderr,(label,r.stdout,r.stderr);killed.append({'name':label,'diagnostic':r.stderr.strip()})
    report={'status':'passed','oracle':result.stdout.strip(),'negative_controls':killed,'retained_test_work':str(work),'collision_reset_child_origin_parent_removal_source_sequence':True,'external_table_closure':'not supplied'}
    if closure_path:
        data=Path(closure_path).read_bytes();assert sha(data)==contract['source_closure_sha256'],'Source audit changed'
        audit=json.loads(data);assert audit['bounded_bank8_family']==[19,171,20,21] or set(audit['bounded_bank8_family'])=={19,171,20,21};assert audit['frame22_in_guided_closure'] is False
        groups=[]
        expected_chains={28:[[12],[12],[28],[12],[28],[12,28],[12,28],[12,28],[12,28],[12,28],[12,28]],29:[[28],[28],[28],[16],[16],[16],[13],[28],[16,28],[14],[14]],31:[[28],[28],[28],[28],[28],[12,28],[28],[12,28],[12,28],[12,28],[12,28]]}
        for name,g in audit['groups'].items():
            records=g['exact_records'];assert len(g['guided_configurations'])==33 and g['guided_children']==[12,13,14,16,28]
            for c in g['guided_configurations']:
                assert c['children']==expected_chains[c['port']][c['power']-1];assert '8:22' not in c['heads']
            for n in g['guided_parent_records']+g['guided_children']+list(range(738,749)):
                raw=records[str(n)]['raw_record'];derived=records[str(n)]['derived'];assert raw['weapani']==0
                patterns=derived['patterns'];assert len(patterns)==raw['max']
                for i,p in enumerate(patterns):
                    ttl=255 if raw['del'][i]==121 else raw['del'][i];animation=ttl-99 if 100<ttl<120 else raw['weapani']+1
                    assert p['ttl']==ttl and p['animation_length']==animation==1
                    expected=[f'8:{raw["sg"][i]}'];assert p['draw_frames']==expected
                    assert p['spawn_offset']==[raw['bx'][i],raw['by'][i]]
                    assert p['chain']==(raw['attack'][i]-100 if 99<raw['attack'][i]<250 else 0)
                if n in g['guided_parent_records']:assert raw['trail']==98 and raw['shipblastfilter']==(208 if name=='e1-3' else 80)
                elif n in g['guided_children']:assert raw['multi']==raw['max'] and raw['trail']==1 and raw['shipblastfilter']==112 and not derived['chains'] and set(derived['heads'])<=({'8:20'} if name=='e1-3' else {'8:20','8:21'})
                else:assert not derived['chains'] and set(derived['heads'])<=({'8:20','8:21'} if n<745 else {'8:20','8:21','8:22'})
            assert records['28']['raw_record']['attack'][4:8]==[0,0,0,0]
            assert all(records['28']['raw_record']['del'][i]>0 and records['28']['raw_record']['sg'][i]>0 for i in range(4,8))
            assert g['queried_frames_from_nontrivial_animation']==[]
            groups.append({'group':name,'guided_configurations':33,'parent_records':33,'child_records':5,'widget_static_records':11,'frame22_guided':False,'widget22_powers':[8,9,10,11],'static_shared20_21':True})
        report['external_table_closure']={'status':'passed','sha256':sha(data),'groups':groups,'raw_records_copied':False}
    return report
