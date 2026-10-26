#!/usr/bin/env python3
"""Finite straight-contour oracle: original full map, polygon-clipped footprint.

Uses the actual engine include and original indexed blitter; no production
coverage helper or world-run cache is used to compute expected output.
"""
from pathlib import Path
import importlib.util,json,sys,hashlib,os
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('shapesy_runtime',ROOT/'tests/test_shapesy_platform_runtime.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
FOCUSED=r'''
static signed char world_plane[8400][336],world_member[8400][336],world_boundary[8400][336];
static Uint8 world_index[8400][336];
typedef struct {int x0,y0,x1,y1,type;short samples[256];bool overflow;} OracleRun;
static OracleRun oracle_lines[512];static unsigned oracle_count;
static Uint32 before_rgba[2560*1600],want_rgba[2560*1600];
static Uint8 before_owner[2560*1600],want_owner[2560*1600],before_cloud[2560*1600],band[2560*1600];
static Uint8 before_index[64000],before_expected[64000];
static unsigned world_upper_planes[9],max_run_span;
static unsigned total_changed,water_changed,fractional[2][2],upper_other[9],overlap_pixels,seen[28],zero_samples;
static int xoffset,current_row,current_phase;static const char *fixture_path;
static int plane_at(int x,int y)
{return x<0||x>=336||y<0||y>=8400?-1:world_plane[y][x];}
static bool deck_at(int x,int y)
{int p=plane_at(x,y);return p==1||p==6||p==8;}
static void keep_run(OracleRun r)
{
 int height=r.y1-r.y0,width=r.x1-r.x0;
 if(r.overflow||height<9||abs(width)*10<height*6||abs(width)*10>height*11)return;
 if((r.type==1&&width<=0)||(r.type==2&&width>=0))return;
 for(int j=0;j<=height;j++)if(abs((r.samples[j]-r.x0)*height-width*j)>3*height)return;
 assert(oracle_count<512);oracle_lines[oracle_count++]=r;
}
static void oracle_world(void)
{
 for(int y=0;y<8400;y++)for(int x=0;x<336;x++){
  unsigned slot=map_indices[(y/28)*14+x/24];int k=-1;
  for(unsigned m=0;m<28;m++)if(shapesy_ids[m]==lookup[slot])k=(int)m;
  world_member[y][x]=(signed char)k;world_index[y][x]=original_sources[slot][y%28*24+x%24];
  world_plane[y][x]=k<0?-1:shapesy_contour_semantic[k*672+y%28*24+x%24];if(k>=0)seen[k]=1;
 }
 for(int y=0;y<8400;y++)for(int x=1;x<336;x++)if(deck_at(x-1,y)&&!deck_at(x,y)){
  for(int j=0;j<3;j++){int p=plane_at(x+j,y);if(p==4||p==5){world_boundary[y][x]=2;break;}if(p==0){world_boundary[y][x]=1;break;}if(p!=7)break;}
 }
 OracleRun active_runs[64];bool used[64]={0};
 for(int y=0;y<8400;y++){
  for(int x=1;x<336;x++)if(world_boundary[y][x]){
   int type=world_boundary[y][x],slot=-1,distance=5;
   for(int j=0;j<64;j++)if(used[j]&&active_runs[j].type==type&&active_runs[j].y1==y-1&&abs(active_runs[j].x1-x)<distance){distance=abs(active_runs[j].x1-x);slot=j;}
   if(slot<0){for(int j=0;j<64;j++)if(!used[j]){slot=j;break;}assert(slot>=0);used[slot]=true;memset(&active_runs[slot],0,sizeof(OracleRun));active_runs[slot].x0=x;active_runs[slot].y0=y;active_runs[slot].type=type;}
   OracleRun *r=&active_runs[slot];r->x1=x;r->y1=y;if(y-r->y0<256)r->samples[y-r->y0]=x;else r->overflow=true;
  }
  for(int j=0;j<64;j++)if(used[j]&&active_runs[j].y1<y){keep_run(active_runs[j]);used[j]=false;}
 }
 for(int j=0;j<64;j++)if(used[j])keep_run(active_runs[j]);
 assert(oracle_count);for(unsigned k=0;k<28;k++)assert(seen[k]);
 char path[1200];snprintf(path,sizeof(path),"%s.world-lines.tsv",fixture_path);FILE *f=fopen(path,"w");assert(f);fprintf(f,"type\tx0\ty0\tx1\ty1\n");
 for(unsigned i=0;i<oracle_count;i++){
  OracleRun r=oracle_lines[i];fprintf(f,"%d\t%d\t%d\t%d\t%d\n",r.type,r.x0,r.y0,r.x1,r.y1);if((unsigned)(r.y1-r.y0)>max_run_span)max_run_span=r.y1-r.y0;
  if(r.type==1)for(int y=r.y0;y<=r.y1;y++)for(int x=r.samples[y-r.y0]-4;x<=r.samples[y-r.y0]+4;x++){
   int p=plane_at(x,y);if(p>=0&&p<9&&p!=6&&p!=8&&world_index[y][x])world_upper_planes[p]++;
  }
 }assert(!fclose(f));
}
typedef struct {long double x,y;} Point;
static int polygon_coverage(int a,int b,int c,int gx,int gy,int size)
{
 int x=gx/size*size,y=gy/size*size;Point polygon[4]={{0,0},{size,0},{size,size},{0,size}},clipped[8];unsigned n=0;
 long double offset=(long double)a*x+(long double)b*y-c;
 for(unsigned j=0;j<4;j++){
  Point p=polygon[j],q=polygon[(j+1)%4];long double vp=a*p.x+b*p.y+offset,vq=a*q.x+b*q.y+offset;
  if(vp<=0)clipped[n++]=p;
  if((vp<=0)!=(vq<=0)){long double f=vp/(vp-vq);clipped[n++]=(Point){p.x+f*(q.x-p.x),p.y+f*(q.y-p.y)};}
 }
 long double area=0;for(unsigned j=0;j<n;j++)area+=clipped[j].x*clipped[(j+1)%n].y-clipped[j].y*clipped[(j+1)%n].x;
 if(area<0)area=-area;return (int)floorl(area*255/(2*size*size)+0.5L+1e-12L);
}
static int visible_member(int x,int y)
{
 int xx=x-xoffset,yy=y-current_phase+28;
 if(x<0||x>=320||y<0||y>=200||xx<0||xx>=288||yy<0||yy>=224)return -1;
 return world_member[current_row*28+yy][xx];
}
static int visible_index(int x,int y)
{return visible_member(x,y)<0?-1:world_index[current_row*28+y-current_phase+28][x-xoffset];}
static int visible_plane(int x,int y)
{return visible_member(x,y)<0?-1:world_plane[current_row*28+y-current_phase+28][x-xoffset];}
static void draw_eight(int row,int phase,int offset,int scale)
{
 current_row=row;current_phase=phase;xoffset=offset;
 mock_geometry.scale=scale;mock_geometry.footprint=8/scale;mock_geometry.dst=(SDL_Rect){0,0,320*scale,200*scale};
 mock_geometry.window_w=mock_geometry.output_w=320*scale;mock_geometry.window_h=mock_geometry.output_h=200*scale;
 shapesy_frame_reset();mapXPos=offset;backPos=phase;mapXbpPos=1;mapYPos=&megaData1.mainmap[row][0]+11;
 clear();render_mirror_shapesy_layer1(&surface,&megaData1.mainmap[row][0],offset,phase-28);assert(shapesy_pass.live);
 for(unsigned r=0;r<8;r++)blit_background_row(&surface,offset,(int)r*28+phase-28,&megaData1.mainmap[row+r][0]);
 assert(shapesy_pass.live&&!reject_reason&&shapesy_pass.row==8);
 assert(shapesy_world.count==oracle_count);
 for(unsigned i=0;i<oracle_count;i++){
  bool found=false;for(unsigned j=0;j<shapesy_world.count;j++){ShapesYContourLine p=shapesy_world.lines[j];OracleRun q=oracle_lines[i];if(p.x0==q.x0&&p.y0==q.y0&&p.x1==q.x1&&p.y1==q.y1&&p.type==q.type)found=true;}assert(found);
 }
}
static void oracle_prepare(void)
{
 memcpy(before_rgba,canvas_pixels,sizeof(before_rgba));memcpy(want_rgba,canvas_pixels,sizeof(want_rgba));
 memcpy(before_owner,hd_owner,sizeof(before_owner));memcpy(want_owner,hd_owner,sizeof(want_owner));memcpy(before_cloud,cloud_owner,sizeof(before_cloud));
 memcpy(before_index,pixels,sizeof(before_index));memcpy(before_expected,expected,sizeof(before_expected));memset(band,0,sizeof(band));
 int yoffset=current_phase-28-current_row*28,size=mock_geometry.footprint;
 for(unsigned i=0;i<oracle_count;i++){
  OracleRun r=oracle_lines[i];int dy=r.y1-r.y0,dx=r.x1-r.x0;
  int a=dy,b=-dx,c=8*dy*(r.x0+xoffset)-dx*(8*(r.y0+yoffset)+4);
  for(int wy=r.y0;wy<=r.y1;wy++){
   int y=wy+yoffset;if(y<0||y>=200||y>=current_phase+196)continue;
   int predicted=(dy*r.x0+dx*(wy-r.y0)+dy/2)/dy,world_old=-1;
   for(int wx=predicted-4;wx<=predicted+4;wx++)if(wx>=0&&wx<336&&world_boundary[wy][wx]==r.type){world_old=wx;break;}
   assert(world_old>=0);int old=world_old+xoffset;
   if(old<1||old>314||old<xoffset||old>=xoffset+288)continue;
   int tap=-1;if(r.type==1){for(int x=old;x<old+7&&x<320;x++){int v=visible_index(x,y);if(v>=48&&v<=63){tap=x;break;}}if(tap<0)continue;}
   for(int x=old-4;x<=old+4;x++){
    int source=visible_index(x,y),plane=visible_plane(x,y);if(source<1||plane==6||plane==8)continue;
    bool water=source>=48&&source<=63;if(r.type==2&&plane!=1&&plane!=4&&plane!=5)continue;
    if(r.type==1&&plane>=0&&plane<9)upper_other[plane]++;
    int k=visible_member(x,y),lx=(x-xoffset)%24*8,ly=(y-current_phase+28)%28*8;
    for(int py=0;py<8;py++)for(int px=0;px<8;px++){
     int gx=x*8+px,gy=y*8+py,at=gy*2560+gx;
     int deck=polygon_coverage(a,b,c,gx,gy,size),outer=polygon_coverage(a,b,c+8*a,gx,gy,size);assert(deck>=0&&outer>=deck&&outer<=255);
     if(r.type==1&&((plane==1&&deck==255)||(water&&!outer)))continue;
     if(r.type==2&&((plane==1&&deck==255)||(plane==4&&!outer)))continue;
     int u=lx+px,v=ly+py,w=v+u+shapesy_contour_wall_offset[k]*8;if(w<0)w=0;if(w>455)w=455;
     const Uint8 *d=shapesy_contour_deck+(v*192+u)*3,*middle=r.type==1?shapesy_contour_shadow+(v*192+u)*3:shapesy_contour_bevel+((v%16)*192+u)*3,*wall=shapesy_contour_right+(w*192+u)*3;
     Uint32 native=palette_rgb(water?source:r.type==1?visible_index(tap,y):0),color=0xff000000u;
     for(int ch=0;ch<3;ch++){unsigned bg=r.type==1?((native>>(16-ch*8))&255):wall[ch];color|=((d[ch]*deck+middle[ch]*(outer-deck)+bg*(255-outer)+127)/255)<<(16-ch*8);}
     if(band[at])overlap_pixels++;band[at]=1;want_rgba[at]=color;if(!water||outer)want_owner[at]=1;
     if(gx%size==size/2&&gy%size==size/2&&((deck>0&&deck<255)||(outer>0&&outer<255)))fractional[mock_geometry.scale==4][r.type-1]++;
    }
   }
  }
 }
}
static void verify_finish(void)
{
 render_mirror_shapesy_end();assert(!reject_reason&&shapesy_frame_check());
 assert(!memcmp(pixels,before_index,sizeof(before_index))&&!memcmp(expected,before_expected,sizeof(before_expected)));
 assert(!memcmp(cloud_owner,before_cloud,sizeof(before_cloud)));
 for(unsigned at=0;at<2560*1600;at++){
  assert(canvas_pixels[at]==want_rgba[at]&&hd_owner[at]==want_owner[at]);
  int x=at%2560/8,y=at/2560/8,source=visible_index(x,y);
  if(!source){zero_samples++;assert(canvas_pixels[at]==before_rgba[at]&&hd_owner[at]==before_owner[at]);}
  if(!band[at])assert(canvas_pixels[at]==before_rgba[at]&&hd_owner[at]==before_owner[at]);
  if(hd_owner[at]!=before_owner[at])assert(band[at]&&source>=48&&source<=63&&!before_owner[at]&&hd_owner[at]==1);
  if(canvas_pixels[at]!=before_rgba[at]){assert(band[at]);total_changed++;if(source>=48&&source<=63)water_changed++;}
 }
 assert(shapesy_present_geometry(mock_geometry.renderer,&mock_geometry.dst));SDL_Rect wrong=mock_geometry.dst;wrong.x++;assert(!shapesy_present_geometry(mock_geometry.renderer,&wrong));assert(!shapesy_present_geometry((SDL_Renderer *)3,&mock_geometry.dst));
}
static void save_masks(void)
{
 char path[1200];snprintf(path,sizeof(path),"%s.contour-masks.bin",fixture_path);FILE *f=fopen(path,"wb");assert(f);
 for(unsigned at=0;at<2560*1600;at++){int v=visible_index(at%2560/8,at/2560/8);Uint8 bits=band[at];if(v>=48&&v<=63)bits|=2;if(v==0)bits|=4;if(!band[at])bits|=8;if(before_owner[at]!=hd_owner[at])bits|=16;assert(fwrite(&bits,1,1,f)==1);}assert(!fclose(f));
}
static void checks(void)
{
 registry();oracle_world();
 for(int scale=2;scale<=4;scale+=2){
  for(int phase=0;phase<28;phase++){draw_eight(284,phase,0,scale);oracle_prepare();verify_finish();}
  const int offsets[]={0,1,23,24,31,32};for(unsigned k=0;k<6;k++){draw_eight(284,27,offsets[k],scale);oracle_prepare();verify_finish();}
 }
 bool rows[293]={0};for(unsigned i=0;i<oracle_count;i++){int row=oracle_lines[i].y0/28;if(row>292)row=292;rows[row]=true;}
 for(int row=0;row<=292;row++)if(rows[row]){draw_eight(row,27,0,4);oracle_prepare();verify_finish();}
 draw_eight(284,27,0,4);oracle_prepare();verify_finish();save_masks();
 assert(total_changed&&water_changed&&zero_samples);for(unsigned s=0;s<2;s++)for(unsigned t=0;t<2;t++)assert(fractional[s][t]);
 /* Small ordinary integrity regressions on actually used contour centers. */
 for(unsigned kind=0;kind<5;kind++){
  registry();draw_eight(284,27,0,4);oracle_prepare();int cell=-1;
  if(kind<4)for(unsigned at=0;at<2560*1600&&cell<0;at++)if(band[at]){
   int x=at%2560/8,y=at/2560/8,v=visible_index(x,y);bool water=v>=48&&v<=63;
   if((kind<2&&water)||(kind>=2&&!water&&v>0))cell=y*320+x;
  }
  if(kind<4){assert(cell>=0);int at=(cell/320)*8*2560+(cell%320)*8;
   if(kind==0)pixels[cell]^=1;if(kind==1||kind==2)canvas_pixels[at]^=1;if(kind==3)hd_owner[at]=0;
  }else megaData1.mainmap[0][0]=NULL;
  render_mirror_shapesy_end();assert(reject_reason&&!shapesy_pass.live&&!shapesy_frame.live);
 }
 /* Finite postpass mutations: exact existing source/map/display witnesses. */
 for(unsigned kind=0;kind<9;kind++){
  registry();draw_eight(284,27,0,4);render_mirror_shapesy_end();assert(shapesy_frame_check());
  if(kind==0)rgb_palette[5]^=1;
  if(kind==1){unsigned slot=0;while(lookup[slot]!=333)slot++;megaData1.shapes[slot].sh[20]^=1;}
  if(kind==2)shapesy_resources.generation++;
  if(kind==3)megaData1.mainmap[0][0]=NULL;
  if(kind==4)mock_geometry.renderer_generation++;
  if(kind==5)mock_geometry.dst.x++;
  if(kind==6)mock_geometry.scale=3;
  if(kind==7)mock_geometry_available=false;
  if(kind==8)levelBrightness=1;
  assert(!shapesy_frame_check());shapesy_frame_reset();if(kind==0)rgb_palette[5]^=1;mock_geometry_available=true;levelBrightness=-99;
 }
 registry();draw_eight(284,27,0,4);shapesy_resources.members[0].rgba[10]^=1;render_mirror_shapesy_end();assert(reject_reason&&!shapesy_pass.live);
 registry();
 printf("straight contour PASS lines=%u changed=%u water_changed=%u zero_samples=%u fractional2x=%u,%u fractional4x=%u,%u overlap_pixels=%u upper_planes=",oracle_count,total_changed,water_changed,zero_samples,fractional[0][0],fractional[0][1],fractional[1][0],fractional[1][1],overlap_pixels);
 for(unsigned p=0;p<9;p++)printf("%u%s",upper_other[p],p==8?"\n":",");
 printf("complete_map_max_run_span=%u upper_planes=",max_run_span);for(unsigned p=0;p<9;p++)printf("%u%s",world_upper_planes[p],p==8?"\n":",");
 assert(!world_upper_planes[2]&&!world_upper_planes[3]&&!world_upper_planes[4]&&!world_upper_planes[5]);
}
'''
def main():
    old=base.CHECKS
    base.CHECKS=old[:old.index('static void checks(void)')]+FOCUSED+old[old.index('int main(int argc'):].replace('assert(argc==4);','assert(argc==4);fixture_path=argv[1];')
    if '--positive-only' not in sys.argv:sys.argv.append('--positive-only')
    base.main()
    out=Path(sys.argv[sys.argv.index('--out')+1]);receipt=json.loads((out/'receipt.json').read_text());mask=out/'original-sources.bin.contour-masks.bin'
    receipt.update(straight_contour=True,oracle='independent original full-map runs and polygon-clipped destination footprint',scales=[2,4],scroll_phases=28,horizontal_offsets=[0,1,23,24,31,32],mask=dict(file=mask.name,sha256=hashlib.sha256(mask.read_bytes()).hexdigest(),width=2560,height=1600,bits={'1':'authorized contour band','2':'original water','4':'original zero','8':'outside band unchanged','16':'new water ownership'}),sanitizer_runtime_env={k:os.environ[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS') if k in os.environ},driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
