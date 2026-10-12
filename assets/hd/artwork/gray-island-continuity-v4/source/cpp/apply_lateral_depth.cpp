#include <fstream>
#include <vector>
#include <cmath>
#include <algorithm>
using namespace std;vector<unsigned char>r(const char*p){ifstream f(p,ios::binary);return vector<unsigned char>(istreambuf_iterator<char>(f),{});}
int main(int ac,char**av){if(ac!=5)return 1;auto a=r(av[1]),b=r(av[2]);int side=stoi(av[3]);if(a.size()!=192*224*4||b.size()!=a.size())return 2;auto o=a;for(int y=0;y<224;y++){int bound=side?191:0;while(bound>=0&&bound<192&&a[(y*192+bound)*4+3]<16)bound+=side?-1:1;for(int x=0;x<192;x++){int p=(y*192+x)*4;double d=side?bound-x:x-bound;double outside=side?191-bound:bound;double expose=clamp((outside-4.)/8.,0.,1.);expose=expose*expose*(3-2*expose);double w=clamp((32-d)/16.,0.,1.)*expose;w*=clamp(min(y,223-y)/4.,0.,1.);w=w*w*(3-2*w);if(!b[p+3]||!a[p+3])w=0;for(int c=0;c<3;c++)o[p+c]=lround(a[p+c]*(1-w)+b[p+c]*w);}}ofstream f(av[4],ios::binary);f.write((char*)o.data(),o.size());}
