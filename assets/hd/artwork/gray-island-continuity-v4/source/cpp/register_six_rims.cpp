#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;
constexpr int W=192,H=224,N=W*H;
double clamp01(double x){return clamp(x,0.,1.);}
vector<double> distance_to(const vector<unsigned char>&a,bool occupied){
 vector<double>d(N,1e9);
 for(int q=0;q<N;q++)if((a[q*4+3]>0)==occupied)d[q]=0;
 const double dg=sqrt(2.);
 for(int y=0;y<H;y++)for(int x=0;x<W;x++){int q=y*W+x;if(x)d[q]=min(d[q],d[q-1]+1);if(y)d[q]=min(d[q],d[q-W]+1);if(x&&y)d[q]=min(d[q],d[q-W-1]+dg);if(x+1<W&&y)d[q]=min(d[q],d[q-W+1]+dg);}
 for(int y=H-1;y>=0;y--)for(int x=W-1;x>=0;x--){int q=y*W+x;if(x+1<W)d[q]=min(d[q],d[q+1]+1);if(y+1<H)d[q]=min(d[q],d[q+W]+1);if(x+1<W&&y+1<H)d[q]=min(d[q],d[q+W+1]+dg);if(x&&y+1<H)d[q]=min(d[q],d[q+W-1]+dg);}
 return d;
}
int main(int argc,char**argv){
 if(argc!=6)return 2;vector<unsigned char>packed(6*N*4),generated(6*N*4),wrapTop(N*4),wrapBottom(N*4);
 auto rd=[](const char*p,vector<unsigned char>&a){return bool(ifstream(p,ios::binary).read((char*)a.data(),a.size()));};if(!rd(argv[1],packed)||!rd(argv[2],generated)||!rd(argv[3],wrapTop)||!rd(argv[4],wrapBottom))return 3;
 vector<vector<unsigned char>> old(6),art(6),out(6);vector<vector<double>> inside(6),outside(6);
 for(int k=0;k<6;k++){old[k]={packed.begin()+k*N*4,packed.begin()+(k+1)*N*4};art[k]={generated.begin()+k*N*4,generated.begin()+(k+1)*N*4};out[k]=old[k];inside[k]=distance_to(old[k],false);outside[k]=distance_to(old[k],true);}
 // Each middle tile uses imagegen's painted wrap seam, unrolled to its edges.
 for(int k:{1,4})for(int y=0;y<H;y++)for(int x=0;x<W;x++){
  int q=4*(y*W+x),sy=k==4?max(0,y-16):y,z=4*(sy*W+(x+96)%W);double w=clamp01((32.-min(x,W-1-x))/16.);if(k==4)w*=clamp01((y-48.)/32.);auto&wrap=k==1?wrapTop:wrapBottom;
  for(int c=0;c<4;c++)art[k][q+c]=lround(art[k][q+c]*(1-w)+wrap[z+c]*w);
 }
 auto apply=[&](int k,int x,int y,const unsigned char*src,double seam){
  int q=y*W+x,p=q*4;bool occ=old[k][p+3]>0;double dist=occ?inside[k][q]:outside[k][q];
  double face=clamp01(((k<3?H-1-y:y)-3.)/8.);
  double edgeRGB=clamp01((32.-dist)/16.);double rgbWeight=max(edgeRGB,seam)*face;
  if(src[3]>0){for(int c=0;c<3;c++)out[k][p+c]=lround(old[k][p+c]*(1-rgbWeight)+src[c]*rgbWeight);}
  double alphaWeight=(occ?clamp01((16.-dist)/8.):clamp01((8.-dist)/2.))*face;
  out[k][p+3]=lround(old[k][p+3]*(1-alphaWeight)+src[3]*alphaWeight);
  if(out[k][p+3]<=3)out[k][p+3]=0;
  if(!out[k][p+3])out[k][p]=out[k][p+1]=out[k][p+2]=0;
 };
 for(int k=0;k<6;k++)for(int y=0;y<H;y++)for(int x=0;x<W;x++){double seam=(k==1||k==4)?clamp01((32.-min(x,W-1-x))/16.):0.;if(k==4)seam*=clamp01((y-48.)/32.);apply(k,x,y,&art[k][4*(y*W+x)],seam);}
 // Carry the same authored repeat-seam halves into the adjacent corner tiles.
 for(int k:{0,2,3,5})for(int y=0;y<H;y++)for(int dx=0;dx<32;dx++){
  bool leftCorner=k==0||k==3;int middle=k<3?1:4;int x=leftCorner?W-1-dx:dx,sourceX=x;double w=clamp01((32.-dx)/16.);if(k>=3)w*=clamp01((y-48.)/32.);int p=4*(y*W+x);unsigned char src[4];
  for(int c=0;c<4;c++)src[c]=lround(art[k][p+c]*(1-w)+art[middle][4*(y*W+sourceX)+c]*w);
  apply(k,x,y,src,w);
 }
 ofstream f(argv[5],ios::binary);for(auto&a:out)f.write((char*)a.data(),a.size());
}
