/* SPDX-License-Identifier: GPL-2.0-or-later
 * SHOP HDR1 fd adapter. SF_* keeps the existing platform flags and IO API.
 * Geometry/path and owner/cache decisions deliberately remain with callers.
 */
#include "shared_asset_reader.h"
static Uint8 *shared_asset_load_fd(const char *path,const GlobalAssetResource *r,bool reject_close_error)
{
 int fd=SF_OPEN(path);if(fd<0)return NULL;
 Uint8 h[28],extra;SF_STAT st;
 bool ok=SF_FSTAT(fd,&st)==0&&SF_REGULAR(st.st_mode)&&st.st_size==r->bytes&&
  SF_READ(fd,h,28)==28&&shared_asset_header_matches(h,r);
 Uint8 *p=ok?malloc(r->bytes-28u):NULL;size_t at=0;
 while(p&&at<r->bytes-28u){int n=SF_READ(fd,p+at,r->bytes-28u-at);if(n<=0)break;at+=(unsigned)n;}
 ok=p&&at==r->bytes-28u&&SF_READ(fd,&extra,1)==0&&shared_asset_hash(p,r->bytes-28u)==r->payload_fnv;
 int closed=SF_CLOSE(fd);if(reject_close_error&&closed)ok=false;
 if(!ok){free(p);return NULL;}return p;
}
