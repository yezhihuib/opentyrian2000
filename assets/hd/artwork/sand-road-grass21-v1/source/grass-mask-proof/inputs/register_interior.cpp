#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
// Deterministic registration of imagegen-authored interior detail. All old
// sand, alpha, 4-HD-pixel tile borders and the old exterior fringe are frozen.
int main(int argc,char**argv){
 if(argc!=5)return 2;const int W=192,H=224,N=W*H;
 std::vector<unsigned char> old(N*4),art(N*4),sand(N*4);
 auto read=[&](const char*p,std::vector<unsigned char>&a){return bool(std::ifstream(p,std::ios::binary).read((char*)a.data(),a.size()));};
 if(!read(argv[1],old)||!read(argv[2],art)||!read(argv[3],sand))return 3;
 std::vector<double> mask(N),weight(N);
 for(int q=0;q<N;q++)mask[q]=(old[q*4+1]-std::max(old[q*4],old[q*4+2])>=12 && (old[q*4]!=sand[q*4]||old[q*4+1]!=sand[q*4+1]||old[q*4+2]!=sand[q*4+2]));
 double aMean=0,oMean=0,denom=0;
 for(int y=0;y<H;y++)for(int x=0;x<W;x++){
  int q=y*W+x;double dist=8.;
  if(!mask[q])dist=0;else for(int dy=-8;dy<=8;dy++)for(int dx=-8;dx<=8;dx++){int xx=x+dx,yy=y+dy;if(xx>=0&&xx<W&&yy>=0&&yy<H&&!mask[yy*W+xx])dist=std::min(dist,std::hypot(double(dx),double(dy)));}
  double edge=std::min({x,y,W-1-x,H-1-y});
  weight[q]=std::clamp((dist-2.)/4.,0.,1.)*std::clamp((edge-3.)/8.,0.,1.);
  aMean+=weight[q]*art[q*4+1];oMean+=weight[q]*old[q*4+1];denom+=weight[q];
 }
 double shift=denom?(aMean-oMean)/denom:0;
 const double ramp[5][3]={{4,40,12},{8,52,12},{12,65,16},{20,77,20},{32,89,28}};
 auto out=old;double before=0,after=0;
 for(int q=0;q<N;q++){
  double g=std::clamp(art[q*4+1]-shift,40.,89.);int lo=0;while(lo<3&&g>ramp[lo+1][1])lo++;
  double t=(g-ramp[lo][1])/(ramp[lo+1][1]-ramp[lo][1]);
  for(int c=0;c<3;c++){double v=ramp[lo][c]*(1-t)+ramp[lo+1][c]*t;out[q*4+c]=std::lround(old[q*4+c]*(1-weight[q])+v*weight[q]);}
  before+=old[q*4+1]*weight[q];after+=out[q*4+1]*weight[q];
 }
 std::cerr<<"shift="<<shift<<" weightedG "<<before/std::max(1.,denom)<<" -> "<<after/std::max(1.,denom)<<"\n";
 std::ofstream(argv[4],std::ios::binary).write((char*)out.data(),out.size());
}
