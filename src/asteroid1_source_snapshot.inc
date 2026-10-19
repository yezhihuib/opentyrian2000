/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared renderer-owned reference for the five strict NEWshd families.
 * Never alias a live sprite bank or trust a loaded pointer instead of its bytes.
 */
static struct {bool valid;Uint8 bytes[42012];} asteroid1_source_snapshot;
static bool asteroid1_source_bytes_match(const Uint8 *p,size_t n)
{
 if(!p||n!=sizeof(asteroid1_source_snapshot.bytes))return false;
 if(!asteroid1_source_snapshot.valid) {
  /* Pin the private copy, not the live bank followed by an unverified copy. */
  memcpy(asteroid1_source_snapshot.bytes,p,n);
  asteroid1_source_snapshot.valid=asteroid1_stamp(asteroid1_source_snapshot.bytes,n)==UINT64_C(0x913975450e0fc00d);
 }
 /* Once pinned, the reference stays immutable until renderer shutdown.
  * Compare on EVERY call, including same-address mutation and bank reload. */
 return asteroid1_source_snapshot.valid&&!memcmp(p,asteroid1_source_snapshot.bytes,n);
}
