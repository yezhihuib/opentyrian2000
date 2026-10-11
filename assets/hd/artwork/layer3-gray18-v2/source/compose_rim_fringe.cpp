// Bounded technical registration of an imagegen-authored fringe correction.
// Original transparent cells are never filled. RGB edits are restricted to
// dark occupied pixels within 2.5 logical px of the original free silhouette.
// Alpha may recede at most 1 logical px, and tile-border bytes stay fixed.
#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <deque>
using namespace std;
int main(int argc,char**argv){if(argc!=4)return 2;constexpr int W=192,H=224;vector<unsigned char>a(W*H*4),g(a.size());ifstream f(argv[1],ios::binary),n(argv[2],ios::binary);if(!f.read((char*)a.data(),a.size())||!n.read((char*)g.data(),g.size()))return 3;auto b=a;int cr=0,ca=0,cz=0;double maxd=0;auto smooth=[](double t){t=clamp(t,0.,1.);return t*t*(3-2*t);};for(int y=0;y<H;y++)for(int x=0;x<W;x++){int p=(y*W+x)*4;if(!a[p+3])continue;double d=21;for(int yy=max(0,y-20);yy<=min(H-1,y+20);yy++)for(int xx=max(0,x-20);xx<=min(W-1,x+20);xx++)if(!a[(yy*W+xx)*4+3])d=min(d,hypot(double(x-xx),double(y-yy)));double border=min({x,y,W-1-x,H-1-y});double join=smooth((border-1)/4.0);double dark=smooth((52.-max({a[p],a[p+1],a[p+2]}))/24.);double t=smooth((20-d)/8.0)*join*dark;if(g[p+3]>32)for(int c=0;c<3;c++)b[p+c]=lround(a[p+c]*(1-t)+g[p+c]*t);double at=smooth((8.-d)/4.0)*join;int target=min<int>(a[p+3],g[p+3]);b[p+3]=lround(a[p+3]*(1-at)+target*at);if(b[p+3]==0){b[p]=b[p+1]=b[p+2]=0;cz++;}bool rgb=false;for(int c=0;c<3;c++)rgb|=a[p+c]!=b[p+c];if(rgb)cr++;if(a[p+3]!=b[p+3]){ca++;maxd=max(maxd,d);}}
// Keep original occupied support at a visually negligible alpha floor of 1.
// This prevents both isolated zero holes and detached subpixel edge fragments.
int support_floor=0;for(int i=0;i<W*H;i++)if(a[i*4+3]&&!b[i*4+3]){b[i*4+3]=1;for(int c=0;c<3;c++)b[i*4+c]=a[i*4+c];support_floor++;}cerr<<"occupied zero-alpha subpixels clamped to 1: "<<support_floor<<"\n";
cr=ca=cz=0;for(int i=0;i<W*H;i++){bool rgb=false;for(int c=0;c<3;c++)rgb|=a[i*4+c]!=b[i*4+c];cr+=rgb;ca+=a[i*4+3]!=b[i*4+3];cz+=a[i*4+3]&&!b[i*4+3];}
ofstream o(argv[3],ios::binary);o.write((char*)b.data(),b.size());cout<<"{\"rgb_changed\":"<<cr<<",\"alpha_changed\":"<<ca<<",\"new_zero_hd_subpixels\":"<<cz<<",\"max_alpha_distance_hd\":"<<maxd<<"}\n";}
