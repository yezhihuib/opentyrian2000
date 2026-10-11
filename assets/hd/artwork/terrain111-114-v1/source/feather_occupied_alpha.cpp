// Alpha-only technical registration. Preserves every original zero, and keeps
// every occupied input subpixel nonzero. Only the occupied side within 4 HD
// pixels (0.5 logical pixel) of an interior hole changes; RGB is untouched.
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
using namespace std;
int main(int argc,char**argv){if(argc!=3)return 2;constexpr int W=192,H=224;vector<unsigned char>a(W*H*4);ifstream f(argv[1],ios::binary);if(!f.read((char*)a.data(),a.size()))return 3;auto b=a;int changed=0;for(int y=0;y<H;y++)for(int x=0;x<W;x++){int p=(y*W+x)*4;if(!a[p+3])continue;double d=5;for(int yy=max(0,y-4);yy<=min(H-1,y+4);yy++)for(int xx=max(0,x-4);xx<=min(W-1,x+4);xx++)if(!a[(yy*W+xx)*4+3])d=min(d,hypot(double(x-xx),double(y-yy)));double t=clamp((d-0.5)/4.0,0.,1.);int v=max(1,int(lround(255*t*t*(3-2*t))));b[p+3]=v;if(v<255)changed++;}ofstream o(argv[2],ios::binary);o.write((char*)b.data(),b.size());cout<<changed<<" occupied HD subpixels received alpha transition; all zero/nonzero support unchanged.\n";}
