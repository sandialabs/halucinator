#ifndef __HALUCINATOR_H__
#define __HALUCINATOR_H__

#include "log.h"
#define INTERCEPT __attribute__((used))

#define UINT32_PTR_OFFSET(reg, offset) (uint32_t*)((uint32_t)reg + offset)
#define UINT16_PTR_OFFSET(reg, offset) (uint16_t*)((uint32_t)reg + offset)
#define UINT8_PTR_OFFSET(reg, offset) (uint8_t*)((uint32_t)reg + offset)
#endif