#include "b313_tail414_control.h"
#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#if defined(B313_V6_ANIMATION_DIAGNOSTIC) && B313_V6_ANIMATION_DIAGNOSTIC
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static bool initialized;
static unsigned tick,phase;
static int top;
static char names[B313_REPORT_COUNT][2][96];
static void initialize(void)
{
 if(initialized)return;
 initialized=true;tick=UINT_MAX;phase=3;top=0;
 const char *v=getenv("BUILDING313_V6_SLICE_TICK");
 if(b313_conservative_enabled()){tick=408;phase=1;top=101;}
 else if(b313_recovery_enabled()){tick=411;phase=2;top=104;}
 else if(b313_sequence_enabled()){tick=408;phase=1;top=101;}
 else if(!v||!strcmp(v,"415")){tick=415;phase=0;top=108;}
 else if(!strcmp(v,"408")){tick=408;phase=1;top=101;}
 else if(!strcmp(v,"411")){tick=411;phase=2;top=104;}
 static const char *const stem[B313_REPORT_COUNT]={"native-writer-observer","building313-native-scope","building313-identity","building313-sample-tags","building313-precommit","building313-final-proof","building313-v6-locked-prefix","building313-v6-selected-transaction"};
 for(unsigned i=0;i<B313_REPORT_COUNT;i++)for(unsigned t=0;t<2;t++)
  snprintf(names[i][t],sizeof(names[i][t]),"%s-%04u.json%s",stem[i],tick,t?".tmp":"");
 /* Single-thread synchronous diagnostic only. No reconfiguration API. */
}
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
void b313_slice_sequence_frame(unsigned current,bool select)
{
 initialize();if(!b313_sequence_enabled()&&!b313_recovery_enabled())return;
 tick=UINT_MAX;phase=3;top=0;
 if(select&&((b313_recovery_enabled()&&current>=(b313_conservative_enabled()?408u:409u)&&current<=411)||(!b313_recovery_enabled()&&current>=408&&current<=410))){tick=current;phase=current<410?1:2;top=(int)current-307;}
 static const char *const stem[B313_REPORT_COUNT]={"native-writer-observer","building313-native-scope","building313-identity","building313-sample-tags","building313-precommit","building313-final-proof","building313-v6-locked-prefix","building313-v6-selected-transaction"};
 for(unsigned i=0;i<B313_REPORT_COUNT;i++)for(unsigned t=0;t<2;t++)
  snprintf(names[i][t],sizeof(names[i][t]),"%s-%04u.json%s",stem[i],tick,t?".tmp":"");
}
#endif
/* Independent read-only414 binding, never changes recovery_write_tick. */
void b313_slice_tail414_select(void)
{
 initialize();if(!b313_tail414_probe_tick(414))return;
 tick=414;phase=0;top=107;
 static const char *const stem[B313_REPORT_COUNT]={"native-writer-observer","building313-native-scope","building313-identity","building313-sample-tags","building313-precommit","building313-final-proof","building313-v6-locked-prefix","building313-v6-selected-transaction"};
 for(unsigned i=0;i<B313_REPORT_COUNT;i++)for(unsigned t=0;t<2;t++)snprintf(names[i][t],sizeof(names[i][t]),"%s-%04u.json%s",stem[i],tick,t?".tmp":"");
}
unsigned b313_slice_tick(void){initialize();return tick;}
unsigned b313_slice_phase(void){initialize();return phase;}
int b313_slice_top(void){initialize();return top;}
const char *b313_slice_payload_sha(void)
{
 initialize();static const char *const hashes[]={B313_V6_PHASE0_SHA256,B313_V6_PHASE1_SHA256,B313_V6_PHASE2_SHA256};
 return phase<3?hashes[phase]:NULL;
}
const char *b313_slice_path(unsigned report,bool temporary)
{initialize();return report<B313_REPORT_COUNT?names[report][temporary?1:0]:NULL;}
#else
typedef int b313_v6_slice_disabled_translation_unit;
#endif
