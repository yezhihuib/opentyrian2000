#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;
vector<unsigned char> rd(const char*p){ifstream f(p,ios::binary);return vector<unsigned char>(istreambuf_iterator<char>(f),{});}
int main(int argc,char**argv){if(argc!=4)return 1;auto a=rd(argv[1]),b=rd(argv[2]);if(a.size()!=192*224*4||b.size()!=a.size())return 2;vector<unsigned char> o=a;for(int y=0;y<224;y++)for(int x=0;x<192;x++){int p=(y*192+x)*4;double d=min({double(x),double(y),191.-x,223.-y});double w=clamp((d-8.)/16.,0.,1.);w=w*w*(3-2*w);for(int c=0;c<3;c++)o[p+c]=lround(a[p+c]*(1-w)+b[p+c]*w);o[p+3]=255;}ofstream f(argv[3],ios::binary);f.write((char*)o.data(),o.size());}
