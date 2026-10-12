#include <vector>
#include <fstream>
#include <queue>
#include <cmath>
#include <algorithm>
using namespace std;const int W=192,H=224,N=W*H;vector<unsigned char>read(char*p){ifstream f(p,ios::binary);return vector<unsigned char>((istreambuf_iterator<char>(f)),{});}int main(int c,char**v){if(c!=6)return 2;auto old=read(v[1]),sand=read(v[2]),mask=read(v[3]);if(old.size()!=N*4||sand.size()!=old.size()||mask.size()!=N)return 3;vector<int>d(N,999);queue<int>q;for(int z=0;z<N;z++)if(!mask[z]){d[z]=0;q.push(z);}while(!q.empty()){int z=q.front();q.pop();if(d[z]>=5)continue;int x=z%W,y=z/W;for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int xx=x+dx,yy=y+dy,j=yy*W+xx;if(xx>=0&&xx<W&&yy>=0&&yy<H&&d[j]>d[z]+1){d[j]=d[z]+1;q.push(j);}}}auto out=old;vector<unsigned char>w(N);for(int z=0;z<N;z++){double a=mask[z]?clamp((d[z]-1)/3.,0.,1.):0;a=a*a*(3-2*a);w[z]=lround(a*255);a=w[z]/255.;for(int k=0;k<3;k++)out[z*4+k]=lround(old[z*4+k]*(1-a)+sand[z*4+k]*a);}ofstream(v[4],ios::binary).write((char*)out.data(),out.size());ofstream(v[5],ios::binary).write((char*)w.data(),w.size());}
