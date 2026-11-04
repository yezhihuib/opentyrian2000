/* Private independent 340 corner, slots of original23 unchanged. */
static bool private_static340_source_matches(unsigned id,const Uint8*data)
{
 if(id!=340||!data)return false;
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(size_t n=0;n<672;n++){h^=data[n];h*=UINT64_C(0x100000001b3);}
 return h==UINT64_C(0x5488748d1b6f0a96);
}
static bool private_static340_ready(void)
{
 if(private_static340_source_fault||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||!game_probe_assets)return false;
 Asset*a=&assets[599];
 if(!a->initialized){
 a->initialized=true;a->bank=ASSET_SHAPESZ;a->index=340;a->w=24;a->h=28;a->anchor_x=a->anchor_y=0;a->valid=read_asset(a,8);
 if(a->valid){uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(size_t n=0;n<172032;n++){h^=a->rgba[n];h*=UINT64_C(0x100000001b3);}
 a->valid=h==UINT64_C(0x1b469b4a10a446c6);
 for(size_t n=3;n<172032;n+=4)if(a->rgba[n]!=255)a->valid=false;}}
 return a->valid;
}
