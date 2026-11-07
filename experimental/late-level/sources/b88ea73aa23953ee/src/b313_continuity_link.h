#ifndef B313_CONTINUITY_LINK_H
#define B313_CONTINUITY_LINK_H
#include "building313_identity.h"
/* Observations only. This interface cannot grant or restore a renderer lease. */
#define BCO_REPORT_ANCHOR409 5u
typedef struct {
 bool independent_requested,configuration_valid,configuration_conflict;
 bool birth_source_observed,anchor_observed,anchor_snapshot_saved,anchor_report_published;
 uint64_t birth_scene,birth_group,birth_serial,anchor_serial,anchor_preparation;
 unsigned anchor_tick;
} BcoLinkStatus;
bool bco_link_independent(void);
BcoLinkStatus bco_link_status(void);
void bco_link_anchor409(unsigned tick,uint64_t preparation,const B313Group *group,bool snapshot_saved,bool report_published);
#endif
