#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;
vector<unsigned char> read(const char*p){ifstream f(p,ios::binary);return vector<unsigned char>(istreambuf_iterator<char>(f),{});}
int main(int argc,char**argv){if(argc!=4)return 1;auto a=read(argv[1]),b=read(argv[2]);if(a.size()!=192*224*4||b.size()!=a.size())return 2;vector<unsigned char> o(a.size());for(int y=0;y<224;y++)for(int x=0;x<192;x++){int p=(y*192+x)*4;double wx=clamp((48.-abs(x-95.5))/24.,0.,1.),wy=clamp((56.-abs(y-111.5))/28.,0.,1.);double edge=clamp(min({double(x),double(y),191.-x,223.-y})/12.,0.,1.);double w=max(wx,wy)*edge;w=w*w*(3-2*w);int dx=(x+96)%192,dy=(y+112)%224,q=(dy*192+dx)*4;for(int c=0;c<3;c++)o[q+c]=lround(a[p+c]*(1-w)+b[p+c]*w);o[q+3]=255;}ofstream f(argv[3],ios::binary);f.write((char*)o.data(),o.size());}
