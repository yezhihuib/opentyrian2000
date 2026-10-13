#ifndef CASH50_ORIGINAL_UNIT_H
#define CASH50_ORIGINAL_UNIT_H
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef int16_t Sint16;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef Sint16 JE_integer;
typedef int8_t JE_shortint;
typedef Uint16 JE_word;
typedef Uint8 JE_byte;
typedef bool JE_boolean;
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
#define MAX_EXPLOSIONS 200
/* Original fields and types; SDL surface itself is deliberately opaque. */
typedef struct {size_t size; Uint8 *data;} Sprite2_array;
typedef struct SDL_Surface SDL_Surface;
#include "enemy_type.inc"
#include "enemy_num.inc"
#include "enemy_data_type.inc"
#include "explosion_type.inc"
#include "player_types.inc"
#include "event_type.inc"
#include "difficulty_type.inc"
extern struct JE_SingleEnemyType enemy[100];
extern JE_byte enemyAvail[100];
uint JE_makeEnemy(struct JE_SingleEnemyType *,Uint16,Sint16);
Sint16 JE_newEnemy(int,Uint16,Sint16);
extern JE_EnemyDatType enemyDat;
extern int difficultyLevel,superArcadeMode,totalEnemy;
extern Sprite2_array spriteSheet11,spriteSheet10,enemySpriteSheets[4];
extern JE_byte enemySpriteSheetIds[4];
enum {SA_NONE=0};
uint mt_rand(void);
#endif
