#include <fstream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;int main(int ac,char**av){if(ac!=3)return 1;ifstream f(av[1],ios::binary);vector<unsigned char>a((istreambuf_iterator<char>(f)),{});if(a.size()!=192*224*4)return 2;vector<char>s(192*224);int erased=0;for(int p=0;p<192*224;p++){if(s[p]||!a[p*4+3])continue;vector<int>v;queue<int>q;q.push(p);s[p]=1;bool edge=false;int mx=0;while(!q.empty()){int z=q.front();q.pop();v.push_back(z);int x=z%192,y=z/192;edge|=x==0||x==191||y==0||y==223;mx=max(mx,int(a[z*4+3]));for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int nx=x+dx,ny=y+dy;if(nx>=0&&nx<192&&ny>=0&&ny<224){int w=ny*192+nx;if(!s[w]&&a[w*4+3]){s[w]=1;q.push(w);}}}}if(!edge&&v.size()<=16&&mx<=6)for(int z:v){for(int c=0;c<4;c++)a[z*4+c]=0;erased++;}}ofstream o(av[2],ios::binary);o.write((char*)a.data(),a.size());return 0;}
