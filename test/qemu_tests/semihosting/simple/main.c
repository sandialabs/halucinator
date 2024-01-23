#include <stdio.h>

/*
This test
Intercepts `_write` to save the output to a buffer and display to screen.

Inserts a call to insert_call on call entry test and then allows it to execute.
It also inserts a call at `insert_point` and allows execution to continue after.

The output should be
```
Inserted Function Executed\n
Entry Function Executed\n
Inserted Function Executed\n
Value of a: 11, Value of b: 20\n"
```

On exit the buffer from write is check to ensure it has proper value
There are also checks of stack/registers to ensure state is restored properly

*/

void insert_call(){
    printf("Inserted Function Executed\n");
}

void entry_call_test(){
    printf("Entry Function Executed\n");
}

int main(){
    int a,b;


    // Use memcpy to make sure its in binary
    printf("Insert Call Test Started\n");
    entry_call_test();
    a = 10;
    b = 20;
    a++;
    printf("Value of a: %i, Value of b: %i\n",a ,b);
}

void exit(int __status){
    while(1);
}