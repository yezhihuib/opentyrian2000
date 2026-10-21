/* Fresh reconstruction test bridge, not shipped in the runtime. */
#include "common_menu_runs.h"
int reconstructed_numeric_dump(const char *text,Uint8 *out,unsigned capacity,int *metrics)
{
 CommonMenuNumericRun r;if(!common_menu_numeric_runs_layout(text,&r))return -1;
 if(!out||!metrics||r.width>capacity||r.height>capacity/r.width)return -2;
 metrics[0]=r.dx;metrics[1]=r.dy;metrics[2]=(int)r.width;metrics[3]=(int)r.height;metrics[4]=(int)r.advance256;
 for(unsigned y=0;y<r.height;y++)for(unsigned x=0;x<r.width;x++){
  Uint8 a,v;if(!common_menu_numeric_runs_sample(&r,r.dx+x,r.dy+y,&a,&v)||(a&&v!=7)||(!a&&v))return -3;
  out[y*r.width+x]=a;
 }
 return (int)(r.width*r.height);
}
