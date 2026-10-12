#include <fstream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
using B=std::vector<unsigned char>;
B rd(std::string p){std::ifstream f(p,std::ios::binary);return B(std::istreambuf_iterator<char>(f),{});}void wr(std::string p,const B&a){std::ofstream(p,std::ios::binary).write((char*)a.data(),a.size());}
double smooth(double x){x=std::clamp(x,0.,1.);return x*x*(3-2*x);}int mix(int a,int b,int w){return (a*(255-w)+b*w+127)/255;}
int main(int n,char**v){if(n!=2)return 2;std::string p=v[1];auto frame=rd(p+"/frame"),grass=rd(p+"/grass"),front=rd(p+"/front234");int ids[]={211,212,213,221,222,223,231,232,233,234,215,224,225};std::vector<B>base(13,B(192*224*4)),mask(13);for(int k=0;k<13;k++){mask[k]=rd(p+"/w"+std::to_string(ids[k]));if(mask[k].size()!=192*224)return 3;for(int y=0;y<224;y++)for(int x=0;x<192;x++){int s=(y*192+x)*4;int gx=(k%3)*192+x,gy=(k/3)*224+y;int q=(gy*576+gx)*4;int a=0;double green=0;if(k<9){a=frame[q+3];green=smooth((frame[q+1]-std::max(frame[q],frame[q+2])-6.)/12.);}for(int c=0;c<3;c++){int rgb=grass[s+c];if(k<9){double fac[3]={0.68039836,0.87371704,0.61345};int z=std::lround(frame[q+c]*(1+(fac[c]-1)*green));rgb=mix(rgb,z,a);}else if(k==9)rgb=front[s+c];base[k][s+c]=rgb;}base[k][s+3]=255;}} 
// Shared source-contiguous connector strips. Opposite sides use consecutive, not equal, samples.
auto copyH=[&](int k,bool right,int srcK,bool srcRight){B old=base[k],ow=mask[k];for(int y=0;y<224;y++)for(int d=0;d<32;d++){int x=right?191-d:d;int sx=srcRight?191-d:d;int w=std::lround(255*(1-smooth(d/31.)));int t=y*192+x,s=y*192+sx;for(int c=0;c<3;c++)base[k][t*4+c]=mix(old[t*4+c],base[srcK][s*4+c],w);mask[k][t]=mix(ow[t],mask[srcK][s],w);}};
auto copyV=[&](int k,bool bottom,int srcK,bool srcBottom){B old=base[k],ow=mask[k];for(int x=0;x<192;x++)for(int d=0;d<32;d++){int y=bottom?223-d:d,sy=srcBottom?223-d:d;int w=std::lround(255*(1-smooth(d/31.)));int t=y*192+x,s=sy*192+x;for(int c=0;c<3;c++)base[k][t*4+c]=mix(old[t*4+c],base[srcK][s*4+c],w);mask[k][t]=mix(ow[t],mask[srcK][s],w);}};
// Top row repeats use211R/212L; left side uses211S/221N; right side213S/223N.
copyH(1,true,0,true);copyH(2,false,1,false);copyV(3,true,0,true);copyV(6,false,3,false);copyV(5,true,2,true);copyV(8,false,5,false);
// Every front reuse pair uses231R/232L. Endcap exterior sides remain ground.
copyH(7,true,6,true);copyH(8,false,7,false);copyH(9,false,7,false);copyH(9,true,6,true);
// Ground-facing outermost samples retain accepted69's local phase, without moving silhouettes.
for(int k=0;k<13;k++)for(int y=0;y<224;y++)for(int x=0;x<192;x++){bool L=(ids[k]==211||ids[k]==221||ids[k]==231),R=(ids[k]==213||ids[k]==223||ids[k]==233),T=(ids[k]==211||ids[k]==212||ids[k]==213),D=(ids[k]>=231&&ids[k]<=234);double g=0;if(L)g=std::max(g,1-smooth(x/12.));if(R)g=std::max(g,1-smooth((191-x)/12.));if(T)g=std::max(g,1-smooth(y/16.));if(D)g=std::max(g,smooth((y-192.)/31.));int z=std::lround(255*g),t=y*192+x;for(int c=0;c<3;c++)base[k][t*4+c]=mix(base[k][t*4+c],grass[t*4+c],z);mask[k][t]=mix(mask[k][t],0,z);}
for(int k=0;k<13;k++){wr(p+"/base"+std::to_string(ids[k]),base[k]);wr(p+"/mask"+std::to_string(ids[k]),mask[k]);} }
