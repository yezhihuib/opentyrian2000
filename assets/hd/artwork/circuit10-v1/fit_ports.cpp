#include <fstream>
#include <vector>
#include <iterator>
#include <string>
#include <map>
#include <algorithm>
std::vector<unsigned char> read(const std::string&p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char**argv){if(argc!=2)return 1;std::string p=argv[1];auto h=read(p+"/circuit-181-8.rgba"),v=read(p+"/circuit-201-8.rgba");std::map<int,std::string> ports={{181,"EW"},{182,"EWS"},{184,"ES"},{185,"WS"},{192,"NESW"},{193,"NWS"},{194,"NE"},{195,"NW"},{201,"NS"},{202,"NEW"}};for(auto [id,ds]:ports){auto a=read(p+"/circuit-"+std::to_string(id)+"-8.rgba");for(char dir:ds)for(int d=0;d<8;d++){int w=d<2?255:(8-d)*255/7;bool vertical=dir=='N'||dir=='S';for(int t=vertical?24:32;t<(vertical?176:200);t++){int x=vertical?t:(dir=='W'?d:191-d),y=vertical?(dir=='N'?d:223-d):t;for(int c=0;c<3;c++){int src=vertical?(v[t*4+c]+v[(223*192+t)*4+c]+1)/2:(h[t*192*4+c]+h[(t*192+191)*4+c]+1)/2;int k=(y*192+x)*4+c;a[k]=(a[k]*(255-w)+src*w+127)/255;}}}std::ofstream f(p+"/fitted-"+std::to_string(id)+".rgba",std::ios::binary);f.write((char*)a.data(),a.size());}}
