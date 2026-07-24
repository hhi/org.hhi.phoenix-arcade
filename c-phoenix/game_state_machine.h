#ifndef GAME_STATE_MACHINE_H
#define GAME_STATE_MACHINE_H

#include "phoenix_state.h"

/* 
 * Executes the current game state logic.
 * Corresponds to GameStateMachine at 0x0400 in the original ROM.
 */
void game_state_machine(void);

#endif // GAME_STATE_MACHINE_H
