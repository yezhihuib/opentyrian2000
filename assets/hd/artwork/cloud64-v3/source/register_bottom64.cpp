#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
static double smooth(double t){t=std::clamp(t,0.,1.);return t*t*(3-2*t);}
int main(int argc,char**argv){if(argc!=4)return 2;const int W=192,H=224,N=W*H*4;std::vector<unsigned char>a(N),g(N);std::ifstream fa(argv[1],std::ios::binary),fg(argv[2],std::ios::binary);if(!fa.read((char*)a.data(),N)||!fg.read((char*)g.data(),N))return 3;auto b=a;for(int y=128;y<200;y++)for(int x=1;x<191;x++){int n=4*(y*W+x),gy=std::min(223,y+20),gn=4*(gy*W+x);double w=smooth((y-128)/16.)*smooth((200-y)/16.)*smooth(std::min(x,191-x)/24.);if(w<=0)continue;int ga=g[gn+3];if(ga>=250)ga=255;if(ga<4)ga=0;int cy=gy;while(cy>0&&g[4*(cy*W+x)+3]<240)--cy;int cn=4*(cy*W+x);for(int c=0;c<3;c++){int v=g[gn+3]<240?g[cn+c]:g[gn+c];b[n+c]=std::lround(a[n+c]*(1-w)+v*w);}b[n+3]=std::lround(a[n+3]*(1-w)+ga*w);}// Remove detached one-pixel alpha residue only; the connected cloud retains its authored feather.
std::vector<char> seen(W*H);std::vector<int> queue;for(int x=0;x<W;x++)if(b[x*4+3]){seen[x]=1;queue.push_back(x);}for(size_t z=0;z<queue.size();z++){int q=queue[z],x=q%W,y=q/W;int next[4]={q-1,q+1,q-W,q+W};bool ok[4]={x>0,x+1<W,y>0,y+1<H};for(int e=0;e<4;e++)if(ok[e]&&!seen[next[e]]&&b[next[e]*4+3]){seen[next[e]]=1;queue.push_back(next[e]);}}for(int q=0;q<W*H;q++)if(!seen[q]&&b[q*4+3])b[q*4+3]=0;
std::ofstream(argv[3],std::ios::binary).write((char*)b.data(),N);}
