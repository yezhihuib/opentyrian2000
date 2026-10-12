#include <fstream>
#include <vector>
#include <iterator>
#include <stdexcept>
#include <string>
std::vector<unsigned char> read(const std::string&p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char**argv){if(argc!=2)return 1;std::string p=argv[1];for(int id:{181,182,184,185,192,193,194,195,201,202}){auto a=read(p+"/raw-"+std::to_string(id)+".rgba"),b=read(p+"/base132.rgba"),m=read(p+"/mask-"+std::to_string(id)+".raw");if(a.size()!=172032||b.size()!=a.size()||m.size()*4!=a.size())throw std::runtime_error("size");for(size_t i=0;i<m.size();++i)for(int c=0;c<3;c++)b[i*4+c]=(a[i*4+c]*unsigned(m[i])+b[i*4+c]*unsigned(255-m[i])+127)/255;std::ofstream f(p+"/circuit-"+std::to_string(id)+"-8.rgba",std::ios::binary);f.write((char*)b.data(),b.size());}}
