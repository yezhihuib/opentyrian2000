/* SPDX-License-Identifier: GPL-2.0-or-later
 * Triple275 later132 reuse, exact1 and default OFF. No gameplay authority.
 * Bit2 in existing mode values remains the original per-family flag; bit4 is
 * the independently requested later group, restricted to ordinary ASTEROID2.
 * The complete original731 stream is sealed only at the actual native level
 * load, before native events mutate their own fields. Runtime checks below
 * inspect only each exact selected case6 row; never restore native event data.
 */
/* Native global is defined by the unchanged tyrian2.c; read-only here. */
extern struct JE_EventRecType eventRec[];
static bool triple275_later132_requested(void)
{
 const char *v=getenv("TRIPLE275_LATER_132_ENABLE");
 return v&&!strcmp(v,"1")&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled;
}
static bool triple275_later132_stream_matches(const struct JE_EventRecType *events)
{
 if(!events||events!=eventRec||maxEvent!=731)return false;
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<731;i++){
  const struct JE_EventRecType *r=events+i;
  /* Exact on-disk order <HBhhbbbB>, independent of host struct padding. */
  Uint8 b[11]={(Uint8)r->eventtime,(Uint8)(r->eventtime>>8),r->eventtype,
   (Uint8)r->eventdat,(Uint8)((uint16_t)r->eventdat>>8),
   (Uint8)r->eventdat2,(Uint8)((uint16_t)r->eventdat2>>8),
   (Uint8)r->eventdat3,(Uint8)r->eventdat5,(Uint8)r->eventdat6,r->eventdat4};
  for(unsigned j=0;j<11;j++){h^=b[j];h*=UINT64_C(1099511628211);}
 }
 return h==UINT64_C(0xa6df39659b2d348d);
}
