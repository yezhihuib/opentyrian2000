/* Only unrelated lookup/eligibility is stubbed. Canvas writer bodies are real. */
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
enum { ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106 };
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[65536];
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef int G101Record;typedef int PCapRecord;typedef int Forest13Record;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
static Sprite2_array spriteSheet8,explosionSpriteSheet;
static bool game_probe_local_blend=true,game_probe_known_blend=true,forest_registry_ok=true;
static unsigned game_probe_scene_assets=2,blend_source_index;
static struct {const Uint8 *data;unsigned id;} terrain_sources[185];
static unsigned terrain_source_count,textErase;
static SDL_Rect last_restore;
static void game_probe_restore_region(unsigned index,SDL_Rect requested,SDL_Rect actual,unsigned groups,unsigned blocks){last_restore=actual;}
static void game_probe_blend_write(bool known,unsigned index,int ox,int oy,int x,int y,Uint8 before,Uint8 source,Uint8 after,unsigned sub,unsigned blocks,bool rgba){}
static void game_probe_scene_draw(int bank,unsigned id,int x,int y,int part,int style,bool mirrored){}
static void ground101_note_draw(const G101Record *r,bool enemy){}
static void ground101_select(const G101Record *r,const Uint8 *p,unsigned i,int x,int y,Uint8 out[4]){memcpy(out,p,4);}
static void plateau_cap_select(const PCapRecord *r,const Uint8 *p,unsigned i,int x,int y,Uint8 out[4]){memcpy(out,p,4);}
static void forest13_select(const Forest13Record *r,const Uint8 *p,unsigned i,int x,int y,Uint8 out[4]){memcpy(out,p,4);}
static const G101Record *ground101_record(unsigned bank,unsigned id){return NULL;}
static const PCapRecord *plateau_cap_record(unsigned id){return NULL;}
static const Forest13Record *forest13_record(unsigned id){return NULL;}
static bool forest13_declared(void){return false;}
static int ground101_layer1_row(Uint8 **map,int x,int y){return 1;}
static Asset *scene_asset(int slot,int role,int index,int ax,int ay){return NULL;}
static bool effect_ramp_monotone(unsigned hue){return true;}
static bool effect_ramp_monotone_to(unsigned hue,unsigned top){return true;}
static bool recognized_value_effect(unsigned index){return false;}
static bool recognized_contact_effect(unsigned index,unsigned hue){return false;}
static Sprite *sprite(unsigned table,unsigned id){return &sprite_table[table].sprite[id];}
static bool sprite_exists(unsigned table,unsigned id){return table<8&&id<sprite_table[table].count&&sprite_table[table].sprite[id].data;}
static void JE_outTextAndDarken(SDL_Surface *s,int x,int y,const char *text,unsigned hue,int value,unsigned font){assert(false);}
static void JE_outTextModify(SDL_Surface *s,int x,int y,const char *text,unsigned hue,int value,unsigned font){assert(false);}
#define PART_SHADE 0
#define FULL_SHADE 1
#define DARKEN 2
#define TRICK 3
