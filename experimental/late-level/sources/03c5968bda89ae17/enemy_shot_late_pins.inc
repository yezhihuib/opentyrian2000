/* Separate, closed late-emitter table. Existing es_weapons and es_next_emitters stay unchanged. */
static const struct {unsigned record,weapon,turret,event[4];uint64_t record_stamp,weapon_stamp;} es_late_emitters[]={
 {282,59,1,{319,320,325,326},UINT64_C(0x8ccd3e8ca782f6f9),UINT64_C(0x213ae11f3eda4ea8)},
 {285,24,1,{291,296,301,312},UINT64_C(0x7329f43eb20aa601),UINT64_C(0x04c6cf64e3602dab)},
};
/* These colors are required only by a contributing91 draw, never by old shots alone. */
static const struct {unsigned index;uint32_t rgb;} es_late_palette[]={{1,0x0c0c0cu},{2,0x181818u},{5,0x454545u},{6,0x515151u},{7,0x5d5d5du},{8,0x696d69u},{9,0x797979u},{10,0x8e8e8eu},{11,0xa2a6a2u},{12,0xbababau},{13,0xcfcfcfu},{14,0xe7e7e7u},{15,0xfbffffu}};
