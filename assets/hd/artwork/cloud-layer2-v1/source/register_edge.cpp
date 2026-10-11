// Registration of an imagegen-authored perimeter correction. This does not
// synthesize cloud texture or a new contour: RGBA comes from the two rasters.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <vector>
using namespace std;
constexpr int W=192,H=224;
using Pixel=array<unsigned char,4>;
vector<Pixel> read(const char*p){vector<Pixel>v(W*H);ifstream f(p,ios::binary);f.read((char*)v.data(),v.size()*4);if(f.gcount()!=v.size()*4)exit(3);return v;}
double smooth(double x){x=clamp(x,0.,1.);return x*x*(3-2*x);}
int main(int argc,char**argv){if(argc!=4)return 2;auto old=read(argv[1]),fresh=read(argv[2]),out=old;vector<array<int,2>> contour;
 for(int y=0;y<H;y++)for(int x=1;x<W-1;x++)if((old[y*W+x][3]>=128)!=(old[y*W+x+1][3]>=128))contour.push_back({x,y});
 for(int y=0;y<H;y++)for(int x=0;x<W;x++){
   double dist=1e9;for(auto c:contour)dist=min(dist,hypot(double(x-c[0]),double(y-c[1])));
   // Full authored change near the free perimeter, preserve the original HD
   // cloud interior outside a 40px (5 logical px) registration band.
   double free_weight=1-smooth((dist-24)/16);
   // Original exact RGBA at all facing tile edges preserves every prior
   // adjacency, including 55 self repetition and 42/45/52/65 transitions.
   double tile_weight=smooth(min({x,W-1-x,y,H-1-y})/16.0);
   double weight=free_weight*tile_weight;
   for(int c=0;c<4;c++)out[y*W+x][c]=lround(old[y*W+x][c]*(1-weight)+fresh[y*W+x][c]*weight);
 }
 ofstream f(argv[3],ios::binary);f.write((char*)out.data(),out.size()*4);
}
