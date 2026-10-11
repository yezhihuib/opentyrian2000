// Deterministic topology registration only. Painted RGB comes from imagegen.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
constexpr int W=192,H=224,N=10,PIX=W*H,TOTAL=N*PIX;
int ids[N]={99,100,106,107,109,110,118,119,120,101};
vector<int> par(TOTAL),countn(TOTAL);vector<bool> zero(TOTAL);
int root(int a){return par[a]==a?a:par[a]=root(par[a]);}
void unite(int a,int b){a=root(a);b=root(b);if(a!=b)par[b]=a;}
int index(int id){for(int i=0;i<N;i++)if(ids[i]==id)return i;return -1;}
int node(int i,int x,int y){return i*PIX+y*W+x;}
int main(int argc,char**argv){if(argc!=3)return 2;string dir=argv[1];
 vector<array<double,4>> old(TOTAL),target(TOTAL),sum(TOTAL),out(TOTAL),fixedsum(TOTAL),fillsum(TOTAL); vector<int> fixedcount(TOTAL),fillcount(TOTAL);
 iota(par.begin(),par.end(),0);
 for(int n=0;n<N;n++){ifstream f(dir+"/"+to_string(ids[n])+".rgba",ios::binary);if(!f)return 3;for(int p=0;p<PIX;p++){unsigned char b[4];f.read((char*)b,4);for(int c=0;c<4;c++)old[n*PIX+p][c]=b[c];}}
 ifstream pairs(argv[2]);string direction;int ia,ib;vector<int> force;
 while(pairs>>direction>>ia>>ib){int a=index(ia),b=index(ib),len=direction=="right"?H:W;
  if(a<0&&b<0)continue;
  for(int t=0;t<len;t++){int na=a<0?-1:direction=="right"?node(a,W-1,t):node(a,t,H-1);int nb=b<0?-1:direction=="right"?node(b,0,t):node(b,t,0);
   if(na>=0&&nb>=0)unite(na,nb);else force.push_back(max(na,nb));
  }
 }
 // Empty/unexported neighbors do not authorize erasing a shared cloud border.
 for(int n=0;n<N;n++)for(int y=0;y<H;y++)for(int x=0;x<W;x++)if(!x||!y||x==W-1||y==H-1){int k=node(n,x,y),r=root(k);for(int c=0;c<4;c++)sum[r][c]+=old[k][c];countn[r]++; if(ids[n]==101){for(int c=0;c<4;c++)fixedsum[r][c]+=old[k][c];fixedcount[r]++;} if(ids[n]==109){for(int c=0;c<4;c++)fillsum[r][c]+=old[k][c];fillcount[r]++;}}
 target=old;
 for(int n=0;n<N;n++)for(int y=0;y<H;y++)for(int x=0;x<W;x++)if(!x||!y||x==W-1||y==H-1){int k=node(n,x,y),r=root(k);for(int c=0;c<4;c++)target[k][c]=fixedcount[r]?fixedsum[r][c]/fixedcount[r]:fillcount[r]?fillsum[r][c]/fillcount[r]:sum[r][c]/countn[r];if(zero[r])target[k][3]=0;}
 out=old;constexpr double BAND=32;
 for(int n=0;n<N;n++)for(int y=0;y<H;y++)for(int x=0;x<W;x++){
  int k=node(n,x,y);if(ids[n]==101)continue;if(!x||!y||x==W-1||y==H-1){out[k]=target[k];continue;}
  int edges[4]={node(n,0,y),node(n,W-1,y),node(n,x,0),node(n,x,H-1)};int dist[4]={x,W-1-x,y,H-1-y};double weights=0,maxw=0;array<double,4> delta{};
  for(int e=0;e<4;e++)if(dist[e]<BAND){double z=1-dist[e]/BAND,w=z*z*(3-2*z);weights+=w;maxw=max(maxw,w);for(int c=0;c<4;c++)delta[c]+=w*(target[edges[e]][c]-old[edges[e]][c]);}
  if(weights)for(int c=0;c<4;c++)out[k][c]=clamp(old[k][c]+maxw*delta[c]/weights,0.,255.);
 }
 // The concave diagonal's top/left are planar interior, not cliff faces.
 // Continue the periodic109 texture through these connector strips rather
 // than extending a constant per-column RGB delta (which made false teeth).
 auto smooth=[](double v){v=clamp(v,0.,1.);return v*v*(3-2*v);};
 int diagonal=index(107),fill=index(109);
 for(int y=1;y<H-1;y++)for(int x=1;x<W-1;x++)if(x<32||y<32){
  double w=max(smooth(1-x/32.),smooth(1-y/32.));
  double keep=smooth(min(W-1-x,H-1-y)/32.);
  int k=node(diagonal,x,y),f=node(fill,x,y);
  for(int c=0;c<3;c++){double continued=old[k][c]*(1-w)+out[f][c]*w;out[k][c]=out[k][c]*(1-keep)+continued*keep;}
 }
 for(int n=0;n<N;n++){ofstream f(dir+"/"+to_string(ids[n])+"-registered.rgba",ios::binary);for(int p=0;p<PIX;p++)for(int c=0;c<4;c++){unsigned char b=lround(out[n*PIX+p][c]);f.write((char*)&b,1);}}
 puts("Registered scoped ground neighbor edges; 32px inward blend. Frozen101 unchanged.");
}
