#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
// Union imagegen's gently wider fringe with accepted v2 grass. Existing
// grass RGB and all tile-facing 4-HD-pixel joins remain byte-identical.
int main(int argc,char**argv){
 if(argc!=4)return 2;const int W=384,H=672,N=W*H;
 std::vector<unsigned char> old(N*4),art(N*4);
 if(!std::ifstream(argv[1],std::ios::binary).read((char*)old.data(),old.size())||!std::ifstream(argv[2],std::ios::binary).read((char*)art.data(),art.size()))return 3;
 auto out=old;const double ramp[5][3]={{4,40,12},{8,52,12},{12,65,16},{20,77,20},{32,89,28}};
 for(int y=0;y<H;y++)for(int x=0;x<W;x++){
  int n=4*(y*W+x);if(int(old[n+1])-std::max(old[n],old[n+2])>=3)continue;
  double confidence=int(art[n+1])-std::max(art[n],art[n+2]);
  int edge=std::min({x%192,191-x%192,y%224,223-y%224});
  double w=std::clamp((confidence-2.)/12.,0.,1.)*std::clamp((edge-3.)/4.,0.,1.);
  double g=std::clamp(double(art[n+1]),40.,89.);int lo=0;while(lo<3&&g>ramp[lo+1][1])lo++;
  double t=(g-ramp[lo][1])/(ramp[lo+1][1]-ramp[lo][1]);
  for(int c=0;c<3;c++)out[n+c]=std::lround(old[n+c]*(1-w)+(ramp[lo][c]*(1-t)+ramp[lo+1][c]*t)*w);
 }
 std::ofstream(argv[3],std::ios::binary).write((char*)out.data(),out.size());
}
