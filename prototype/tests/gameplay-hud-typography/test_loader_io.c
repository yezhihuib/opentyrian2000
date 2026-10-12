#include "gameplay_hud_fixed_text.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#define CHECK(x) assert(x)
#define PAYLOAD_BYTES 23680
#define FILE_BYTES 23744
static size_t allocations,frees,opens,reads,closes,stats;
static void *live_pointer;
static int live_descriptor=-1,reject_allocation,reject_stat,reject_close;
static int fail_read_number,short_read_number,override_size=-1;
void *fixed_test_malloc(size_t size)
{
	++allocations;
	CHECK(size == PAYLOAD_BYTES && live_pointer == NULL);
	if (reject_allocation) return NULL;
	live_pointer = malloc(size);
	CHECK(live_pointer != NULL);
	return live_pointer;
}

void fixed_test_free(void *pointer)
{
	if (pointer)
	{
		CHECK(pointer == live_pointer);
		++frees;
		live_pointer = NULL;
	}
	free(pointer);
}

int fixed_test_open(const char *path, int flags, ...)
{
	CHECK(live_descriptor == -1);
	++opens;
	live_descriptor = open(path, flags);
	return live_descriptor;
}

ssize_t fixed_test_read(int descriptor, void *buffer, size_t count)
{
	CHECK(descriptor == live_descriptor && count <= PAYLOAD_BYTES);
	++reads;
	if (fail_read_number && --fail_read_number == 0)
	{
		errno = EIO;
		return -1;
	}
	if (short_read_number && --short_read_number == 0) return read(descriptor, buffer, count - 1);
	return read(descriptor, buffer, count);
}

int fixed_test_fstat(int descriptor, struct stat *status)
{
	int result;
	CHECK(descriptor == live_descriptor);
	++stats;
	if (reject_stat) return -1;
	result = fstat(descriptor, status);
	if (!result && override_size >= 0) status->st_size = override_size;
	return result;
}

int fixed_test_close(int descriptor)
{
	int result;
	CHECK(descriptor == live_descriptor);
	++closes;
	live_descriptor = -1;
	result = close(descriptor);
	return reject_close ? -1 : result;
}


static unsigned cases;
static void reject(const char *path)
{
 size_t opened=opens,closed=closes;assert(!hud_fixed_text_load(path));
 assert(!live_pointer&&live_descriptor==-1);assert(opens==opened+1&&closes==closed+1);
 assert(!hud_fixed_text_load(path));assert(opens==opened+1);
 hud_fixed_text_shutdown();assert(!live_pointer&&live_descriptor==-1);
 reject_allocation=reject_stat=reject_close=fail_read_number=short_read_number=0;override_size=-1;cases++;
}
static void write_resource(const char *file,const unsigned char *raw,size_t size)
{FILE *f=fopen(file,"wb");assert(f);assert(fwrite(raw,1,size,f)==size);assert(!fclose(f));}
int main(int argc,char **argv)
{
 assert(argc>=2);char file[1200];snprintf(file,sizeof(file),"%s/gameplay-hud-fixed-text-v1.hda",argv[1]);
 unsigned char raw[FILE_BYTES+1];FILE *f=fopen(file,"rb");assert(f);assert(fread(raw,1,FILE_BYTES,f)==FILE_BYTES);fclose(f);raw[FILE_BYTES]=1;
 if(argc==3){reject(argv[1]);assert(allocations==0);puts("HUT1 production guard constants reject synthetic source contract.");return 0;}
 reject_allocation=1;reject(argv[1]);reject_stat=1;reject(argv[1]);reject_close=1;reject(argv[1]);
 for(int n=1;n<=3;n++){fail_read_number=n;reject(argv[1]);}
 for(int n=1;n<=2;n++){short_read_number=n;reject(argv[1]);}
 size_t sizes[]={63,FILE_BYTES-1,FILE_BYTES+1};
 for(unsigned i=0;i<3;i++){write_resource(file,raw,sizes[i]);override_size=FILE_BYTES;reject(argv[1]);}
 write_resource(file,raw,FILE_BYTES);assert(hud_fixed_text_load(argv[1]));assert(live_pointer&&live_descriptor==-1);
 size_t o=opens,r=reads,a=allocations;assert(hud_fixed_text_load(argv[1]));assert(opens==o&&reads==r&&allocations==a);
 hud_fixed_text_shutdown();assert(!live_pointer&&live_descriptor==-1);assert(allocations==frees+1); /* one deliberate allocation failure */
 printf("HUT1 I/O accounting PASS:%u failures,short/racing file rejection,one attempt,no leaked allocation/descriptor.\n",cases);
}
