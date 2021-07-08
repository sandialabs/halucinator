// Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC 
// (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, 
// the U.S. Government retains certain rights in this software.

#include <string.h>

char str_to_copy[] = "THIS IS THE STRING TO COPY";
char str_dest[sizeof(str_to_copy)];
void run_test(){
    // Does nothing other than provide a function to intercept
}

int test_end(){
    return;
}

int main(){

    // Use memcpy to make sure its in binary
    memcpy(str_dest, str_to_copy, sizeof(str_to_copy)); 
    run_test();
    test_end();

}

void exit(int __status){
    while(1);
}