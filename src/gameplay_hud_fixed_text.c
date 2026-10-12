/* Optional finite HUT1 baked labels. No original asset bytes are shipped. */
#include "gameplay_hud_fixed_text.h"
#include <fcntl.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define HUD_OPEN(path) _open(path, _O_RDONLY | _O_BINARY | _O_NOINHERIT)
#define HUD_READ _read
#define HUD_CLOSE _close
#define HUD_FSTAT _fstat
#define HUD_STAT struct _stat
#define HUD_REGULAR(mode) (((mode) & _S_IFMT) == _S_IFREG)
#else
#include <unistd.h>
/* Check the opened object. Nonblocking open also keeps FIFOs bounded. */
#define HUD_OPEN(path) open(path, O_RDONLY | O_NONBLOCK)
#define HUD_READ read
#define HUD_CLOSE close
#define HUD_FSTAT fstat
#define HUD_STAT struct stat
#define HUD_REGULAR(mode) S_ISREG(mode)
#endif


#ifndef HUD_FIXED_PIC3_FNV
#define HUD_FIXED_PIC3_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_FIXED_PALETTE_FNV
#define HUD_FIXED_PALETTE_FNV UINT64_C(0x5e80e83992be2927)
#endif
#ifndef HUD_FIXED_SOURCE_FNV
#define HUD_FIXED_SOURCE_FNV UINT64_C(0xb110512dd1fc63f4)
#endif

enum { SOURCE_WIDTH=320, SOURCE_HEIGHT=200, DENSITY=4,
       HEADER_BYTES=64, PAYLOAD_BYTES=23680, FILE_BYTES=23744 };
/* Tile/source serialization is fixed, without a resource-provided coordinate. */
static const struct { int x,y,w,offset; } tiles[12]={
 {284,54,19,0}, {285,138,5,95}, {285,144,5,120}, {285,150,5,145},
 {285,156,5,170}, {285,162,5,195}, {285,168,5,220},
 {296,138,5,245}, {296,144,5,270}, {296,150,5,295},
 {296,156,5,320}, {296,162,5,345}
};
static bool attempted,captured;
static uint8_t *payload;
static uint8_t source_indices[370];
static uint32_t read_u32(const uint8_t *p)
{
	return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
	       ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t read_u64(const uint8_t *p)
{
	return (uint64_t)read_u32(p) | ((uint64_t)read_u32(p + 4) << 32);
}

static uint64_t fnv_update(uint64_t hash, const uint8_t *bytes, size_t count)
{
	for (size_t i = 0; i < count; ++i)
		hash = (hash ^ bytes[i]) * UINT64_C(1099511628211);
	return hash;
}

static uint64_t fnv64(const uint8_t *bytes, size_t count)
{
	return fnv_update(UINT64_C(14695981039346656037), bytes, count);
}


static bool valid_header(const uint8_t *h)
{
 return !memcmp(h,"HUT1",4)&&read_u32(h+4)==1&&read_u32(h+8)==4&&
  read_u32(h+12)==12&&read_u32(h+16)==370&&read_u32(h+20)==PAYLOAD_BYTES&&
  read_u32(h+24)==1&&read_u32(h+28)==0&&
  read_u64(h+32)==HUD_FIXED_PIC3_FNV&&read_u64(h+40)==HUD_FIXED_PALETTE_FNV&&
  read_u64(h+48)==HUD_FIXED_SOURCE_FNV;
}
static bool valid_payload(const uint8_t *data,const uint8_t *h)
{
 if(fnv64(data,PAYLOAD_BYTES)!=read_u64(h+56))return false;
 for(size_t i=3;i<PAYLOAD_BYTES;i+=4)if(data[i]!=255)return false;
 return true;
}
/* Each request fits _read's unsigned count. Short reads and interruptions fail
 * closed rather than introducing an unbounded retry loop. */
static bool read_exact(int file, uint8_t *data, unsigned count)
{
	return HUD_READ(file, data, count) == (long)count;
}

bool hud_fixed_text_load(const char *directory)
{
	char path[1024];
	uint8_t header[HEADER_BYTES], extra;
	HUD_STAT status;
	uint8_t *data = NULL;
	bool valid = false;
	int length, file;

	if (attempted)
		return payload != NULL;
	attempted = true;
	if (!directory || !*directory)
		return false;
	length = snprintf(path, sizeof(path), "%s/gameplay-hud-fixed-text-v1.hda", directory);
	if (length < 0 || (size_t)length >= sizeof(path))
		return false;
	file = HUD_OPEN(path);
	if (file < 0)
		return false;
	if (HUD_FSTAT(file, &status) || !HUD_REGULAR(status.st_mode) ||
	    status.st_size != FILE_BYTES ||
	    !read_exact(file, header, sizeof(header)) || !valid_header(header))
		goto done;
	data = malloc(PAYLOAD_BYTES);
	if (!data || !read_exact(file, data, PAYLOAD_BYTES) ||
	    HUD_READ(file, &extra, 1) != 0)
		goto done;
	valid = valid_payload(data, header);

done:
	if (HUD_CLOSE(file))
		valid = false;
	if (!valid)
	{
		free(data);
		return false;
	}
	payload = data;
	return true;
}


static bool valid_source(const uint8_t *indices,int pitch)
{
 return indices&&pitch>=320&&(size_t)pitch<=(SIZE_MAX-320)/199;
}
void hud_fixed_text_forget_source(void) {captured=false;}
void hud_fixed_text_shutdown(void)
{
 hud_fixed_text_forget_source();free(payload);payload=NULL;attempted=false;
}
bool hud_fixed_text_ready(void) {return payload&&captured;}
bool hud_fixed_text_capture(const uint8_t *indices,int pitch)
{
 uint64_t hash=UINT64_C(14695981039346656037);
 hud_fixed_text_forget_source();
 if(!payload||!valid_source(indices,pitch))return false;
 for(int y=0;y<200;y++)hash=fnv_update(hash,indices+(size_t)y*pitch,320);
 if(hash!=HUD_FIXED_PIC3_FNV)return false;
 for(int i=0;i<12;i++)for(int y=0;y<5;y++)
  memcpy(source_indices+tiles[i].offset+y*tiles[i].w,
   indices+(size_t)(tiles[i].y+y)*pitch+tiles[i].x,(size_t)tiles[i].w);
 if(fnv64(source_indices,sizeof(source_indices))!=HUD_FIXED_SOURCE_FNV)return false;
 captured=true;return true;
}
bool hud_fixed_text_palette_matches(const uint32_t packed_rgb[256])
{
 uint64_t hash=UINT64_C(14695981039346656037);
 if(!payload||!packed_rgb)return false;
 for(int i=0;i<256;i++) {
  uint8_t rgb[3]={(uint8_t)(packed_rgb[i]>>16),(uint8_t)(packed_rgb[i]>>8),(uint8_t)packed_rgb[i]};
  hash=fnv_update(hash,rgb,3);
 }
 return hash==HUD_FIXED_PALETTE_FNV;
}
/* Compact fixed ledger: MODE0..94, SHIELD95..244, ARMOR245..369. */
bool hud_fixed_text_position(unsigned cell,int *x,int *y)
{
 if(cell>=370||!x||!y)return false;
 for(unsigned i=0;i<12;i++)if(cell>=(unsigned)tiles[i].offset&&cell<(unsigned)(tiles[i].offset+tiles[i].w*5)) {
  unsigned local=cell-(unsigned)tiles[i].offset;
  *x=tiles[i].x+(int)(local%(unsigned)tiles[i].w);
  *y=tiles[i].y+(int)(local/(unsigned)tiles[i].w);return true;
 }
 return false;
}
int hud_fixed_text_cell(int x,int y)
{
 /* The fade loop asks once per subpixel. Reject outside the finite boxes
  * without scanning all12tiles, preserving the same370-cell layout. */
 if(x>=284&&x<303&&y>=54&&y<59)return (y-54)*19+x-284;
 if(y<138||y>=173)return -1;
 int row=(y-138)/6,dy=(y-138)%6;
 if(dy>=5)return -1;
 if(x>=285&&x<290)return 95+row*25+dy*5+x-285;
 if(x>=296&&x<301&&row<5)return 245+row*25+dy*5+x-296;
 return -1;
}
bool hud_fixed_text_group_matches(unsigned group,const uint8_t *indices,int pitch)
{
 if(!hud_fixed_text_ready()||group>=3||!valid_source(indices,pitch))return false;
 unsigned first=group==0?0:group==1?1:7,last=group==0?1:group==1?7:12;
 for(unsigned i=first;i<last;i++)for(int y=0;y<5;y++)
  if(memcmp(source_indices+tiles[i].offset+y*tiles[i].w,
   indices+(size_t)(tiles[i].y+y)*pitch+tiles[i].x,(size_t)tiles[i].w))return false;
 return true;
}
const uint8_t *hud_fixed_text_sample(unsigned cell,int sx,int sy,int density)
{
 if(!hud_fixed_text_ready()||cell>=370||(density!=4&&density!=8)||sx<0||sy<0||sx>=density||sy>=density)return NULL;
 for(unsigned i=0;i<12;i++)if(cell>=(unsigned)tiles[i].offset&&cell<(unsigned)(tiles[i].offset+tiles[i].w*5)) {
  unsigned local=cell-(unsigned)tiles[i].offset,dx=local%(unsigned)tiles[i].w,dy=local/(unsigned)tiles[i].w;
  size_t pixel=(size_t)tiles[i].offset*16+(dy*4+(unsigned)(sy/(density/4)))*tiles[i].w*4+dx*4+(unsigned)(sx/(density/4));
  return payload+pixel*4;
 }
 return NULL;
}
