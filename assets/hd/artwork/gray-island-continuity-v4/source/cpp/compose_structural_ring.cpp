#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
using namespace std; const int W=192,H=224;
vector<unsigned char>rd(const char*p){ifstream f(p,ios::binary);return vector<unsigned char>(istreambuf_iterator<char>(f),{});}
double ss(double v){v=clamp(v,0.,1.);return v*v*(3-2*v);}
vector<double> dist(vector<unsigned char>&a,bool inside){vector<double>d(W*H,10000);for(int p=0;p<W*H;p++)if(bool(a[p*4+3])!=inside)d[p]=0;for(int pass=0;pass<2;pass++)for(int yy=0;yy<H;yy++)for(int xx=0;xx<W;xx++){int y=pass?H-1-yy:yy,x=pass?W-1-xx:xx,p=y*W+x;for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int nx=x+dx,ny=y+dy;if(nx>=0&&nx<W&&ny>=0&&ny<H)d[p]=min(d[p],d[ny*W+nx]+(dx&&dy?sqrt(2.):1.));}}return d;}
int main(int ac,char**av){if(ac!=7)return 1;int id=stoi(av[1]);string faces=av[2];auto a=rd(av[3]),g=rd(av[4]),b=rd(av[5]);if(a.size()!=W*H*4||g.size()!=a.size()||b.size()!=a.size())return 2;auto di=dist(a,true),doo=dist(a,false);bool lower=id>=141;auto o=a;for(int y=0;y<H;y++)for(int x=0;x<W;x++){int q=y*W+x,p=q*4;double d=a[p+3]?di[q]:doo[q];double wa=1-ss((d-6)/10.);double edge=min({x,y,W-1-x,H-1-y});wa*=ss(edge/4.);double alpha=a[p+3]*(1-wa)+g[p+3]*wa;double wg=(1-ss((di[q]-24)/40.))*(g[p+3]/255.);if(lower)wg=max(wg,ss((y-64.)/24.)*(1-ss((y-136.)/24.))*(g[p+3]/255.));double face=0;for(char c:faces){double z=c=='N'?y:c=='S'?H-1-y:c=='W'?x:W-1-x;face=max(face,1-ss((z-4.)/12.));}if(lower)face*=1-ss((y-64.)/24.);wg*=1-face;for(int c=0;c<3;c++){double base=b[p+c];if(lower){double z=ss((y-88.)/32.);base=base*(1-z)+a[p+c]*z;}o[p+c]=lround(base*(1-wg)+g[p+c]*wg);}o[p+3]=lround(alpha);if(o[p+3]<=3)o[p]=o[p+1]=o[p+2]=o[p+3]=0;}
ofstream f(av[6],ios::binary);f.write((char*)o.data(),o.size());}
