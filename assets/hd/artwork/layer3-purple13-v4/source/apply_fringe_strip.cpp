#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
int main(int argc,char**argv){if(argc!=4)return 2;int W=192,H=224;std::vector<unsigned char>a(W*H*4),g(W*16*4);std::ifstream(argv[1],std::ios::binary).read((char*)a.data(),a.size());std::ifstream(argv[2],std::ios::binary).read((char*)g.data(),g.size());auto b=a;for(int y=208;y<224;y++)for(int x=0;x<W;x++){int n=4*(y*W+x);double w=std::pow((y-207)/16.,1.5);double L=.2126*a[n]+.7152*a[n+1]+.0722*a[n+2],G=.2126*g[n-208*W*4]+.7152*g[n-208*W*4+1]+.0722*g[n-208*W*4+2];double ratio=std::min(1.,G/std::max(1.,L));double highlight=std::clamp((L-45)/75.,0.,1.);double f=1-w*(1-ratio+0.15*highlight);f=std::max(.75,f);for(int c=0;c<3;c++)b[n+c]=std::max(int(a[n+c])-28,int(std::lround(a[n+c]*f)));}std::ofstream(argv[3],std::ios::binary).write((char*)b.data(),b.size());}
