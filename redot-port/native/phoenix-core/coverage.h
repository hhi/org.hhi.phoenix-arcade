#ifndef COVERAGE_H
#define COVERAGE_H

#include <stdbool.h>
#include "phoenix_state.h"

void coverage_set_output_path(const char* path);
bool coverage_is_enabled(void);
void coverage_hit(const char* name);
void coverage_observe_frame(int frame, const PhoenixState* s);
void coverage_write_dump(void);

#endif
