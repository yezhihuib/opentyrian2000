#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
using B=std::vector<unsigned char>;
B read(const char*p){std::ifstream f(p,std::ios::binary);return B(std::istreambuf_iterator<char>(f),{});}
void write(const char*p,const B&b){std::ofstream(p,std::ios::binary).write((const char*)b.data(),b.size());}
double smooth(double a){a=std::clamp(a,0.,1.);return a*a*(3-2*a);}
int main(int argc,char**v){if(argc!=5)return 2;auto old=read(v[1]),gen=read(v[2]);int W=768,H=896;if(old.size()!=W*H*4||old.size()!=gen.size())return 3;B out(old.size()),mask(W*H);for(int y=0;y<H;++y)for(int x=0;x<W;++x){double dx=std::abs(x+.5-W/2.),dy=std::abs(y+.5-H/2.);int a=std::lround(255*std::max(1-smooth((dx-24)/40),1-smooth((dy-24)/40)));int s=y*W+x;int t=((y+H/2)%H)*W+(x+W/2)%W;mask[t]=a;for(int c=0;c<3;c++)out[t*4+c]=(old[s*4+c]*(255-a)+gen[s*4+c]*a+127)/255;out[t*4+3]=255;}write(v[3],out);write(v[4],mask);}
