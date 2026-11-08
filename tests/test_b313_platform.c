#define _POSIX_C_SOURCE 200809L
/* Run only in a fresh disposable working directory. No game or SDL dependency.
 * POSIX: cc -std=c99 -I<overlay> test_b313_platform.c -lcrypto -o test-platform
 * MSVC: cl /std:c11 /I<overlay> test_b313_platform.c /link bcrypt.lib
 * Deliberately no NDEBUG: assertions include test actions.
 */
#ifdef NDEBUG
#error Build this regression with assertions enabled
#endif
#include "b313_platform.h"
#include <assert.h>
#include <string.h>
static void vector(const void *data,size_t bytes,const char *expected)
{
 unsigned char digest[B313_SHA256_BYTES];char hex[65];
 static const char digits[]="0123456789abcdef";
 assert(b313_sha256(data,bytes,digest));
 for(unsigned i=0;i<32;i++){hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}
 hex[64]=0;assert(!strcmp(hex,expected));
}
int main(void)
{
 vector(NULL,0,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
 vector("abc",3,"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
 vector("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",56,"248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
 uint64_t sec,nsec,sec2,nsec2,size;
 assert(b313_process_id()>0&&b313_monotonic_time(&sec,&nsec));
 assert(b313_monotonic_time(&sec2,&nsec2)&&nsec<1000000000&&nsec2<1000000000);
 assert(sec2>sec||(sec2==sec&&nsec2>=nsec));
 const char *tmp="platform-exclusive.tmp",*final="platform-final.json",*other="platform-other.tmp";
 int fd=b313_open_exclusive(tmp);assert(fd>=0);
 errno=0;assert(b313_open_exclusive(tmp)<0&&errno==EEXIST);
 FILE *f=b313_fdopen_write(fd);assert(f);
 const unsigned char bytes[]={0x41,0x0a,0x1a,0x00,0xff};
 assert(fwrite(bytes,1,sizeof bytes,f)==sizeof bytes);
 assert(!fflush(f)&&!b313_sync_file(f));
 assert(b313_regular_file_size(f,&size)&&size==sizeof bytes);
 assert(!fclose(f));
 assert(!b313_publish_no_replace(tmp,final));
 fd=b313_open_exclusive(other);assert(fd>=0);f=b313_fdopen_write(fd);assert(f);
 assert(fputs("replacement",f)>=0&&!fflush(f)&&!b313_sync_file(f)&&!fclose(f));
 errno=0;assert(b313_publish_no_replace(other,final)<0&&errno==EEXIST);
 assert(!b313_unlink(tmp));
 f=fopen(final,"rb");assert(f);unsigned char got[sizeof bytes];
 assert(fread(got,1,sizeof got,f)==sizeof got&&!memcmp(got,bytes,sizeof bytes));
 assert(fgetc(f)==EOF&&!ferror(f)&&!fclose(f));
 assert(b313_publish_no_replace("missing-source.tmp","missing-final.json")<0);
 assert(!b313_unlink(other)&&!b313_unlink(final));
 return 0;
}
