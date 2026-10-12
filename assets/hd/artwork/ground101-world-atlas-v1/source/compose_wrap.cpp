#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
using B=std::vector<unsigned char>;
B read(const char*p){std::ifstream f(p,std::ios::binary);return B(std::istreambuf_iterator<char>(f),{});}
void write(const char*p,const B&b){std::ofstream(p,std::ios::binary).write((const char*)b.data(),b.size());}
double smooth(double a){a=std::clamp(a,0.,1.);return a*a*(3-2*a);}
int main(int argc,char**v){if(argc!=6)return 2;auto old=read(v[1]),gen=read(v[2]),hor=read(v[3]);int W=768,H=896;if(old.size()!=W*H*4||old.size()!=gen.size()||hor.size()!=W*256*4)return 3;B out(old.size()),mask(W*H);for(int y=0;y<H;++y)for(int x=0;x<W;++x){double dx=std::abs(x+.5-W/2.),dy=std::abs(y+.5-H/2.);int av=std::lround(255*(1-smooth((dx-16)/32))),ah=std::lround(255*(1-smooth((dy-16)/32)));int s=y*W+x;int t=((y+H/2)%H)*W+(x+W/2)%W;mask[t]=255-(255-av)*(255-ah)/255;for(int c=0;c<3;c++){int q=(old[s*4+c]*(255-av)+gen[s*4+c]*av+127)/255;if(ah)q=(q*(255-ah)+hor[((y-320)*W+x)*4+c]*ah+127)/255;out[t*4+c]=q;}out[t*4+3]=255;}write(v[4],out);write(v[5],mask);}
