# Large Parameter Test

This tests HALucinators ability to generate function calls with large parameters.

The C file contains functions with 4, 5 and 10 parameters and function called
`write_int`.  Each of these functions calls `write_int` with each of its parameters.

The `ParameterTest` in `large_parameters_call.py` intercepts execution of run
test and then generates a chain of calls to `four_parameters`, `five_parameters`,
followed by `ten_parameters`.  Each call is done with a state variable and
`write_int` captures the parameters for each call.  In addition the stack pointer
is checked before and after each call to ensure it is properly preserved.
On exit the parameters captured for each call are compared to expected values.