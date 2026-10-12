#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <queue>
using namespace std;const int W=192,H=224,N=W*H;
vector<unsigned char>read(const string&p){ifstream f(p,ios::binary);return vector<unsigned char>((istreambuf_iterator<char>(f)),{});}double smooth(double x){x=clamp(x,0.,1.);return x*x*(3-2*x);}
int main(int c,char**v){if(c!=7)return 2;auto old=read(v[1]),sand=read(v[2]);if(old.size()!=N*4||sand.size()!=old.size())return 3;ifstream f(v[3]);char axis;int side,n;double feather;f>>axis>>side>>feather>>n;vector<double>a(n),b(n);for(int j=0;j<n;j++)f>>a[j]>>b[j];vector<unsigned char>out=old,mask(N),dark(N),seen(N),guard(N);vector<double>lum(N);for(int z=0;z<N;z++){lum[z]=.2126*old[z*4]+.7152*old[z*4+1]+.0722*old[z*4+2];dark[z]=lum[z]<64;}
// Protect actual coherent dark stone outlines, not isolated sand-grain speckles.
for(int z=0;z<N;z++)if(dark[z]&&!seen[z]){vector<int>q{z};seen[z]=1;for(size_t k=0;k<q.size();k++){int p=q[k],x=p%W,y=p/W;for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int xx=x+dx,yy=y+dy,j=yy*W+xx;if(xx>=0&&xx<W&&yy>=0&&yy<H&&dark[j]&&!seen[j]){seen[j]=1;q.push_back(j);}}}if(q.size()>=16)for(int p:q)guard[p]=1;}
// Fill enclosed stone interiors, then retain a compact outline/highlight collar.
vector<unsigned char>outside(N);queue<int>q;for(int z=0;z<N;z++)if((z/W==0||z/W==H-1||z%W==0||z%W==W-1)&&!guard[z]){outside[z]=1;q.push(z);}while(!q.empty()){int z=q.front();q.pop();int x=z%W,y=z/W;for(auto d:vector<pair<int,int>>{{1,0},{-1,0},{0,1},{0,-1}}){int xx=x+d.first,yy=y+d.second,j=yy*W+xx;if(xx>=0&&xx<W&&yy>=0&&yy<H&&!guard[j]&&!outside[j]){outside[j]=1;q.push(j);}}}for(int z=0;z<N;z++)if(!outside[z])guard[z]=1;
vector<int>dist(N,999);for(int z=0;z<N;z++)if(guard[z]){dist[z]=0;q.push(z);}while(!q.empty()){int z=q.front();q.pop();if(dist[z]>=8)continue;int x=z%W,y=z/W;for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int xx=x+dx,yy=y+dy,j=yy*W+xx;if(xx>=0&&xx<W&&yy>=0&&yy<H&&dist[j]>dist[z]+1){dist[j]=dist[z]+1;q.push(j);}}}
for(int y=0;y<H;y++)for(int x=0;x<W;x++){int z=y*W+x;double w=1,distance=999;if(axis!='f'){double t=axis=='x'?y:x,pos=axis=='x'?x:y;int k=0;while(k+2<n&&t>a[k+1])k++;double u=smooth((t-a[k])/(a[k+1]-a[k]));double boundary=b[k]*(1-u)+b[k+1]*u;distance=side*(pos-boundary);w=smooth(distance/feather)*smooth((dist[z]-3.)/4.);}mask[z]=lround(w*255);w=mask[z]/255.;double shade=1;if(axis!='f'&&w>0){double sum=0;int count=0;for(int dy=-12;dy<=12;dy++)for(int dx=-12;dx<=12;dx++){sum+=lum[clamp(y+dy,0,H-1)*W+clamp(x+dx,0,W-1)];count++;}double ao=clamp((sum/count)/88.2,.72,1.10);double edge=smooth((64-distance)/48.);shade=1+(ao-1)*edge;}for(int k=0;k<3;k++)out[z*4+k]=lround(clamp(old[z*4+k]*(1-w)+sand[z*4+k]*shade*w,0.,255.));out[z*4+3]=old[z*4+3];}
ofstream(v[4],ios::binary).write((char*)out.data(),out.size());ofstream(v[5],ios::binary).write((char*)mask.data(),mask.size());ofstream(v[6])<<"{\"protected_pixels\":"<<count(mask.begin(),mask.end(),0)<<",\"pure_new_sand_pixels\":"<<count(mask.begin(),mask.end(),255)<<",\"original_alpha_exact\":true}\n";}
