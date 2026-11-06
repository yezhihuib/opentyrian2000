#ifndef B313_CONTINUITY_REPORT_H
#define B313_CONTINUITY_REPORT_H
#include <stdbool.h>
#include <stdint.h>
enum BcoReportStage {BCO_REPORT_BEGIN=0,BCO_REPORT_BIRTH_PENDING=1,BCO_REPORT_BIRTH_CLOSED=2,BCO_REPORT_FIRST_FAILURE=3,BCO_REPORT_FINAL_RECEIPT=4};
enum BcoReportIo {BCO_IO_CLOCK=1,BCO_IO_ORDER=2,BCO_IO_OPEN=3,BCO_IO_STREAM=4,BCO_IO_WRITE=5,BCO_IO_FLUSH=6,BCO_IO_SYNC=7,BCO_IO_CLOSE=8,BCO_IO_PUBLISH=9,BCO_IO_CLEANUP=10,BCO_IO_REENTRY=11};
typedef struct {bool io_failed,io_error_known;unsigned io_stage,io_error,attempted_seq,published_seq,published_mask;uint64_t process_id,monotonic_sec,monotonic_nsec;} BcoReportStatus;
bool bco_report_emit(unsigned stage,unsigned tick,bool tick_known);
void bco_report_first_failure(void);
BcoReportStatus bco_report_status(void);
void bco_report_finish_mark(void);
void bco_report_at_halt(unsigned tick,unsigned code);
#endif
