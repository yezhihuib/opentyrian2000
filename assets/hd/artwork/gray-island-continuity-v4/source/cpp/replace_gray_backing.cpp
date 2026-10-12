#include <fstream>
#include <vector>
#include <queue>
#include <cmath>
#include <algorithm>
using namespace std;const int W=192,H=224,N=W*H;
vector<unsigned char>rd(const char*p){ifstream f(p,ios::binary);return vector<unsigned char>(istreambuf_iterator<char>(f),{});}
vector<double>distance(const vector<unsigned char>&m){vector<double>d(N,10000);for(int p=0;p<N;p++)if(m[p])d[p]=0;for(int t=0;t<2;t++)for(int yy=0;yy<H;yy++)for(int xx=0;xx<W;xx++){int y=t?H-1-yy:yy,x=t?W-1-xx:xx,p=y*W+x;for(int j=-1;j<=1;j++)for(int i=-1;i<=1;i++){int nx=x+i,ny=y+j;if(nx>=0&&nx<W&&ny>=0&&ny<H)d[p]=min(d[p],d[ny*W+nx]+(i&&j?sqrt(2.):1.));}}return d;}
int main(int ac,char**av){if(ac!=6)return 1;auto a=rd(av[1]),b=rd(av[2]);if(a.size()!=N*4||b.size()!=a.size())return 2;int shift=stoi(av[3]);vector<unsigned char>m(N),seen(N);for(int p=0;p<N;p++){int r=a[p*4],g=a[p*4+1],bl=a[p*4+2];m[p]=(a[p*4+3]&&((r-g>=2&&bl-g>=5)||(bl-r>=8&&g-r>=4)));}auto d=distance(m);for(int p=0;p<N;p++)if(d[p]<=3)m[p]=1;queue<int>q;for(int p=0;p<N;p++)if((p%W==0||p%W==W-1||p/W==0||p/W==H-1)&&!m[p]){seen[p]=1;q.push(p);}while(!q.empty()){int p=q.front();q.pop();int x=p%W,y=p/W;for(auto off:vector<pair<int,int>>{{1,0},{-1,0},{0,1},{0,-1}}){int nx=x+off.first,ny=y+off.second;if(nx>=0&&nx<W&&ny>=0&&ny<H){int z=ny*W+nx;if(!m[z]&&!seen[z]){seen[z]=1;q.push(z);}}}}for(int p=0;p<N;p++)if(!seen[p])m[p]=1;d=distance(m);auto o=a;vector<unsigned char>mask(N);for(int y=0;y<H;y++)for(int x=0;x<W;x++){int p=y*W+x,z=((y+shift+H)%H*W+x)*4;double w=clamp((d[p]-6.)/10.,0.,1.);w=w*w*(3-2*w);if(!a[p*4+3])w=0;mask[p]=lround((1-w)*255);for(int c=0;c<3;c++)o[p*4+c]=lround(a[p*4+c]*(1-w)+b[z+c]*w);}ofstream f(av[4],ios::binary);f.write((char*)o.data(),o.size());ofstream k(av[5],ios::binary);k.write((char*)mask.data(),mask.size());}
