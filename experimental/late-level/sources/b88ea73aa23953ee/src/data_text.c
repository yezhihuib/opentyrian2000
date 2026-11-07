/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
/* Optional Data-only presentation. The native INDEX8 English loader is untouched. */
#include "data_text.h"
#include "hd_cursor.h"
#include "file.h"
#include "palette.h"
#include "video.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#ifdef _MSC_VER
#include <io.h>
#else
#include <fcntl.h>
#include <unistd.h>
#endif

#define MAX_ENTRIES 149u
#define MAX_GLYPHS 4335u
#define MAX_LINES 512u
#define BODY_WIDTH 1051u /* 584 output pixels at a 20px font from the 36px atlas. */
#define PAGE_LINES 16u /* Initial 1280x800 layout; the actual viewport updates this. */
struct SourcePin { unsigned episode, bytes; uint64_t fnv; };
struct EntryPin { unsigned episode, occurrence, start, end; uint64_t fnv; bool empty_body; };
#include "data_text_pins.inc"
#include "data_exit_pins.inc"
struct Entry { unsigned episode, occurrence; const char *title, *header, *body; uint64_t source; };
struct Glyph { uint32_t cp; unsigned advance; };
struct Line { const char *start, *end; bool emphasis; unsigned width; };
static struct Entry entries[MAX_ENTRIES];
static struct Glyph glyphs[MAX_GLYPHS];
static struct Line lines[MAX_LINES];
static unsigned entry_count, glyph_count, line_count, font_width, font_height, font_columns;
static unsigned episode, occurrences[4], selected_slot, slots, menu, scroll_offsets[4];
static unsigned layout_episode, layout_occurrence, layout_width;
static unsigned body_width=BODY_WIDTH, page_lines=PAGE_LINES;
static int body_height=428, body_leading=26, body_cell=27;
static const char *scroll_anchors[4];
static bool chinese, attempted, resources_ok, source_ok, active, layout_ok;
static char directory[1024] = "assets/data-text-zh-CN-v1";
static unsigned char *text_bytes, *font_bytes, *exit_bytes;
static bool exit_attempted;
static SDL_Texture *exit_texture;
static SDL_Renderer *exit_renderer;
static const unsigned char *font_alpha;
static SDL_Texture *font_texture;
static SDL_Renderer *texture_renderer;
static SDL_Texture *cursor_texture;
static SDL_Renderer *cursor_renderer;
static uint32_t *cursor_rgba;
static SDL_Surface *active_screen;
static Uint32 last_scroll;
static int held_direction;
static bool held_clock;
static unsigned transition_depth;
struct CursorPixel { unsigned x, y, index; };
static struct CursorPixel cursor_pixels[24*28];
static unsigned cursor_count;
static bool cursor_recording, frame_cursor_owner;

static uint32_t u32(const unsigned char *p)
{ return (uint32_t)p[0] | (uint32_t)p[1]<<8 | (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24; }
static unsigned u16(const unsigned char *p)
{ return p[0] | (unsigned)p[1]<<8; }
static uint64_t u64(const unsigned char *p)
{ return (uint64_t)u32(p) | (uint64_t)u32(p+4)<<32; }
static uint64_t fnv(const unsigned char *p, size_t n)
{
    uint64_t h = UINT64_C(14695981039346656037);
    for (size_t i=0; i<n; ++i) h = (h ^ p[i]) * UINT64_C(1099511628211);
    return h;
}
/* Strict Unicode scalar decoder: rejects overlong, surrogate, truncated and >U+10FFFF. */
static bool decode(const char **cursor, const char *end, uint32_t *cp)
{
    const unsigned char *p=(const unsigned char *)*cursor;
    if ((const char *)p>=end) return false;
    unsigned n; uint32_t value;
    if (*p<0x80) { n=1; value=*p; }
    else if (*p>=0xc2 && *p<=0xdf) { n=2; value=*p & 31; }
    else if (*p>=0xe0 && *p<=0xef) { n=3; value=*p & 15; }
    else if (*p>=0xf0 && *p<=0xf4) { n=4; value=*p & 7; }
    else return false;
    if ((size_t)(end-(const char *)p)<n) return false;
    for (unsigned i=1; i<n; ++i) { if ((p[i]&0xc0)!=0x80) return false; value=(value<<6)|(p[i]&63); }
    if ((n==2 && value<0x80) || (n==3 && value<0x800) || (n==4 && value<0x10000) ||
        value>0x10ffff || (value>=0xd800 && value<=0xdfff) || value==0) return false;
    *cursor=(const char *)p+n; *cp=value; return true;
}
static int glyph_index(uint32_t cp)
{
    unsigned lo=0, hi=glyph_count;
    while (lo<hi) { unsigned m=lo+(hi-lo)/2; if (glyphs[m].cp<cp) lo=m+1; else hi=m; }
    return lo<glyph_count && glyphs[lo].cp==cp ? (int)lo : -1;
}
static bool valid_text(const char *p, size_t length, bool body)
{
    const char *end=p+length;
    while (p<end) {
        uint32_t cp;
        if (!decode(&p,end,&cp) || (cp<32 && !(body && cp=='\n')) ||
            (cp!='\n' && glyph_index(cp)<0)) return false;
    }
    return true;
}
static unsigned char *read_resource(const char *root, const char *name, size_t limit, size_t *bytes)
{
    char path[4096];
    if (!root || snprintf(path,sizeof(path),"%s/%s",root,name)>=(int)sizeof(path)) return NULL;
#ifdef _MSC_VER
    struct _stat before;
    if (_stat(path,&before) || !(before.st_mode & _S_IFREG)) return NULL;
    FILE *f=fopen(path,"rb");
#else
    /* Nonblocking open prevents optional FIFOs from waiting for a writer. */
    int fd=open(path,O_RDONLY|O_NONBLOCK);
    if (fd<0) return NULL;
    struct stat before;
    if (fstat(fd,&before) || !S_ISREG(before.st_mode)) { close(fd); return NULL; }
    FILE *f=fdopen(fd,"rb");
    if (!f) close(fd);
#endif
    if (!f) return NULL;
#ifdef _MSC_VER
    struct _stat info;
    if (_fstat(_fileno(f),&info) || !(info.st_mode & _S_IFREG)) { fclose(f); return NULL; }
#else
    struct stat info;
    if (fstat(fileno(f),&info) || !S_ISREG(info.st_mode)) { fclose(f); return NULL; }
#endif
    if (fseek(f,0,SEEK_END)) { fclose(f); return NULL; }
    long length=ftell(f);
    if (length<=0 || (unsigned long)length>limit || fseek(f,0,SEEK_SET)) { fclose(f); return NULL; }
    unsigned char *p=malloc((size_t)length);
    if (!p) { fclose(f); return NULL; }
    bool good=fread(p,1,(size_t)length,f)==(size_t)length && fgetc(f)==EOF && !ferror(f);
    fclose(f);
    if (!good) { free(p); return NULL; }
    *bytes=(size_t)length; return p;
}
static const struct EntryPin *entry_pin(unsigned ep, unsigned occurrence)
{
    for (size_t i=0; i<sizeof(entry_pins)/sizeof(*entry_pins); ++i)
        if (entry_pins[i].episode==ep && entry_pins[i].occurrence==occurrence) return &entry_pins[i];
    return NULL;
}
static bool parse_font(const unsigned char *p, size_t n)
{
    if (n<64 || memcmp(p,"DZF1",4) || u32(p+4)!=1 || u32(p+16)!=40 || u32(p+20)!=48 ||
        u32(p+32)!=36 || u32(p+36)!=36 || u32(p+40)!=8 || u64(p+56)!=0) return false;
    unsigned w=u32(p+8), h=u32(p+12), count=u32(p+24), columns=u32(p+28);
    if (w!=2048 || !h || h>4080 || !count || count>MAX_GLYPHS || columns!=51 ||
        h%48 || (count+columns-1)/columns>h/48 || u32(p+44)!=(uint32_t)w*h ||
        n!=64+(size_t)count*8+(size_t)w*h || fnv(p+64,n-64)!=u64(p+48)) return false;
    for (unsigned i=0; i<count; ++i) {
        const unsigned char *r=p+64+i*8;
        uint32_t cp=u32(r); unsigned advance=u16(r+4);
        if (cp<32 || cp>0x10ffff || (cp>=0xd800 && cp<=0xdfff) || (i && cp<=glyphs[i-1].cp) ||
            !advance || advance>40 || u16(r+6)) return false;
        glyphs[i].cp=cp; glyphs[i].advance=advance;
    }
    glyph_count=count; font_width=w; font_height=h; font_columns=columns;
    font_alpha=p+64+count*8;
    return true;
}
static bool parse_entries(const unsigned char *p, size_t n)
{
    if (n<24 || memcmp(p,"DZT1",4) || u32(p+4)!=1 || !u32(p+8) || u32(p+8)>MAX_ENTRIES ||
        u32(p+12)!=n-24 || fnv(p+24,n-24)!=u64(p+16)) return false;
    unsigned count=u32(p+8); size_t off=24;
    for (unsigned i=0; i<count; ++i) {
        if (n-off<24) return false;
        const unsigned char *r=p+off; unsigned ep=u16(r), occurrence=u16(r+2);
        unsigned a=u32(r+4), b=u32(r+8), c=u32(r+12);
        const struct EntryPin *pin=entry_pin(ep,occurrence);
        if (!pin || u64(r+16)!=pin->fnv || a>16384 || b>16384 || c>16384 ||
            (size_t)a+b+c+3>n-off-24 || (!pin->empty_body && (!a || !b || !c))) return false;
        for (unsigned j=0; j<i; ++j)
            if (entries[j].episode==ep && entries[j].occurrence==occurrence) return false;
        const char *title=(const char *)r+24, *header=title+a+1, *body=header+b+1;
        if (title[a] || header[b] || body[c] || !valid_text(title,a,false) || !valid_text(header,b,false) ||
            !valid_text(body,c,true)) return false;
        entries[i]=(struct Entry){ep,occurrence,title,header,body,pin->fnv};
        off+=24+(size_t)a+b+c+3;
    }
    if (off!=n) return false;
    entry_count=count; return true;
}
static void load_resources(void)
{
    if (attempted) return;
    attempted=true;
    size_t n=0;
    font_bytes=read_resource(directory,"data-text-zh-CN-v1.dzf",16u*1024u*1024u,&n);
    if (!font_bytes || n!=DATA_TEXT_FONT_BYTES || fnv(font_bytes,n)!=DATA_TEXT_FONT_FNV || !parse_font(font_bytes,n)) goto fail;
    text_bytes=read_resource(directory,"data-text-zh-CN-v1.dct",1024u*1024u,&n);
    if (!text_bytes || n!=DATA_TEXT_RESOURCE_BYTES || fnv(text_bytes,n)!=DATA_TEXT_RESOURCE_FNV || !parse_entries(text_bytes,n)) goto fail;
    resources_ok=true; return;
fail:
    free(font_bytes); free(text_bytes); font_bytes=text_bytes=NULL;
    font_alpha=NULL; glyph_count=entry_count=0;
}
void data_text_invalidate(void)
{
    if (exit_texture) SDL_DestroyTexture(exit_texture);
    exit_texture=NULL; exit_renderer=NULL;
    if (font_texture) SDL_DestroyTexture(font_texture);
    font_texture=NULL; texture_renderer=NULL;
    if (cursor_texture) SDL_DestroyTexture(cursor_texture);
    cursor_texture=NULL; cursor_renderer=NULL; free(cursor_rgba); cursor_rgba=NULL;
}
void data_text_set_directory(const char *root)
{
    data_text_invalidate(); free(font_bytes); free(text_bytes); free(exit_bytes); exit_bytes=NULL; exit_attempted=false; font_bytes=text_bytes=NULL;
    font_alpha=NULL; attempted=resources_ok=layout_ok=false; glyph_count=entry_count=line_count=0;
    memset(scroll_offsets,0,sizeof(scroll_offsets)); memset(scroll_anchors,0,sizeof(scroll_anchors));
    if (root && strlen(root)<sizeof(directory)) strcpy(directory,root);
}
void data_text_set_language(const char *language)
{ chinese=language && !strcmp(language,"zh-CN"); }
const char *data_text_language(void) { return chinese ? "zh-CN" : "en"; }
void data_text_toggle(void) { chinese=!chinese; held_direction=0; held_clock=false; }
void data_text_episode(unsigned ep, const char *root)
{
    episode=ep; source_ok=false; layout_ok=false; layout_episode=layout_occurrence=0;
    memset(occurrences,0,sizeof(occurrences)); memset(scroll_offsets,0,sizeof(scroll_offsets));
    memset(scroll_anchors,0,sizeof(scroll_anchors));
    const struct SourcePin *pin=NULL;
    for (size_t i=0; i<sizeof(source_pins)/sizeof(*source_pins); ++i)
        if (source_pins[i].episode==ep) pin=&source_pins[i];
    if (!pin) return;
    char filename[32]; snprintf(filename,sizeof(filename),"cubetxt%u.dat",ep);
    size_t n=0; unsigned char *p=read_resource(root,filename,128u*1024u,&n);
    if (!p) return;
    bool good=n==pin->bytes && fnv(p,n)==pin->fnv;
    for (size_t i=0; good && i<sizeof(entry_pins)/sizeof(*entry_pins); ++i) {
        const struct EntryPin *e=&entry_pins[i];
        if (e->episode==ep && (e->start>e->end || e->end>n || fnv(p+e->start,e->end-e->start)!=e->fnv)) good=false;
    }
    free(p); source_ok=good;
}
void data_text_bind(unsigned slot, unsigned occurrence)
{
    if (slot<4) { if (occurrences[slot]!=occurrence) { scroll_offsets[slot]=0; scroll_anchors[slot]=NULL; } occurrences[slot]=occurrence; }
}
static const struct Entry *slot_entry(unsigned slot)
{
    if (!resources_ok || !source_ok || slot>=slots || slot>=4) return NULL;
    for (unsigned i=0; i<entry_count; ++i)
        if (entries[i].episode==episode && entries[i].occurrence==occurrences[slot] &&
            *entries[i].title && *entries[i].header) return &entries[i];
    return NULL;
}
static bool closing(uint32_t cp)
{ return cp==0x3001 || cp==0x3002 || cp==0xff0c || cp==0xff01 || cp==0xff1f || cp==0xff1a || cp==0xff1b || cp==0x201d || cp==0x2019 || cp==0x300b || cp==0x3009 || cp==0xff09 || cp==')' || cp==']' || cp==',' || cp=='.' || cp=='!' || cp=='?' || cp==':' || cp==';'; }
static bool opening(uint32_t cp)
{ return cp==0x201c || cp==0x2018 || cp==0x300a || cp==0x3008 || cp==0xff08 || cp=='(' || cp=='['; }
/* Complete scalar boundaries, paragraph gaps, Latin word boundaries and CJK punctuation. */
static bool wrap(const char *text, unsigned width, struct Line *out, unsigned capacity, unsigned *count)
{
    const char *p=text, *end=text+strlen(text); unsigned used=0; bool emphasis=false;
    while (p<end) {
        if (used==capacity) return false;
        if (*p=='\n') { ++p; out[used++]=(struct Line){p,p,emphasis,0}; continue; }
        const char *start=p, *q=p, *last_break=NULL, *previous=NULL;
        unsigned pixels=0, break_pixels=0; bool line_emphasis=emphasis;
        uint32_t previous_cp=0;
        while (q<end && *q!='\n') {
            const char *before=q; uint32_t cp;
            if (!decode(&q,end,&cp)) return false;
            int index=glyph_index(cp); if (index<0) return false;
            unsigned advance=cp=='~' ? 0 : glyphs[index].advance;
            if (pixels+advance>width && before>start) {
                const char *stop=before; unsigned stop_pixels=pixels;
                if (last_break && last_break>start && cp<128 && previous_cp<128) { stop=last_break; stop_pixels=break_pixels; }
                else if ((closing(cp) || opening(previous_cp)) && previous && previous>start) stop=previous;
                q=stop; pixels=stop_pixels; break;
            }
            if (cp==' ' || (cp>=0x2e80 && !opening(cp))) { last_break=q; break_pixels=pixels+advance; }
            previous=before; previous_cp=cp; pixels+=advance;
        }
        if (q==start) return false;
        const char *finish=q;
        for (const char *s=start; s<finish; ++s) if (*s=='~') emphasis=!emphasis;
        out[used++]=(struct Line){start,finish,line_emphasis,pixels};
        p=q;
        if (p<end && *p=='\n') ++p;
        else while (p<end && *p==' ') ++p;
    }
    *count=used; return used>0;
}
/* Preserve every paragraph gap, but spend only half a row on each blank line. */
static int line_advance(unsigned at)
{ return lines[at].start==lines[at].end ? body_leading/2 : body_leading; }
static int line_extent(unsigned at)
{ return lines[at].start==lines[at].end ? line_advance(at) : body_cell; }
static unsigned visible_lines(unsigned start)
{
    unsigned at=start; int y=0;
    while (at<line_count && y+line_extent(at)<=body_height) { y+=line_advance(at); ++at; }
    return at>start ? at-start : 1;
}
static unsigned page_start_before(unsigned end)
{
    if (!end) return 0;
    unsigned start=end-1; int height=line_extent(start);
    while (start && height+line_advance(start-1)<=body_height) height+=line_advance(--start);
    return start;
}
static unsigned max_scroll(void) { return page_start_before(line_count); }
static void remember_scroll(void)
{
    if (selected_slot<4 && layout_ok && scroll_offsets[selected_slot]<line_count)
        scroll_anchors[selected_slot]=lines[scroll_offsets[selected_slot]].start;
}
static void layout_entry(const struct Entry *entry)
{
    if (!entry) { layout_ok=false; line_count=0; return; }
    if (!layout_ok || layout_episode!=episode || layout_occurrence!=entry->occurrence || layout_width!=body_width) {
        const char *anchor=scroll_anchors[selected_slot];
        layout_ok=wrap(entry->body,body_width,lines,MAX_LINES,&line_count);
        layout_episode=episode; layout_occurrence=entry->occurrence; layout_width=body_width;
        /* Keep the same passage at the top when a resize changes the wrapping. */
        if (layout_ok && anchor) {
            unsigned at=0;
            while (at+1<line_count && lines[at+1].start<=anchor) ++at;
            scroll_offsets[selected_slot]=at;
        }
    }
    if (selected_slot<4 && scroll_offsets[selected_slot]>max_scroll()) scroll_offsets[selected_slot]=max_scroll();
    remember_scroll();
}
void data_text_begin(unsigned current_menu, unsigned selected, unsigned count, SDL_Surface *screen)
{
    active=current_menu==7 || current_menu==8;
    if (!active) { active_screen=NULL; return; }
    menu=current_menu; selected_slot=selected; slots=count>4 ? 4 : count; active_screen=screen;
    load_resources();
    const struct Entry *entry=slot_entry(selected_slot);
    layout_entry(entry);
}
void data_text_end(void) { active=false; active_screen=NULL; held_direction=0; held_clock=false; data_text_cursor_clear(); }
void data_text_transition(bool begin)
{ if (begin) ++transition_depth; else if (transition_depth) --transition_depth; }
bool data_text_body_active(void)
{ return active && menu==8 && chinese && layout_ok && slot_entry(selected_slot)!=NULL; }
void data_text_scroll(int amount)
{
    if (!data_text_body_active()) return;
    int64_t next=(int64_t)scroll_offsets[selected_slot]+amount;
    if (next<0) next=0;
    if ((uint64_t)next>max_scroll()) next=max_scroll();
    scroll_offsets[selected_slot]=(unsigned)next; remember_scroll();
}
static unsigned page_step(int direction)
{
    if (!data_text_body_active()) return page_lines;
    unsigned offset=scroll_offsets[selected_slot];
    return direction<0 ? offset-page_start_before(offset) : visible_lines(offset);
}
void data_text_scroll_held(int direction, bool page)
{
    Uint32 now=SDL_GetTicks();
    if (!direction) { held_direction=0; held_clock=false; return; }
    direction=direction<0 ? -1 : 1;
    if (direction!=held_direction || !held_clock || now-last_scroll>=80) {
        data_text_scroll(direction*(page ? (int)page_step(direction) : 1));
        last_scroll=now; held_clock=true; held_direction=direction;
    }
}
void data_text_page(int direction)
{ data_text_scroll(direction<0 ? -(int)page_step(-1) : (int)page_step(1)); }
void data_text_mouse_scroll(int direction)
{
    direction=direction<0 ? -1 : 1;
    data_text_scroll(direction);
    last_scroll=SDL_GetTicks(); held_clock=true; held_direction=direction;
}

void data_text_home(bool end)
{ if (data_text_body_active()) { scroll_offsets[selected_slot]=end ? max_scroll() : 0; remember_scroll(); } }
void data_text_wheel(int amount) { data_text_scroll(amount); }
static bool prepare_texture(SDL_Renderer *renderer)
{
    if (font_texture && renderer==texture_renderer) return true;
    if (!resources_ok) return false;
    data_text_invalidate();
    /* The only full-color temporary is one bounded 2048×4080 font atlas. */
    uint32_t *pixels=malloc((size_t)font_width*font_height*sizeof(*pixels));
    if (!pixels) return false;
    for (size_t i=0; i<(size_t)font_width*font_height; ++i) pixels[i]=((uint32_t)font_alpha[i]<<24)|0x00ffffff;
    font_texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STATIC,(int)font_width,(int)font_height);
    bool good=font_texture && !SDL_UpdateTexture(font_texture,NULL,pixels,(int)font_width*4);
    free(pixels);
    if (!good) { data_text_invalidate(); return false; }
    SDL_SetTextureBlendMode(font_texture,SDL_BLENDMODE_BLEND);
#if SDL_VERSION_ATLEAST(2,0,12)
    SDL_SetTextureScaleMode(font_texture,SDL_ScaleModeLinear);
#endif
    texture_renderer=renderer; return true;
}
static SDL_Rect mapped(const SDL_Rect *dst, int x, int y, int w, int h)
{
    SDL_Rect r={dst->x+x*dst->w/1280,dst->y+y*dst->h/800,0,0};
    r.w=dst->x+(x+w)*dst->w/1280-r.x; r.h=dst->y+(y+h)*dst->h/800-r.y;
    return r;
}
/* One bounded whole-run font asset, sharing the accepted shop's alpha/role
 * treatment. Optional failure leaves the original indexed gold lettering. */
static bool prepare_exit(SDL_Renderer *renderer)
{
    if (!exit_attempted) {
        exit_attempted=true; size_t n=0;
        exit_bytes=read_resource(directory,"data-exit-v1.hda",DATA_EXIT_BYTES,&n);
        if (exit_bytes && (n!=DATA_EXIT_BYTES || fnv(exit_bytes,n)!=DATA_EXIT_FNV)) { free(exit_bytes); exit_bytes=NULL; }
    }
    if (!exit_bytes) return false;
    if (exit_texture && exit_renderer==renderer) return true;
    if (exit_texture) SDL_DestroyTexture(exit_texture);
    exit_texture=NULL; exit_renderer=NULL;
    const unsigned char *alpha=exit_bytes+64,*roles=alpha+DATA_EXIT_WIDTH*DATA_EXIT_HEIGHT;
    uint32_t pixels[DATA_EXIT_WIDTH*DATA_EXIT_HEIGHT*5];
    for (unsigned layer=0; layer<5; ++layer) for (unsigned p=0; p<DATA_EXIT_WIDTH*DATA_EXIT_HEIGHT; ++p)
        pixels[layer*DATA_EXIT_WIDTH*DATA_EXIT_HEIGHT+p]=((uint32_t)(!layer || roles[p]==layer+11 ? alpha[p] : 0)<<24)|0x00ffffff;
    exit_texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STATIC,DATA_EXIT_WIDTH,DATA_EXIT_HEIGHT*5);
    if (!exit_texture || SDL_UpdateTexture(exit_texture,NULL,pixels,DATA_EXIT_WIDTH*4) || SDL_SetTextureBlendMode(exit_texture,SDL_BLENDMODE_BLEND)) {
        if (exit_texture) SDL_DestroyTexture(exit_texture); exit_texture=NULL; return false;
    }
#if SDL_VERSION_ATLEAST(2,0,12)
    SDL_SetTextureScaleMode(exit_texture,SDL_ScaleModeLinear);
#endif
    exit_renderer=renderer; return true;
}
static SDL_Color exit_color(unsigned index)
{
    SDL_Color color={0,0,0,255};
    SDL_GetRGB(rgb_palette[index],main_window_tex_format,&color.r,&color.g,&color.b);
    return color;
}
static void draw_exit(SDL_Renderer *r,const SDL_Rect *dst,int x,int y,bool selected)
{
    if (!prepare_exit(r)) return;
    /* PIC1's recessed Data field is palette index 228. Restore that same field
     * under the native lettering, without introducing a separate button. */
    SDL_Rect background=mapped(dst,menu==7 ? 680 : 1032,y-8,menu==7 ? 564 : 212,64);
    SDL_Color bg=exit_color(228); SDL_SetRenderDrawColor(r,bg.r,bg.g,bg.b,255); SDL_RenderFillRect(r,&background);
    for (unsigned layer=0; layer<5; ++layer) {
        SDL_Rect src={0,(int)(layer*DATA_EXIT_HEIGHT),DATA_EXIT_WIDTH,DATA_EXIT_HEIGHT};
        SDL_Rect target=mapped(dst,x-1+(layer ? 0 : 8),y-1+(layer ? 0 : 8),DATA_EXIT_WIDTH,DATA_EXIT_HEIGHT);
        unsigned index=layer ? 240+layer+11+(selected ? -1 : -3) : 224;
        SDL_Color color=exit_color(index); SDL_SetTextureColorMod(exit_texture,color.r,color.g,color.b);
        SDL_RenderCopy(r,exit_texture,&src,&target);
    }
}
static void panel(SDL_Renderer *r, const SDL_Rect *dst, int x, int y, int w, int h)
{
    SDL_Rect rect=mapped(dst,x,y,w,h);
    SDL_SetRenderDrawColor(r,18,24,39,255); SDL_RenderFillRect(r,&rect);
}
static void draw_line(SDL_Renderer *r, const SDL_Rect *dst, const struct Line *line, int x, int y, int scale, bool bright)
{
    const char *p=line->start; bool emphasis=line->emphasis;
    while (p<line->end) {
        uint32_t cp; if (!decode(&p,line->end,&cp)) break;
        if (cp=='~') { emphasis=!emphasis; continue; }
        int index=glyph_index(cp); if (index<0) break;
        SDL_Rect src={index%(int)font_columns*40,index/(int)font_columns*48,40,48};
        SDL_Rect target=mapped(dst,x-2*scale/100,y,40*scale/100,48*scale/100);
        SDL_SetTextureColorMod(font_texture,emphasis ? 255 : bright ? 240 : 192,emphasis ? 216 : bright ? 240 : 204,emphasis ? 132 : 228);
        SDL_RenderCopy(r,font_texture,&src,&target);
        x+=(int)glyphs[index].advance*scale/100;
    }
}
static void draw_string(SDL_Renderer *r, const SDL_Rect *dst, const char *text, int x, int y, int scale)
{
    struct Line line={text,text+strlen(text),false,0}; draw_line(r,dst,&line,x,y,scale,true);
}
/* Native output pixels keep the 1280-wide reader compact without turning a
 * 640-wide window into tiny text. The 36px atlas is only downsampled. */
struct ReadingMetrics { SDL_Rect clip; int font, leading; unsigned width, rows; };
static struct ReadingMetrics reading_metrics(const SDL_Rect *dst)
{
    struct ReadingMetrics m;
    m.clip=mapped(dst,648,196,584,428);
    m.font=(dst->w*20+640)/1280;
    if (m.font<16) m.font=16;
    if (m.font>36) m.font=36;
    m.leading=m.font+6;
    int cell=(48*m.font+35)/36;
    m.rows=m.clip.h>=cell ? 1u+(unsigned)(m.clip.h-cell)/(unsigned)m.leading : 1u;
    m.width=m.clip.w>0 ? (unsigned)m.clip.w*36u/(unsigned)m.font : 1u;
    if (!m.width) m.width=1;
    return m;
}
static void draw_body_line(SDL_Renderer *r, const struct Line *line, int x, int y, int font)
{
    const char *p=line->start; bool emphasis=line->emphasis; unsigned pen=0;
    while (p<line->end) {
        uint32_t cp; if (!decode(&p,line->end,&cp)) break;
        if (cp=='~') { emphasis=!emphasis; continue; }
        int index=glyph_index(cp); if (index<0) break;
        SDL_Rect src={index%(int)font_columns*40,index/(int)font_columns*48,40,48};
        int left=((int)pen-2)*font/36;
        SDL_Rect target={x+left,y,((int)pen+38)*font/36-left,48*font/36};
        SDL_SetTextureColorMod(font_texture,emphasis ? 255 : 240,emphasis ? 216 : 240,emphasis ? 132 : 228);
        SDL_RenderCopy(r,font_texture,&src,&target);
        pen+=glyphs[index].advance;
    }
}
static bool prepare_cursor(SDL_Renderer *renderer);
void data_text_present(SDL_Renderer *r, SDL_Surface *screen, const SDL_Rect *dst)
{
    if (!active || transition_depth || active_screen!=screen || !prepare_texture(r) || (cursor_count && !prepare_cursor(r))) return;
    SDL_BlendMode old_mode; Uint8 cr,cg,cb,ca; SDL_Rect old_clip;
    bool clipped=SDL_RenderIsClipEnabled(r)==SDL_TRUE;
    SDL_RenderGetClipRect(r,&old_clip); SDL_GetRenderDrawBlendMode(r,&old_mode); SDL_GetRenderDrawColor(r,&cr,&cg,&cb,&ca);
    SDL_SetRenderDrawBlendMode(r,SDL_BLENDMODE_NONE);
    SDL_RenderSetClipRect(r,dst);
    if (chinese) {
        struct ReadingMetrics metrics=reading_metrics(dst);
        body_width=metrics.width; page_lines=metrics.rows;
        body_height=metrics.clip.h; body_leading=metrics.leading; body_cell=(48*metrics.font+35)/36;
        layout_entry(slot_entry(selected_slot));
        if (menu==7) {
            for (unsigned slot=0; slot<slots; ++slot) {
                const struct Entry *entry=slot_entry(slot); if (!entry) continue;
                struct Line title_lines[16]; unsigned count=0; int scale=78;
                while (scale>=40) {
                    if (wrap(entry->title,472u*100u/(unsigned)scale,title_lines,16,&count) && count*(unsigned)(44*scale/100)<=104) break;
                    scale-=2;
                }
                if (scale<40) continue;
                panel(r,dst,764,168+(int)slot*112,480,108);
                for (unsigned i=0; i<count; ++i) draw_line(r,dst,&title_lines[i],772,168+(int)slot*112+(int)i*44*scale/100,scale,slot==selected_slot);
            }
        }
        const struct Entry *entry=slot_entry(selected_slot);
        if (entry) {
            panel(r,dst,8,680,576,56);
            draw_string(r,dst,entry->header,32,684,85);
            if (menu==8) {
                panel(r,dst,632,36,620,100);
                int header_scale=dst->w>0 && 64000/dst->w>68 ? 64000/dst->w : 68;
                draw_string(r,dst,entry->header,648,48,header_scale);
            }
            if (data_text_body_active()) {
                panel(r,dst,640,192,604,432);
                SDL_RenderSetClipRect(r,&metrics.clip);
                unsigned offset=scroll_offsets[selected_slot];
                int y=metrics.clip.y;
                unsigned visible=visible_lines(offset);
                for (unsigned i=0; i<visible && offset+i<line_count; ++i) {
                    draw_body_line(r,&lines[offset+i],metrics.clip.x,y,metrics.font);
                    y+=line_advance(offset+i);
                }
                SDL_RenderSetClipRect(r,dst);
                panel(r,dst,640,632,384,44);
                char progress[64]; snprintf(progress,sizeof(progress),"Read %u%%  %u/%u",max_scroll() ? offset*100/max_scroll() : 100,offset+1,line_count);
                draw_string(r,dst,progress,648,636,65);
            }
        }
    }
    /* Native hit regions, anchors and list selection brightness are unchanged. */
    if (menu==7) draw_exit(r,dst,688,slots ? 176+(int)slots*112 : 640,selected_slot==slots);
    else draw_exit(r,dst,1040,640,false);
    /* Discoverability stays local to Data; a failed resource never hides native text. */
    panel(r,dst,8,744,1240,48);
    if (chinese && slot_entry(selected_slot)) draw_string(r,dst,"F6: \xe7\xae\x80\xe4\xbd\x93\xe4\xb8\xad\xe6\x96\x87 / English   Up/Down  PgUp/PgDn  Home/End",16,744,65);
    else if (chinese) draw_string(r,dst,"F6: Chinese / English   English fallback",16,744,65);
    else draw_string(r,dst,"F6: English / \xe7\xae\x80\xe4\xbd\x93\xe4\xb8\xad\xe6\x96\x87",16,744,70);
    SDL_RenderSetClipRect(r,clipped ? &old_clip : NULL);
    SDL_SetRenderDrawBlendMode(r,old_mode); SDL_SetRenderDrawColor(r,cr,cg,cb,ca);
}

/* Replay only opaque native cursor writes, including writes equal to the underlay.
 * This keeps mouse feedback above the Data frame and Chinese panels without
 * depending on successful loading of the optional Chinese font. */
void data_text_cursor_frame_owner(bool owner) { frame_cursor_owner=owner; }
void data_text_cursor_begin(SDL_Surface *screen)
{
    cursor_count=0;
    cursor_recording=active && (resources_ok || frame_cursor_owner) && screen==active_screen;
}
void data_text_cursor_pixel(SDL_Surface *screen, const Uint8 *pixel)
{
    if (!cursor_recording || screen!=active_screen || cursor_count>=24*28 || !screen->pixels) return;
    uintptr_t base=(uintptr_t)screen->pixels, address=(uintptr_t)pixel;
    if (address<base || address-base>=(size_t)screen->pitch*screen->h) return;
    size_t offset=address-base;
    unsigned x=(unsigned)(offset%(unsigned)screen->pitch), y=(unsigned)(offset/(unsigned)screen->pitch);
    if (x>=(unsigned)screen->w) return;
    cursor_pixels[cursor_count++]=(struct CursorPixel){x,y,*pixel};
}
void data_text_cursor_done(void) { cursor_recording=false; }
void data_text_cursor_clear(void) { cursor_recording=false; cursor_count=0; }
/* A full canonical sparse cursor plane uses the same nearest SDL sampler as
 * the native base. Floor rectangles (or idealized half-pixel formulas) disagree
 * with SDL at fractional sizes and exact floating-point ties. */
static bool prepare_cursor(SDL_Renderer *renderer)
{
    if (cursor_texture && cursor_renderer==renderer) return true;
    if (cursor_texture) SDL_DestroyTexture(cursor_texture);
    cursor_texture=NULL; cursor_renderer=NULL;
    if (!cursor_rgba) cursor_rgba=malloc(1280u*800u*4u);
    if (!cursor_rgba) return false;
    cursor_texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,1280,800);
    if (!cursor_texture) return false;
    if (SDL_SetTextureBlendMode(cursor_texture,SDL_BLENDMODE_BLEND)) goto fail;
#if SDL_VERSION_ATLEAST(2,0,12)
    if (SDL_SetTextureScaleMode(cursor_texture,SDL_ScaleModeNearest)) goto fail;
#endif
    cursor_renderer=renderer; return true;
fail:
    SDL_DestroyTexture(cursor_texture);cursor_texture=NULL;return false;
}
void data_text_cursor_present(SDL_Renderer *renderer, SDL_Surface *screen, const SDL_Rect *output, const Uint32 *rgb, const SDL_PixelFormat *format)
{
    if (hd_cursor_active() || !active || (!resources_ok && !frame_cursor_owner) || transition_depth || active_screen!=screen || !cursor_count || !rgb || !format || !prepare_cursor(renderer)) return;
    memset(cursor_rgba,0,1280u*800u*4u);
    for (unsigned i=0;i<cursor_count;++i) {
        const struct CursorPixel *pixel=&cursor_pixels[i]; Uint8 r,g,b;
        if (pixel->x>=320 || pixel->y>=200) continue;
        SDL_GetRGB(rgb[pixel->index],format,&r,&g,&b);
        uint32_t color=UINT32_C(0xff000000)|(uint32_t)r<<16|(uint32_t)g<<8|b;
        for (unsigned y=0;y<4;++y) for (unsigned x=0;x<4;++x)
            cursor_rgba[(pixel->y*4+y)*1280+pixel->x*4+x]=color;
    }
    if (SDL_UpdateTexture(cursor_texture,NULL,cursor_rgba,1280*4)) return;
    SDL_Rect old_clip; bool clipped=SDL_RenderIsClipEnabled(renderer)==SDL_TRUE;
    SDL_RenderGetClipRect(renderer,&old_clip);SDL_RenderSetClipRect(renderer,output);
    SDL_RenderCopy(renderer,cursor_texture,NULL,output);
    SDL_RenderSetClipRect(renderer,clipped ? &old_clip : NULL);
}
