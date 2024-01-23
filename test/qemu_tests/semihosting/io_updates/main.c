#include <stdint.h>
#include <stdio.h>
#include <unistd.h>

/*
This test intercepts the calls to read/write digital and analog and updated their valued

*/

#define NUM_DIGITAL 10
#define NUM_ANALOG 4
static float g_analog_values[NUM_ANALOG];
static uint8_t g_digital_values[NUM_DIGITAL];

/*
Gets the analog value
Return zero on success, -1 on failure
*/
int read_analog(uint32_t num, float* value)
{
    if (num < NUM_ANALOG) {
        *value = g_analog_values[num];
        return 0;
    }
    return -1;
}

/*
Writes the analog value
Return zero on success, -1 on failure
*/
int write_analog(uint32_t num, float value)
{
    if (num < NUM_ANALOG) {
        g_analog_values[num] = value;
        return 0;
    }
    return -1;
}

int write_digital(int num, uint8_t value)
{
    if (num < NUM_DIGITAL) {
        g_digital_values[num] = value ? 1 : 0;
        return 0;
    }
    return -1;
}

int read_digital(int num, uint8_t* value)
{
    if (num < NUM_DIGITAL) {
        *value = g_digital_values[num];
        return 0;
    }
    return -1;
}

int main()
{
    float analog_tmp = 0;
    uint8_t digital_tmp = 0;

    printf("Starting IO Test");

    while (1) {
        printf("Analog Values:");
        for (uint32_t i = 0; i < NUM_ANALOG; ++i) {
            read_analog(i, &analog_tmp);
            write_analog(i, analog_tmp);
            printf("    %i: %f\n", i, analog_tmp);
        }
        printf("\n");

        printf("Digital Values:\n");
        for (uint32_t i = 0; i < NUM_DIGITAL; ++i) {
            read_digital(i, &digital_tmp);
            write_digital(i, digital_tmp);

            printf("   %i: %i\n", i, digital_tmp);
        }
        printf("\n\n");
        sleep(2);
    }

    // Use memcpy to make sure its in binary
}

void exit(int __status)
{
    while (1)
        ;
}