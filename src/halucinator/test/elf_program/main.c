#include <stdio.h>
#include <sys/stat.h>

int non_zero_initalized = 3;
int zero_initalized = 0;

extern int _end;

void *_sbrk(int incr) {
  static unsigned char *heap = NULL;
  unsigned char *prev_heap;

  if (heap == NULL) {
    heap = (unsigned char *)&_end;
  }
  prev_heap = heap;

  heap += incr;

  return prev_heap;
}

int _close(int file) {
  return -1;
}

int _fstat(int file, struct stat *st) {
  st->st_mode = S_IFCHR;

  return 0;
}

int _isatty(int file) {
  return 1;
}

int _lseek(int file, int ptr, int dir) {
  return 0;
}

void _exit(int status) {
  while(1);
}

void _kill(int pid, int sig) {
  return;
}

int _getpid(void) {
  return -1;
}

int _write (int file, char * ptr, int len) {
  int written = 0;

  if ((file != 1) && (file != 2) && (file != 3)) {
    return -1;
  }

    return len;
}

int _read (int file, char * ptr, int len) {
  int read = 0;

  if (file != 0) {
    return -1;
  }

  return 0;
}

void check_call(){
    printf("Check_Call Called\n");
}

int main(){

    // Use memcpy to make sure its in binary
    if (non_zero_initalized == 0){
        printf("Non-zero initialized global failed %i\n", non_zero_initalized);
    }
    else{
        printf("Initialized global is not 0 %i\n", non_zero_initalized);
    }

        // Use memcpy to make sure its in binary
    if (zero_initalized  == 0){
        printf("Zero initialized global is zero %i\n", zero_initalized);
    }
    else{
        printf("Zero initialized global is not 0 %i\n", zero_initalized);
    }

    check_call();
}

void exit(int __status){
    while(1);
}
