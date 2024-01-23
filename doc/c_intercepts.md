
# Using C for Intercepts

In addition, to using python for intercepts.  HALucinator can use C code for intercepting
and replacing code in the firmware.  This provides higher performance, but has its own
set of restrictions as the code executes in the emulator and thus has more constrained
access to host system resources.

This is achieved by compiling a bare-metal file and injecting it in the emulated machine.
Typically, memory not present in the physical machine is added so it will not conflict
with the original firmware.  This program is refered to as an elf program.  Currenltly,
this has only been used on bare-metal arm systems executing from physical memory.


## Executing an Elf Program


HALucinator has the ability to inject and execute an ELF program. On `exit` of the
elf program (or other specified function), execution will move to the entry point
defined in the configuration file.

Throughout this documentation two programs are considered. The first is the elf
program.  This is a program you likely compiled and want use to help analyze/
re-host another binary (the firmware).
Functions from the elf program can be used to replace functions in the firmware
by rewriting instructions in the firmware's memory to branch to the instructions
provided by the elf program. This overwrites the original function.

Its config file entry looks like the below with `(default)<type>` used and comment
to describe its function. In the future HALucinator may be extended to allow
injecting multiple elfs and executing them in sequence

```yaml
elf_program:
  name:  (None)<str>    #  Required, used to reference symbols from the elf program
                        #  in normal intercepts

  build: {cmd: (None)<str>, dir: (None)<str>, module_relative: (None)<str>}
          # Optional: If specified the cmd: will be executed from dir.
          # dir is relative to the directory of this config
          # If module_relative is not None the string  will be used to import
          # a python module and dir will relative to the directory of that module.

  elf: main.elf  # Path to the elf file (if full path give it is used/else is
                 # assumed to be relative to location of this file

  elf_module_relative: (None)<str>  # The full path for a python module that the
                                    # elf file should be loaded from

  execute_before: (True)<bool>      # This program should execute before the
                                    # entry point specified in config file

  exit_function: (exit)<str>        # Symbol when executed, execution should be
                                    # redirected to entry_ point

  intercepts:                       # Optional, list of intercepts
    - handler: <str>                # Name of the function to redirect execution to
      symbol:  <str>                # Either symbol/addr is required.  Specifies place
      addr: <int>                   # in firmware to be redirected to handler
      options: <arch specific>      # Optional passed to the rewriter to specify
                                    # for example could be use to specify arm/thumb mode
```

For an example see `src/halucinator/elf_program`


## Theory of operation

When the config file is parsed.  The build command if provided will be executed
to rebuild the program.  If it compiles successfully it will be injected into
the machine and its intercepts put in place by rewriting the firmware in QEMU's
memory (files on disk are unmodified).
It does the following.  It inspects the elf file and uses its segments to try
and infer the required memory spaces for the program to run. Currently,
stack space must be manually added.  It adds these to
the machine's memory if they do not conflict with existing memory. If it conflicts
an error is thrown. It also loads
the symbols from the elf into the configuration, but prefixes them with $<name>$<symbol>
where <name> is the value given to the elf_program entry.

After the qemu machine is created it loads any `PT_LOAD` segments into its
memory.  It then rewrites the memory to place branches at the places designated
by the intercepts symbol/addr value to its value for handler. It then rewrites
the `exit_function` to branch to the `entry_point`.

##  Setting python intercepts on the elf_program.

Regular python intercepts can be set on the `elf_program` by referencing either
its address, or using `$<name>$<symbol>` where `<name>` is the value given to the
`elf_program` name entry.  For example, the below uses
a python handler to handle the `_write` function for an `elf_program` with name
`program_1`.  As a note this particular intercept allows stdio etc to
write to the console enabling printf style debugging of your injected
`elf_program`.

```yaml
intercepts:
  - class: halucinator.bp_handlers.generic.newlib_syscalls.NewLibSysCalls
    function: _write
    symbol: $program_1$_write
```

## Calling functions in the original firmware

Functions in the original firmare can be called from the elf program by exporting
calling stubs and data types from a Ghidra project.  The `ghidra_scripts/export_calling_stubs.py`
will export a `.h` and `.c` file that can be used during compilation.  Depending on your
project there may be some conflicts with the types between Ghidra's stdlib defs and
your compilers.

##  Examples using C programs

Some examples of building bare-metal programs can be found in `test/qemu_tests`.  These can
server as templates for building C programs that are used to replace code in a firmware.