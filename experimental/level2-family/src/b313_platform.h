#ifndef B313_PLATFORM_H
#define B313_PLATFORM_H
/* Explicit platform adapters; no renderer permissions or global API aliases. */
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#define B313_SHA256_BYTES 32
#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <bcrypt.h>
#include <io.h>
#include <fcntl.h>
#include <sys/stat.h>
#pragma comment(lib, "bcrypt.lib")
static inline int b313_windows_error(DWORD e)
{
 switch(e){
 case ERROR_FILE_EXISTS:case ERROR_ALREADY_EXISTS:errno=EEXIST;break;
 case ERROR_FILE_NOT_FOUND:case ERROR_PATH_NOT_FOUND:errno=ENOENT;break;
 case ERROR_ACCESS_DENIED:case ERROR_SHARING_VIOLATION:errno=EACCES;break;
 case ERROR_DISK_FULL:errno=ENOSPC;break;
 case ERROR_NOT_ENOUGH_MEMORY:case ERROR_OUTOFMEMORY:errno=ENOMEM;break;
 case ERROR_INVALID_PARAMETER:errno=EINVAL;break;
 default:errno=EIO;break;
 }
 return -1;
}
static inline bool b313_sha256(const void *data,size_t size,unsigned char out[B313_SHA256_BYTES])
{
 BCRYPT_ALG_HANDLE alg=NULL;BCRYPT_HASH_HANDLE hash=NULL;
 PUCHAR object=NULL;DWORD object_size=0,digest_size=0,got=0;
 bool ok=false;const unsigned char *p=(const unsigned char *)data;
 if(!out||(!data&&size)){errno=EINVAL;return false;}
 if(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,NULL,0)<0)goto done;
 if(BCryptGetProperty(alg,BCRYPT_OBJECT_LENGTH,(PUCHAR)&object_size,sizeof object_size,&got,0)<0||got!=sizeof object_size||!object_size)goto done;
 if(BCryptGetProperty(alg,BCRYPT_HASH_LENGTH,(PUCHAR)&digest_size,sizeof digest_size,&got,0)<0||got!=sizeof digest_size||digest_size!=B313_SHA256_BYTES)goto done;
 object=(PUCHAR)malloc(object_size);if(!object)goto done;
 if(BCryptCreateHash(alg,&hash,object,object_size,NULL,0,0)<0)goto done;
 while(size){ULONG n=size>ULONG_MAX?ULONG_MAX:(ULONG)size;
  if(BCryptHashData(hash,(PUCHAR)p,n,0)<0)goto done;
  p+=n;size-=n;
 }
 if(BCryptFinishHash(hash,out,B313_SHA256_BYTES,0)<0)goto done;
 ok=true;
 done:
 if(hash&&BCryptDestroyHash(hash)<0)ok=false;
 if(alg&&BCryptCloseAlgorithmProvider(alg,0)<0)ok=false;
 free(object);
 if(!ok)errno=EIO;
 return ok;
}
static inline bool b313_regular_file_size(FILE *f,uint64_t *size)
{
 struct _stat64 st;
 if(!f||!size){errno=EINVAL;return false;}
 if(_fstat64(_fileno(f),&st))return false;
 if((st.st_mode&_S_IFMT)!=_S_IFREG||st.st_size<0){errno=EINVAL;return false;}
 *size=(uint64_t)st.st_size;return true;
}
static inline bool b313_monotonic_time(uint64_t *sec,uint64_t *nsec)
{
 LARGE_INTEGER count,freq;
 if(!sec||!nsec){errno=EINVAL;return false;}
 if(!QueryPerformanceFrequency(&freq)||!QueryPerformanceCounter(&count)||freq.QuadPart<=0||count.QuadPart<0){errno=EIO;return false;}
 uint64_t f=(uint64_t)freq.QuadPart,c=(uint64_t)count.QuadPart;
 /* Reject impossible/unsupported frequency rather than overflowing conversion. */
 if(f>UINT64_MAX/UINT64_C(1000000000)){errno=ERANGE;return false;}
 *sec=c/f;*nsec=((c%f)*UINT64_C(1000000000))/f;return true;
}
static inline uint64_t b313_process_id(void){return (uint64_t)GetCurrentProcessId();}
static inline int b313_open_exclusive(const char *path){return _open(path,_O_WRONLY|_O_CREAT|_O_EXCL|_O_BINARY|_O_NOINHERIT,_S_IREAD|_S_IWRITE);}
static inline FILE *b313_fdopen_write(int fd){return _fdopen(fd,"wb");}
static inline int b313_close(int fd){return _close(fd);}
static inline int b313_unlink(const char *path){return _unlink(path);}
static inline int b313_sync_file(FILE *f){return _commit(_fileno(f));}
static inline int b313_publish_no_replace(const char *temporary,const char *final)
{
 /* Same-volume hard link: existing final names are never replaced. No copy fallback. */
 if(CreateHardLinkA(final,temporary,NULL))return 0;
 return b313_windows_error(GetLastError());
}
#else
/* Translation units must define _POSIX_C_SOURCE=200809L before system headers. */
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <time.h>
#include <openssl/sha.h>
static inline bool b313_sha256(const void *data,size_t size,unsigned char out[B313_SHA256_BYTES])
{
 if(!out||(!data&&size)){errno=EINVAL;return false;}
 return SHA256((const unsigned char *)(data?data:""),size,out)!=NULL;
}
static inline bool b313_regular_file_size(FILE *f,uint64_t *size)
{
 struct stat st;
 if(!f||!size){errno=EINVAL;return false;}
 if(fstat(fileno(f),&st))return false;
 if(!S_ISREG(st.st_mode)||st.st_size<0){errno=EINVAL;return false;}
 *size=(uint64_t)st.st_size;return true;
}
static inline bool b313_monotonic_time(uint64_t *sec,uint64_t *nsec)
{
 struct timespec t;
 if(!sec||!nsec){errno=EINVAL;return false;}
 if(clock_gettime(CLOCK_MONOTONIC,&t))return false;
 if(t.tv_sec<0||t.tv_nsec<0||t.tv_nsec>=1000000000L){errno=ERANGE;return false;}
 *sec=(uint64_t)t.tv_sec;*nsec=(uint64_t)t.tv_nsec;return true;
}
static inline uint64_t b313_process_id(void){return (uint64_t)getpid();}
static inline int b313_open_exclusive(const char *path){return open(path,O_WRONLY|O_CREAT|O_EXCL,0600);}
static inline FILE *b313_fdopen_write(int fd){return fdopen(fd,"w");}
static inline int b313_close(int fd){return close(fd);}
static inline int b313_unlink(const char *path){return unlink(path);}
static inline int b313_sync_file(FILE *f){return fsync(fileno(f));}
static inline int b313_publish_no_replace(const char *temporary,const char *final){return link(temporary,final);}
#endif
#endif
