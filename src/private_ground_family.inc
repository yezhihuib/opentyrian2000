/* Private finite ground family. RGBA payload, exact source pins, full family fallback.
 * No collision/index-plane or map edits. Deliberately not a published contract. */
static const unsigned private_ground_ids[10]={372,380,390,367,368,376,378,386,387,388};
static const uint64_t private_ground_source[10]={UINT64_C(0xe5ab487b1d777c88),UINT64_C(0xeaf92ca7e66b6029),UINT64_C(0x18e7b1576b2c866f),UINT64_C(0xb5c43e4d37eef3c1),UINT64_C(0xfbf4027a212bc257),UINT64_C(0xf164c0ad2583443f),UINT64_C(0x526beca231fd766a),UINT64_C(0x59cae4c3dc8ff0ee),UINT64_C(0x8bdf81b6fdfa4f28),UINT64_C(0x812a9162941357b3)};
static const uint64_t private_ground_payload[10]={UINT64_C(0x979842c7fb07f657),UINT64_C(0x1319d37af0fcbb79),UINT64_C(0x5c79d31ca0640d11),UINT64_C(0x7f6d7c512bff04e6),UINT64_C(0xcae428fe01fd2a26),UINT64_C(0xcd88af59096f5597),UINT64_C(0xae8597271faf9c31),UINT64_C(0x360f6c61766416ad),UINT64_C(0x300e49764e3a21c7),UINT64_C(0x49817f3e5b941434)};
static int private_ground_member(unsigned id)
{for(int i=0;i<10;i++)if(id==private_ground_ids[i])return i;return -1;}
static bool private_ground_ready(void)
{
 if(private_ground_source_fault||game_probe_density!=8||game_probe_missing||game_probe_invalid||game_probe_original_reference||!game_probe_assets)return false;
 bool ready=true;
 for(int i=0;i<10;i++) {
  Asset*a=&assets[576+i];
  if(!a->initialized) {
   a->initialized=true;a->bank=ASSET_SHAPESZ;a->index=(int)private_ground_ids[i];a->w=24;a->h=28;a->anchor_x=a->anchor_y=0;
   a->valid=read_asset(a,8);
   if(a->valid) {
    uint64_t h=UINT64_C(0xcbf29ce484222325);
    for(size_t n=0;n<24*28*8*8*4;n++){h^=a->rgba[n];h*=UINT64_C(0x100000001b3);}
    a->valid=h==private_ground_payload[i];
    for(size_t n=3;n<24*28*8*8*4;n+=4)if(a->rgba[n]!=255)a->valid=false;
   }
  }
  if(!a->valid)ready=false;
 }
 return ready;
}
static bool private_ground_source_matches(unsigned id,const Uint8*data)
{
 int i=private_ground_member(id);if(i<0||!data)return false;
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 for(size_t n=0;n<24*28;n++){h^=data[n];h*=UINT64_C(0x100000001b3);}
 return h==private_ground_source[i];
}
