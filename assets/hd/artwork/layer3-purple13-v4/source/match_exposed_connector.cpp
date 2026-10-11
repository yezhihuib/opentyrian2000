// Finite2-logical-row purple connector registration to authored adjacent actor
// edge tones. Opaque foundation geometry and every other pixel stay exact.
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
using namespace std;
int main(int argc,char**argv){if(argc!=4)return 2;const int W=576,H=672;vector<unsigned char>a(W*H*4),r(W*16*4);ifstream f(argv[1],ios::binary),g(argv[2],ios::binary);if(!f.read((char*)a.data(),a.size())||!g.read((char*)r.data(),r.size()))return 3;auto b=a;auto gate=[](const unsigned char*p){double R=p[0],G=p[1],B=p[2];return clamp((min(R-G,B-G)-5)/10.,0.,1.)*clamp((B-R+12)/12.,0.,1.)*clamp((max({R,G,B})-50)/20.,0.,1.);};int ch=0,worst=0;for(int x=0;x<W;x++){double up[3]={},dn[3]={},uw=0,dw=0;for(int xx=max(0,x-3);xx<=min(W-1,x+3);xx++)for(int yy=0;yy<2;yy++){auto p=&r[((6+yy)*W+xx)*4];auto q=&r[((8+yy)*W+xx)*4];double s=exp(-pow((xx-x)/1.5,2)/2),u=s*p[3]/255.,v=s*q[3]/255.;uw+=u;dw+=v;for(int c=0;c<3;c++){up[c]+=p[c]*u;dn[c]+=q[c]*v;}}if(uw<1||dw<1)continue;for(int y=440;y<456;y++){int p=(y*W+x)*4;double t=(y-440+.5)/16.,w=gate(&a[p])*.8;bool changed=false;for(int c=0;c<3;c++){double target=up[c]/uw*(1-t)+dn[c]/dw*t;double delta=clamp((target-a[p+c])*w,-20.,20.);b[p+c]=clamp<int>(lround(a[p+c]+delta),0,255);changed|=b[p+c]!=a[p+c];worst=max(worst,abs(int(a[p+c])-b[p+c]));}ch+=changed;}}ofstream o(argv[3],ios::binary);o.write((char*)b.data(),b.size());cout<<ch<<" pixels; max RGB delta "<<worst<<"; alpha/other rows/geometry exact\n";}
