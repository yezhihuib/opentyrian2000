// Deterministic edge registration. All authored RGB is imagegen or frozen accepted art.
// Only the one added IDs may change. A harmonic correction inside a 32-HD-pixel
// band avoids extending per-column edge differences into false ledges or teeth.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
constexpr int W=192,H=224,P=W*H,BAND=32;
const vector<int> ids={113,36,58,98,101,110,118};
int main(int argc,char**argv){
 if(argc!=3){cerr<<"usage: register_plateau_edges rgba_directory pairs_file\n";return 2;}
 const string dir=argv[1];const int total=ids.size()*P;
 vector<array<double,3>> rgb(total),sums(total),frozen(total),target(total);vector<int> count(total),fc(total),parent(total);
 vector<unsigned char> alpha(total);
 iota(parent.begin(),parent.end(),0);
 auto root=[&](int n){while(parent[n]!=n){parent[n]=parent[parent[n]];n=parent[n];}return n;};
 auto node=[](int i,int x,int y){return i*P+y*W+x;};
 auto idx=[](int id){auto i=find(ids.begin(),ids.end(),id);return i==ids.end()?-1:int(i-ids.begin());};
 for(int i=0;i<int(ids.size());i++){
  ifstream f(dir+"/"+to_string(ids[i])+".rgba",ios::binary);if(!f)return 3;
  for(int p=0;p<P;p++){unsigned char b[4];if(!f.read((char*)b,4)||(i>=1&&b[3]!=255)||(b[3]!=0&&b[3]!=255))return 4;alpha[i*P+p]=b[3];for(int c=0;c<3;c++)rgb[i*P+p][c]=b[c];}
  char extra;if(f.read(&extra,1))return 5;
 }
 ifstream pairs(argv[2]);string direction;int a,b,np=0;
 while(pairs>>direction>>a>>b){int ia=idx(a),ib=idx(b);if(ia<0||ib<0||(ia>=1&&ib>=1))return 6;np++;
  for(int t=0;t<(direction=="right"?H:W);t++){
   int na=direction=="right"?node(ia,W-1,t):node(ia,t,H-1);
   int nb=direction=="right"?node(ib,0,t):node(ib,t,0);
   na=root(na);nb=root(nb);if(na!=nb)parent[nb]=na;
  }
 }
 for(int i=0;i<int(ids.size());i++)for(int y=0;y<H;y++)for(int x=0;x<W;x++)if(!x||!y||x==W-1||y==H-1){
  int k=node(i,x,y),r=root(k);count[r]++;for(int c=0;c<3;c++)sums[r][c]+=rgb[k][c];
  if(i>=1){fc[r]++;for(int c=0;c<3;c++)frozen[r][c]+=rgb[k][c];}
 }
 target=rgb;
 for(int i=0;i<1;i++)for(int y=0;y<H;y++)for(int x=0;x<W;x++)if(!x||!y||x==W-1||y==H-1){int k=node(i,x,y),r=root(k);for(int c=0;c<3;c++)target[k][c]=fc[r]?frozen[r][c]/fc[r]:sums[r][c]/count[r];}
 for(int i=0;i<1;i++){
  vector<array<double,3>> delta(P);vector<int> band;
  for(int y=0;y<H;y++)for(int x=0;x<W;x++){
   int d=min(min(x,W-1-x),min(y,H-1-y)),p=y*W+x;
   if(!d)for(int c=0;c<3;c++)delta[p][c]=target[i*P+p][c]-rgb[i*P+p][c];
   else if(d<BAND)band.push_back(p);
  }
  int iteration=0;double err=0;
  for(;iteration<1800;iteration++){
   err=0;
   for(int p:band)for(int c=0;c<3;c++){
    double desired=(delta[p-1][c]+delta[p+1][c]+delta[p-W][c]+delta[p+W][c])*0.25;
    double step=1.65*(desired-delta[p][c]);delta[p][c]+=step;err=max(err,abs(step));
   }
   if(err<0.0001)break;
  }
  ofstream f(dir+"/"+to_string(ids[i])+"-registered.rgba",ios::binary);
  for(int p=0;p<P;p++){unsigned char b[4];for(int c=0;c<3;c++)b[c]=lround(clamp(rgb[i*P+p][c]+delta[p][c],0.,255.));b[3]=alpha[i*P+p];if(!b[3])b[0]=b[1]=b[2]=0;f.write((char*)b,4);}
  cout<<ids[i]<<" iterations="<<iteration<<" residual="<<err<<"\n";
 }
 cout<<"Registered "<<np<<" real-map edges; 1 new ID only; frozen assets read-only.\n";
}
