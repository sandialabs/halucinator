# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC 
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, 
# the U.S. Government retains certain rights in this software.

void run_test(){
    // Does nothing other than provide a function to intercept
}

int write_int(int p){
    // Just here so it can be intercepted and we grab the int
}

int test_end(){
    return;
}

/*
Will use halucinator to create a call to this
*/
int four_parameters(int one, int two, int three, int four){
    
    write_int(one);
    write_int(two);
    write_int(three);
    write_int(four);
}

/* 
Will use halucinator call function to create a call to this 
test five parameters
*/
int five_parameters(int one, int two, int three, int four, int five){
    write_int(one);
    write_int(two);
    write_int(three);
    write_int(four);
    write_int(five);
}


/* 
Will use halucinator call function to create a call to this 
test 10 parameters
*/
int ten_parameters(int one, int two, int three, int four, int five, 
                   int six, int seven, int eight, int nine, int ten){
    write_int(one);
    write_int(two);
    write_int(three);
    write_int(four);
    write_int(five);
    write_int(six);
    write_int(seven);
    write_int(eight);
    write_int(nine);
    write_int(ten);
}

int main(){

    // Use memcpy to make sure its in binary
    run_test();
    test_end();

}

void exit(int __status){
    while(1);
}