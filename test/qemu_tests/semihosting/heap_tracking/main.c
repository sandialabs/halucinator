#include <stdio.h>
#include <stdlib.h>

/*
This test

*/

#define MALLOC_SIZE 10
#define CALLOC_NUM 3
#define CALLOC_SIZE 8 // you also need to change the calloc buf type below
#define REALLOC_SIZE 20

#define TEST_MALLOC 1
#define TEST_CALLOC 1
#define TEST_REALLOC 1

#define TEST_DOUBLE_FREE 1
#define TEST_FREE_BEFORE_ALLOC 1

#define TEST_OVERFLOW 1
#define TEST_UNDERFLOW 1

int main()
{
    if (TEST_MALLOC) {
        printf("Malloc testing\n\r");
        char* buf;

        if (TEST_FREE_BEFORE_ALLOC) {
            free(buf);
        }
        buf = malloc(MALLOC_SIZE);
        printf("Buffer addr is %p\n", buf);

        //Test write whole buffer
        for (int i = 0; i < MALLOC_SIZE; ++i) {
            buf[i] = 'b';
        }

        //Check Buffer
        printf("Buffer contains: ");
        for (int i = 0; i < MALLOC_SIZE; ++i) {
            printf("%c", buf[i]);
        }
        printf("\n");

        if (TEST_OVERFLOW) {
            //Testing Overflow
            buf[MALLOC_SIZE] = 'O';
        }
        if (TEST_UNDERFLOW) {
            //Test underflow
            *(buf - 1) = 'U';
        }

        printf("Freeing buffer\n");
        free(buf);
        if (TEST_DOUBLE_FREE) {
            free(buf);
        }
    }

    if (TEST_CALLOC) {
        printf("calloc testing\n\r");
        double* calbuf;

        if (TEST_FREE_BEFORE_ALLOC) {
            free(calbuf);
        }

        calbuf = (double*)calloc(CALLOC_NUM, CALLOC_SIZE);

        //Test write whole buffer
        for (int i = 0; i < CALLOC_NUM; i++) {
            calbuf[i] = 'b';
        }

        //Check Buffer
        printf("Buffer contains: ");
        for (int i = 0; i < CALLOC_NUM; i++) {
            printf("%c", calbuf[i]);
        }
        printf("\n");

        if (TEST_OVERFLOW) {
            //Testing Overflow
            calbuf[CALLOC_NUM] = 'O';
        }
        if (TEST_UNDERFLOW) {
            //Test underflow
            *(calbuf - 1) = 'U';
        }

        printf("freeing buffer\n\r");
        free(calbuf);
        if (TEST_DOUBLE_FREE) {
            free(calbuf);
        }
    }

    if (TEST_REALLOC) {
        printf("realloc testing\n\r");
        char* realbuf;

        realbuf = malloc(MALLOC_SIZE);

        //Test write whole buffer
        for (int i = 0; i < MALLOC_SIZE; i++) {
            realbuf[i] = 'b';
        }

        //Check Buffer
        //printf("Buffer contains: ");
        for (int i = 0; i < MALLOC_SIZE; i++) {
            printf("%c", realbuf[i]);
        }
        printf("\n");

        realbuf = realloc(realbuf, REALLOC_SIZE);

        //Test write whole buffer
        for (int i = 0; i < REALLOC_SIZE; i++) {
            realbuf[i] = 'b';
        }

        //heck Buffer
        printf("Buffer contains: ");
        for (int i = 0; i < REALLOC_SIZE; i++) {
            printf("%c", realbuf[i]);
        }
        printf("\n");

        if (TEST_OVERFLOW) {
            //Testing Overflow
            realbuf[REALLOC_SIZE] = 'U';
        }

        if (TEST_UNDERFLOW) {
            //Test underflow
            *(realbuf - 1) = '0';
        }

        printf("freeing buffer\n\r");
        free(realbuf);
        if (TEST_DOUBLE_FREE) {
            free(realbuf);
        }
    }

    printf("Test Done press ctrl-c\n");
}
