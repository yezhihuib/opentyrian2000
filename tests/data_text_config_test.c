/* SPDX-License-Identifier: GPL-2.0-or-later */
#define _POSIX_C_SOURCE 200809L
#include "config.h"
#include "data_text.h"
#include "file.h"
#include "video.h"
#include "video_scale.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
bool load_opentyrian_config(void);
int fullscreen_display=-1;
ScalingMode scaling_mode=SCALE_INTEGER;
const char *const scaling_mode_names[ScalingMode_MAX]={"None","Integer","Fit","4:3"};
uint scaler;
const struct Scalers scalers[]={{640,400,NULL,NULL,"2x"},{1280,800,NULL,NULL,"4x"}};
void set_scaler_by_name(const char *name){scaler=!strcmp(name,"4x");}
bool set_scaling_mode_by_name(const char *name){for(int i=0;i<ScalingMode_MAX;++i)if(!strcmp(name,scaling_mode_names[i])){scaling_mode=(ScalingMode)i;return true;}return false;}
int main(int argc,char **argv){assert(argc==2);bool loaded=load_opentyrian_config();
 if(!strcmp(argv[1],"default")){assert(!loaded);assert(!strcmp(data_text_language(),"en"));assert(save_opentyrian_config());}
 else if(!strcmp(argv[1],"zh")){assert(loaded);assert(!strcmp(data_text_language(),"en"));assert(fullscreen_display==2 && scaler==1 && scaling_mode==SCALE_INTEGER);assert(keySettings[0]==SDL_SCANCODE_W && mouseSettings[0]==3);data_text_toggle();assert(!strcmp(data_text_language(),"zh-CN"));assert(save_opentyrian_config());}
 else if(!strcmp(argv[1],"read-zh")){assert(loaded);assert(!strcmp(data_text_language(),"zh-CN"));const char *v;ConfigSection *s=config_find_section(&opentyrian_config,"unrelated",NULL);assert(s && config_get_string_option(s,"preserve",&v) && !strcmp(v,"sentinel"));assert(fullscreen_display==2 && scaler==1 && scaling_mode==SCALE_INTEGER);assert(keySettings[0]==SDL_SCANCODE_W && mouseSettings[0]==3);data_text_toggle();assert(save_opentyrian_config());}
 else if(!strcmp(argv[1],"read-en")){assert(loaded);assert(!strcmp(data_text_language(),"en"));}
 else if(!strcmp(argv[1],"invalid")){assert(loaded);assert(!strcmp(data_text_language(),"en"));}
 else assert(0);
 config_deinit(&opentyrian_config);puts("Actual config load/save language persistence passed");return 0;}
