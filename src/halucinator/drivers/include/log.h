#include <stdio.h>

#define ERROR_LEVEL 10
#define WARNING_LEVEL 20
#define INFO_LEVEL 30
#define DEBUG_LEVEL 40

#ifndef LOG_LEVEL
#define LOG_LEVEL DEBUG_LEVEL
#endif

#define LOG_ERROR(...)                                     \
    do {                                                   \
        if (LOG_LEVEL >= ERROR_LEVEL) {                    \
            printf("ERROR| %s:%i | ", __FILE__, __LINE__); \
            printf(__VA_ARGS__);                           \
        }                                                  \
    } while (0)

#define LOG_INFO(...)                                     \
    do {                                                  \
        if (LOG_LEVEL >= INFO_LEVEL) {                    \
            printf("INFO| %s:%i | ", __FILE__, __LINE__); \
            printf(__VA_ARGS__);                          \
        }                                                 \
    } while (0)

#define LOG_WARNING(...)                                     \
    do {                                                     \
        if (LOG_LEVEL >= WARNING_LEVEL) {                    \
            printf("WARNING| %s:%i | ", __FILE__, __LINE__); \
            printf(__VA_ARGS__);                             \
        }                                                    \
    } while (0)

#define LOG_DEBUG(...)                                     \
    do {                                                   \
        if (LOG_LEVEL >= DEBUG_LEVEL) {                    \
            printf("DEBUG| %s:%i | ", __FILE__, __LINE__); \
            printf(__VA_ARGS__);                           \
        }                                                  \
    } while (0)
