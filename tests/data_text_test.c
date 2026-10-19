/* SPDX-License-Identifier: GPL-2.0-or-later */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <limits.h>
#include <sys/stat.h>
#include "../src/data_text.c"
Palette palette;
Uint32 rgb_palette[256];
SDL_PixelFormat *main_window_tex_format;
FILE *dir_fopen(const char *dir,const char *name,const char *mode)
{
    char path[4096];
    if (snprintf(path,sizeof(path),"%s/%s",dir,name)>=(int)sizeof(path)) return NULL;
    return fopen(path,mode);
}
static void put32(unsigned char *p,uint32_t v)
{ for (unsigned i=0;i<4;++i) p[i]=(unsigned char)(v>>(8*i)); }
static void put64(unsigned char *p,uint64_t v)
{ put32(p,(uint32_t)v);put32(p+4,(uint32_t)(v>>32)); }
static unsigned meaningful(const char *p,const char *end)
{
    unsigned result=0;
    while (p<end) { uint32_t cp; assert(decode(&p,end,&cp)); if (cp!=' ' && cp!='\n' && cp!='~') ++result; }
    return result;
}
static void decoder_tests(void)
{
    static const unsigned char invalid[][6]={{0xc0,0x80},{0xc1,0xbf},{0xe0,0x80,0x80},{0xed,0xa0,0x80},{0xf0,0x80,0x80,0x80},{0xf4,0x90,0x80,0x80},{0xf5,0x80,0x80,0x80},{0x80},{0xe4,0xb8},{0xf0,0x90,0x80}};
    static const unsigned lens[]={2,2,3,3,4,4,4,1,2,3};
    for(unsigned i=0;i<sizeof(lens)/sizeof(*lens);++i) { const char *p=(const char *)invalid[i];uint32_t cp;assert(!decode(&p,p+lens[i],&cp)); }
    const char good[]="中文é😀"; const char *p=good;uint32_t cp;unsigned count=0;
    while(p<good+strlen(good)){assert(decode(&p,good+strlen(good),&cp));++count;}assert(count==4);
}
static void render(SDL_Renderer *renderer,SDL_Surface *target,SDL_Surface *screen,const char *output,const char *tag,int width,int height)
{
    SDL_Rect dst=height==720 ? (SDL_Rect){64,0,1152,720} : (SDL_Rect){0,0,width,height};
    SDL_SetRenderDrawColor(renderer,40,60,80,255);SDL_RenderClear(renderer);
    data_text_present(renderer,screen,&dst);
    assert(SDL_RenderReadPixels(renderer,NULL,target->format->format,target->pixels,target->pitch)==0);
    char file[4096];snprintf(file,sizeof(file),"%s/%s-%dx%d.bmp",output,tag,width,height);if (!getenv("DATA_TEXT_NO_CAPTURE")) assert(SDL_SaveBMP(target,file)==0);
}
static void cursor_sampler_tests(void)
{
    SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
    SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(screen&&target);
    SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);assert(r);
    Uint32 *baseline=malloc(1280u*800u*4),*pixels=malloc(1280u*800u*4);assert(baseline&&pixels);
    Uint32 rgb[256]={0};rgb[228]=SDL_MapRGB(target->format,255,239,127);
    active=true;active_screen=screen;chinese=false;resources_ok=false;data_text_cursor_frame_owner(true);
    data_text_cursor_begin(screen);
    const unsigned cells[][2]={{56,62},{57,62},{56,63},{200,80},{319,199},{0,0},{159,99}};
    for(unsigned i=0;i<sizeof(cells)/sizeof(*cells);++i){Uint8 *p=(Uint8 *)screen->pixels+cells[i][1]*screen->pitch+cells[i][0];*p=228;data_text_cursor_pixel(screen,p);}
    data_text_cursor_done();assert(cursor_count==sizeof(cells)/sizeof(*cells));
    const SDL_Rect outputs[]={{0,0,640,400},{0,0,1280,800},{64,0,1152,720},{17,23,1000,625},{11,13,853,533}};
    for(unsigned density=2;density<=4;density+=2)for(unsigned o=0;o<sizeof(outputs)/sizeof(*outputs);++o){
        unsigned w=320*density,h=200*density;
        for(unsigned y=0;y<h;++y)for(unsigned x=0;x<w;++x)pixels[y*w+x]=0xff000000;
        for(unsigned i=0;i<sizeof(cells)/sizeof(*cells);++i)for(unsigned y=0;y<density;++y)for(unsigned x=0;x<density;++x)pixels[(cells[i][1]*density+y)*w+cells[i][0]*density+x]=rgb[228];
        SDL_Texture *texture=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STATIC,(int)w,(int)h);assert(texture);
        assert(!SDL_UpdateTexture(texture,NULL,pixels,(int)w*4));assert(!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE));assert(!SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest));
        SDL_SetRenderDrawColor(r,0,0,0,255);assert(!SDL_RenderClear(r));assert(!SDL_RenderCopy(r,texture,NULL,&outputs[o]));assert(!SDL_RenderReadPixels(r,NULL,target->format->format,baseline,1280*4));
        SDL_SetRenderDrawColor(r,0,0,0,255);assert(!SDL_RenderClear(r));data_text_cursor_present(r,screen,&outputs[o],rgb,target->format);assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
        if(memcmp(baseline,target->pixels,1280u*800u*4)){for(unsigned yy=0;yy<800;++yy)for(unsigned xx=0;xx<1280;++xx){Uint32 actual;memcpy(&actual,(Uint8 *)target->pixels+yy*target->pitch+xx*4,4);if(actual!=baseline[yy*1280+xx]){fprintf(stderr,"cursor mismatch density%u output%u xy%u,%u native%08x replay%08x\n",density,o,xx,yy,baseline[yy*1280+xx],actual);abort();}}}SDL_DestroyTexture(texture);
    }
    data_text_cursor_clear();data_text_cursor_frame_owner(false);active=false;active_screen=NULL;
    data_text_invalidate();free(baseline);free(pixels);SDL_DestroyRenderer(r);SDL_FreeSurface(target);SDL_FreeSurface(screen);
    puts("Native cursor nearest-sampler replay exact at 5 viewports x 2 scaler densities, including fractional letterbox and missing Chinese font");
}
static uint64_t region_hash(SDL_Surface *s,SDL_Rect rect)
{
    uint64_t h=UINT64_C(14695981039346656037);
    for(int y=rect.y;y<rect.y+rect.h;++y)
        for(int x=rect.x;x<rect.x+rect.w;++x) {
            Uint32 pixel;memcpy(&pixel,(Uint8 *)s->pixels+y*s->pitch+x*4,4);
            for(unsigned i=0;i<4;++i)h=(h^((pixel>>(i*8))&255))*UINT64_C(1099511628211);
        }
    return h;
}
static void exit_label_tests(SDL_Surface *screen,const char *output)
{
    SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(target);
    SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);assert(r);SDL_Rect dst={0,0,1280,800};
    for(unsigned count=0;count<=4;++count) {
        SDL_Rect area={680,count ? 168+(int)count*112 : 632,564,64};
        uint64_t selected_hash=0;
        for(unsigned language=0;language<2;++language) {
            data_text_set_language(language ? "zh-CN" : "en");
            data_text_begin(7,count,count,screen);
            SDL_SetRenderDrawColor(r,40,60,80,255);assert(!SDL_RenderClear(r));data_text_present(r,screen,&dst);
            assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
            Uint32 bg;memcpy(&bg,(Uint8 *)target->pixels+area.y*target->pitch+area.x*4,4);
            Uint8 red,green,blue;SDL_GetRGB(bg,target->format,&red,&green,&blue);assert(red==palette[228].r&&green==palette[228].g&&blue==palette[228].b);
            unsigned ink=0,antialias=0,gold=0;
            for(int y=area.y;y<area.y+area.h;++y)for(int x=688;x<835;++x) {
                Uint32 pixel;memcpy(&pixel,(Uint8 *)target->pixels+y*target->pitch+x*4,4);
                SDL_GetRGB(pixel,target->format,&red,&green,&blue);
                if(red>100)++ink;if(red>70&&red<190)++antialias;
                if(red>100&&red>green&&green>blue)++gold;
            }
            assert(ink>1500&&antialias>100&&gold>1500);
            uint64_t h=region_hash(target,area);
            if(language)assert(h==selected_hash);else selected_hash=h;
            if(count) {
                data_text_begin(7,0,count,screen);data_text_present(r,screen,&dst);
                assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
                assert(region_hash(target,area)!=selected_hash);
            }
        }
    }
    data_text_begin(8,0,4,screen);data_text_present(r,screen,&dst);
    assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
    SDL_Rect area={1032,632,212,64};uint64_t chinese_exit=region_hash(target,area);
    data_text_toggle();data_text_present(r,screen,&dst);
    assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
    assert(chinese_exit==region_hash(target,area));
    data_text_transition(true);SDL_SetRenderDrawColor(r,40,60,80,255);assert(!SDL_RenderClear(r));
    assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));uint64_t paused=region_hash(target,area);
    data_text_present(r,screen,&dst);assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
    assert(paused==region_hash(target,area));data_text_transition(false);
    for(unsigned language=0;language<2;++language) {
        data_text_set_language(language ? "zh-CN" : "en");data_text_present(r,screen,&dst);
        data_text_cursor_begin(screen);const Uint8 *at=(const Uint8 *)screen->pixels+160*screen->pitch+260;
        data_text_cursor_pixel(screen,at);data_text_cursor_done();assert(cursor_count==1);
        Uint32 rgb[256]={0};rgb[228]=SDL_MapRGB(target->format,255,0,255);
        data_text_cursor_present(r,screen,&dst,rgb,target->format);
        assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));
        Uint32 cursor;memcpy(&cursor,(Uint8 *)target->pixels+640*target->pitch+1040*4,4);assert(cursor==rgb[228]);
        data_text_cursor_clear();
    }
    /* Failure is local: no background erase before a validated font texture. */
    unsigned char *saved_exit=exit_bytes;char saved_directory[1024];strcpy(saved_directory,directory);
    data_text_invalidate();exit_bytes=NULL;exit_attempted=false;assert(strlen(output)<sizeof(directory));strcpy(directory,output);
    char path[4096];assert(snprintf(path,sizeof(path),"%s/data-exit-v1.hda",output)<(int)sizeof(path));
    for(unsigned failure=0;failure<5;++failure) {
        if(failure==4)assert(!mkfifo(path,0600));
        else if(failure) {
            FILE *bad=fopen(path,"wb");assert(bad);
            size_t length=failure==1 ? 1 : failure==2 ? DATA_EXIT_BYTES : DATA_EXIT_BYTES+1;
            for(size_t i=0;i<length;++i)assert(fputc(0,bad)!=EOF);assert(!fclose(bad));
        }
        SDL_SetRenderDrawColor(r,40,60,80,255);assert(!SDL_RenderClear(r));
        assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));uint64_t before=region_hash(target,area);
        exit_attempted=false;draw_exit(r,&dst,1040,640,false);assert(!exit_bytes&&!exit_texture);
        assert(!SDL_RenderReadPixels(r,NULL,target->format->format,target->pixels,target->pitch));assert(before==region_hash(target,area));
        if(failure)assert(!unlink(path));
    }
    strcpy(directory,saved_directory);exit_bytes=saved_exit;exit_attempted=true;
    data_text_cursor_clear();data_text_invalidate();SDL_DestroyRenderer(r);SDL_FreeSurface(target);
    puts("Exit: large gold shop font, both languages, list0-4, selection brightness, reader, F6, cursor-over-label, fade suspension and missing/truncated/corrupt/oversize/FIFO fallback passed");
}
int main(int argc,char **argv)
{
    assert(argc==4);decoder_tests();assert(SDL_Init(SDL_INIT_VIDEO)==0);cursor_sampler_tests();
    main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_ARGB8888);assert(main_window_tex_format);
    char palette_path[4096];assert(snprintf(palette_path,sizeof(palette_path),"%s/palette.dat",argv[1])<(int)sizeof(palette_path));FILE *pal=fopen(palette_path,"rb");assert(pal);
    for(unsigned i=0;i<256;++i){unsigned char c[3];assert(fread(c,1,3,pal)==3);palette[i]=(SDL_Color){(c[0]<<2)|(c[0]>>4),(c[1]<<2)|(c[1]>>4),(c[2]<<2)|(c[2]>>4),255};rgb_palette[i]=SDL_MapRGB(main_window_tex_format,palette[i].r,palette[i].g,palette[i].b);}fclose(pal);
    data_text_set_directory(argv[2]);load_resources();assert(resources_ok);assert(entry_count==149);
    struct ReadingMetrics large=reading_metrics(&(SDL_Rect){0,0,1280,800});
    struct ReadingMetrics small=reading_metrics(&(SDL_Rect){0,0,640,400});
    struct ReadingMetrics letter=reading_metrics(&(SDL_Rect){64,0,1152,720});
    struct ReadingMetrics integer=reading_metrics(&(SDL_Rect){160,60,960,600});
    assert(integer.font==16 && integer.leading==22 && integer.rows==14);
    assert(large.font==20 && large.leading==26 && large.rows==16 && large.width==1051);
    assert(small.font==16 && small.leading==22 && small.rows==9 && small.width==657);
    assert(letter.font==18 && letter.rows==16 && letter.clip.x>640);
    const struct ReadingMetrics metrics[]={small,large,letter,integer};
    for(unsigned i=0;i<4;++i)
        assert((int)(metrics[i].rows-1)*metrics[i].leading+48*metrics[i].font/36<=metrics[i].clip.h);
    unsigned longest=0,total=0,empty=0;
    const unsigned widths[]={small.width,large.width,letter.width,integer.width};
    for(unsigned layout=0;layout<4;++layout) {
        unsigned width=widths[layout];
        for(unsigned i=0;i<entry_count;++i) {
            const struct Entry *entry=&entries[i];
            if(!*entry->body){++empty;continue;}
            unsigned count=0;assert(wrap(entry->body,width,lines,MAX_LINES,&count));
            unsigned kept=0; const char *original=entry->body, *original_end=original+strlen(original);
            for(unsigned j=0;j<count;++j) {
                kept+=meaningful(lines[j].start,lines[j].end);
                const char *part=lines[j].start;
                while(part<lines[j].end) {
                    uint32_t actual, expected=0; assert(decode(&part,lines[j].end,&actual));
                    if(actual==' ' || actual=='\n' || actual=='~') continue;
                    do { assert(decode(&original,original_end,&expected)); } while(expected==' ' || expected=='\n' || expected=='~');
                    assert(actual==expected);
                }
            }
            assert(kept==meaningful(entry->body,entry->body+strlen(entry->body)));
            line_count=count; body_height=metrics[layout].clip.h;
            body_leading=metrics[layout].leading; body_cell=(48*metrics[layout].font+35)/36;
            for(unsigned at=0;at<line_count;++at) {
                unsigned visible=visible_lines(at);int y=0;
                for(unsigned j=0;j<visible && at+j<line_count;++j) { assert(y+line_extent(at+j)<=body_height); y+=line_advance(at+j); }
            }
            unsigned limit=max_scroll();assert(visible_lines(limit)==line_count-limit);
            if(limit)assert(visible_lines(limit-1)<line_count-limit+1);
            unsigned at=0,covered=0;
            for(;;) {
                unsigned end=at+visible_lines(at);assert(at<=covered);if(end>covered)covered=end;
                if(at==limit)break;unsigned next=end<limit?end:limit;assert(next>at);at=next;
            }
            assert(covered==line_count);covered=line_count;at=limit;
            for(;;) {
                assert(at+visible_lines(at)>=covered);covered=at;
                if(!at)break;unsigned next=page_start_before(at);assert(next<at);at=next;
            }
            assert(!covered);
            if(count>longest)longest=count;total+=count;
            struct Line tiny[1];unsigned one;assert(!wrap(entry->body,1,tiny,1,&one));
        }
    }
    assert(empty==16 && longest>40);
    body_width=large.width;page_lines=large.rows;body_height=large.clip.h;
    body_leading=large.leading;body_cell=(48*large.font+35)/36;
    char latin[6000];memset(latin,'A',sizeof(latin)-1);latin[sizeof(latin)-1]=0;unsigned latin_lines=0;
    assert(wrap(latin,BODY_WIDTH,lines,MAX_LINES,&latin_lines) && latin_lines>90);
    unsigned latin_kept=0;for(unsigned j=0;j<latin_lines;++j)latin_kept+=meaningful(lines[j].start,lines[j].end);assert(latin_kept==sizeof(latin)-1);
    size_t n=0;unsigned char *font=read_resource(argv[2],"data-text-zh-CN-v1.dzf",16u*1024u*1024u,&n);assert(font);
    assert(!parse_font(font,63));font[0]^=1;assert(!parse_font(font,n));font[0]^=1;
    put32(font+24,MAX_GLYPHS+1);assert(!parse_font(font,n));put32(font+24,glyph_count);
    font[64]^=1;assert(!parse_font(font,n));font[64]^=1;
    put32(font+64+8,u32(font+64));put64(font+48,fnv(font+64,n-64));assert(!parse_font(font,n));free(font);
    assert(parse_font(font_bytes,DATA_TEXT_FONT_BYTES));
    unsigned char *text=read_resource(argv[2],"data-text-zh-CN-v1.dct",1024u*1024u,&n);assert(text);
    assert(!parse_entries(text,23));text[0]^=1;assert(!parse_entries(text,n));text[0]^=1;
    text[48]=0xc0;put64(text+16,fnv(text+24,n-24));assert(!parse_entries(text,n));free(text);
    assert(parse_entries(text_bytes,DATA_TEXT_RESOURCE_BYTES));
    SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);assert(screen);SDL_FillRect(screen,NULL,228);
    uint64_t native_hash=fnv(screen->pixels,(size_t)screen->pitch*screen->h);
    for(unsigned ep=1;ep<=5;++ep){data_text_episode(ep,argv[1]);assert(source_ok);}
    data_text_episode(4,argv[1]);data_text_bind(0,5);data_text_bind(1,4);data_text_bind(2,6);data_text_bind(3,7);
    exit_label_tests(screen,argv[3]);
    data_text_set_language("zh-CN");data_text_begin(8,0,4,screen);assert(data_text_body_active());
    data_text_home(true);assert(scroll_offsets[0]==max_scroll());data_text_scroll(99999);assert(scroll_offsets[0]==max_scroll());
    data_text_scroll(INT_MAX);assert(scroll_offsets[0]==max_scroll());data_text_scroll(INT_MIN);assert(!scroll_offsets[0]);
    data_text_scroll(-99999);assert(!scroll_offsets[0]);data_text_scroll(9);unsigned before=scroll_offsets[0];assert(before==9);
    data_text_scroll_held(0,false);data_text_home(false);unsigned step=page_step(1);data_text_scroll_held(1,true);assert(scroll_offsets[0]==step);
    data_text_scroll_held(1,true);assert(scroll_offsets[0]==step);SDL_Delay(90);step+=page_step(1);data_text_scroll_held(1,true);assert(scroll_offsets[0]==(step<max_scroll()?step:max_scroll()));
    data_text_scroll_held(0,false);data_text_home(false);data_text_mouse_scroll(1);assert(scroll_offsets[0]==1);data_text_scroll_held(1,false);assert(scroll_offsets[0]==1);
    data_text_home(false);data_text_scroll(9);before=scroll_offsets[0];
    data_text_toggle();assert(!data_text_body_active());data_text_toggle();assert(data_text_body_active() && scroll_offsets[0]==before);
    for(unsigned run=0;run<3;++run){
        int width=run?1280:640,height=run==2?720:run?800:400;
        SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,width,height,32,SDL_PIXELFORMAT_ARGB8888);assert(target);
        SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(target);assert(renderer);
        data_text_home(false);render(renderer,target,screen,argv[3],"reader-first",width,height);
        assert(page_lines==(run?16u:9u));
        assert(visible_lines(0)>page_lines); /* Half-line paragraph gaps fit more content. */
        for(unsigned first=0;first<line_count;++first) {
            unsigned visible=visible_lines(first);int y=0;
            for(unsigned j=0;j<visible && first+j<line_count;++j){assert(y+line_extent(first+j)<=body_height);y+=line_advance(first+j);}
        }
        assert(visible_lines(max_scroll())==line_count-max_scroll());
        if(max_scroll())assert(visible_lines(max_scroll()-1)<line_count-max_scroll()+1);
        unsigned step=page_step(1);data_text_page(1);assert(scroll_offsets[0]==step);
        data_text_page(-1);assert(scroll_offsets[0]==0);
        data_text_home(true);assert(scroll_offsets[0]==max_scroll());
        data_text_scroll_held(0,false);data_text_home(false);data_text_scroll_held(1,true);
        assert(scroll_offsets[0]==step);
        const char *anchor=scroll_anchors[0];
        data_text_begin(8,1,4,screen);data_text_home(false);data_text_scroll(3);
        const char *other_anchor=scroll_anchors[1];
        data_text_begin(8,0,4,screen);
        assert(lines[scroll_offsets[0]].start==anchor);
        SDL_Rect resized=run ? (SDL_Rect){0,0,640,400} : (SDL_Rect){0,0,1280,800};
        data_text_present(renderer,screen,&resized);
        assert(scroll_offsets[0]<=max_scroll());
        assert(lines[scroll_offsets[0]].start<=anchor && (scroll_offsets[0]+1>=line_count || lines[scroll_offsets[0]+1].start>anchor));
        data_text_begin(8,1,4,screen);
        assert(lines[scroll_offsets[1]].start<=other_anchor && (scroll_offsets[1]+1>=line_count || lines[scroll_offsets[1]+1].start>other_anchor));
        data_text_begin(8,0,4,screen);
        data_text_home(true);data_text_present(renderer,screen,&(SDL_Rect){64,0,1152,720});
        assert(scroll_offsets[0]<=max_scroll());
        render(renderer,target,screen,argv[3],"reader-resized",width,height);
        data_text_home(false);
        data_text_transition(true);uint64_t paused=fnv(target->pixels,(size_t)target->pitch*target->h);data_text_present(renderer,screen,&(SDL_Rect){0,0,width,height});assert(paused==fnv(target->pixels,(size_t)target->pitch*target->h));data_text_transition(false);assert(data_text_body_active());
        data_text_invalidate();assert(prepare_texture(renderer));
        data_text_cursor_begin(screen);const Uint8 *cursor=(const Uint8 *)screen->pixels+80*screen->pitch+200;data_text_cursor_pixel(screen,cursor);data_text_cursor_done();assert(cursor_count==1);
        Uint32 rgb[256]={0};rgb[228]=SDL_MapRGB(target->format,255,0,255);
        data_text_cursor_present(renderer,screen,&(SDL_Rect){0,0,width,height},rgb,target->format);
        assert(SDL_RenderReadPixels(renderer,NULL,target->format->format,target->pixels,target->pitch)==0);
        Uint32 pixel;memcpy(&pixel,(Uint8 *)target->pixels+(80*height/200)*target->pitch+(200*width/320)*4,4);Uint8 rr,gg,bb;SDL_GetRGB(pixel,target->format,&rr,&gg,&bb);assert(rr==255&&gg==0&&bb==255);data_text_cursor_clear();
        /* Frame-owned English cursor replay is independent of optional font readiness. */
        data_text_set_language("en");data_text_cursor_frame_owner(true);resources_ok=false;
        data_text_cursor_begin(screen);data_text_cursor_pixel(screen,cursor);data_text_cursor_done();assert(cursor_count==1);
        rgb[228]=SDL_MapRGB(target->format,0,255,127);
        data_text_cursor_present(renderer,screen,&(SDL_Rect){0,0,width,height},rgb,target->format);
        assert(SDL_RenderReadPixels(renderer,NULL,target->format->format,target->pixels,target->pitch)==0);
        memcpy(&pixel,(Uint8 *)target->pixels+(80*height/200)*target->pitch+(200*width/320)*4,4);SDL_GetRGB(pixel,target->format,&rr,&gg,&bb);assert(rr==0&&gg==255&&bb==127);
        data_text_cursor_clear();data_text_cursor_frame_owner(false);resources_ok=true;data_text_set_language("zh-CN");
        data_text_home(true);render(renderer,target,screen,argv[3],"reader-last",width,height);
        data_text_begin(7,0,4,screen);render(renderer,target,screen,argv[3],"list",width,height);
        data_text_begin(0,0,4,screen);uint64_t h=fnv(target->pixels,(size_t)target->pitch*target->h);data_text_present(renderer,screen,&(SDL_Rect){0,0,width,height});assert(h==fnv(target->pixels,(size_t)target->pitch*target->h));
        data_text_invalidate();SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);data_text_begin(8,0,4,screen);
    }
    assert(native_hash==fnv(screen->pixels,(size_t)screen->pitch*screen->h));
    data_text_end();assert(!data_text_body_active());data_text_begin(8,0,4,screen);assert(data_text_body_active());
    data_text_episode(4,"/missing");data_text_bind(0,5);data_text_begin(8,0,1,screen);assert(!source_ok && !data_text_body_active());
    char fifo[4096];snprintf(fifo,sizeof(fifo),"%s/data-text-zh-CN-v1.dzf",argv[3]);assert(mkfifo(fifo,0600)==0);
    data_text_set_directory(argv[3]);data_text_begin(8,0,1,screen);assert(!resources_ok && !data_text_body_active());
    data_text_set_directory("/missing");data_text_begin(8,0,1,screen);assert(!resources_ok && !data_text_body_active());
    data_text_set_language("garbage");assert(!strcmp(data_text_language(),"en"));
    SDL_FreeSurface(screen);SDL_Quit();printf("Data text: 149 entries, %u body lines, longest %u, four original empty bodies, strict UTF8/parser/fallback/scroll/toggle/native-equivalence/viewport640+1280+letterbox/page+resize-anchor passed\n",total,longest);return 0;
}
