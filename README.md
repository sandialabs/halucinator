# HALucinator - Firmware rehosting through abstraction layer modeling.

## Setup in a Docker


Clone this repo and submodules for avatar2 and qemu
```
git clone <this repo>
git submodule update --init
```
A recursive clone can be done, but QEMU will then pull a lot of submodules that may not be needed.
QEMU's build process will pull the needed modules

Then run
```
docker build -t halucinator ./
docker run --name halucinator --rm -i -t halucinator bash
#Inside Docker container run
hal_dev_uart -i=1073811456
```
Building the docker may take a while time

In separate terminal run
```
docker exec -it halucinator bash
#Inside docker container run
./test/STM32/example/run.sh
```

You will eventually see in both terminals messages containing
```
 ****UART-Hyperterminal communication based on IT ****
 Enter 10 characters using keyboard :
```

Enter 10 Characters in the first terminal running `hal_dev_uart` press enter
should then see text echoed followed by.

```txt
 Example Finished
```


## Setup in Virtual Environment

Note:  This has been lightly tested on 20.04 and 22.04

1.  Install dependencies using `./install_deps.sh`

1.  Create and activate a python3 virtual environment (You can use virtualmachine
    wrapper but it is not required).  You often have to restart you terminal
    after installing virutalmachine wrapper for below to work
    ```
       mkvirtualenv -p `which python3` halucinator
    ```
    If (halucinator) is not in your prompt use `workon halucinator`

    Note: You may have to manually configure virtualenvwrapper. Or build you virtual environment using you preferred method
    ```bash
        pip3 install virtualenvwrapper
    ```
    Then add to `~/.bashrc` using your favorite editor and then run
    `source ~/.bashrc`.  Replace `your username` in below

    ```bash
    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
    export WORKON_HOME=$HOME/.virtualenvs
    export VIRTUALENVWRAPPER_VIRTUALENV=/home/<your username>/.local/bin/virtualenv
    source ~/.local/bin/virtualenvwrapper.sh
    ```

Get the repo and its immediate submodules
```
git clone <this repo>
git submodule update --init
```

Activate you virtual environment
```
workon halucinator
./setup.sh
```

1.  Simlink gdb-multiarch to arm-none-eabi-gdb
    If you don't have arm-none-eabi-gdb on your path symlink gdb-multiarch to it.
    It which was installed in step 1.  Just symlink it to `arm-none-eabi-gdb`

    ```bash
    sudo ln /usr/bin/gdb-multiarch /usr/bin/arm-none-eabi-gdb
    ```

### Note on setting HALUCINATOR_QEMU_*

You can override the QEMU that is used by HALucinator setting

```sh
export HALUCINATOR_QEMU_ARM=<full path to your qemu-system-arm>
export HALUCINATOR_QEMU_ARM64=<full path to your qemu-system-aarch64>
export HALUCINATOR_QEMU_POWERPC=<>
```

If using virtual environments thes can be set in the $VIRTUAL_ENV/bin/postactivate and
removed in $VIRTUAL_ENV/bin/predeactivate

## Running

Running Halucinator requires a configuration file that lists the functions to
intercept and the handler to be called on that interception. These are usually split
across three files for portability.  The files are a memory file that
describes the memory layout, an intercept file that describes what to intercept
and a symbol/address file that maps addresses to symbol names.  Internally, HALucinator
concatenates these configs into one config with the last taking precidence. See the Config
File section below for full details

All of these commands assume you are in your halucinator virtual environment

```sh
halucinator  -c=<memory_file.yaml> -c=<intercept_file.yaml> -c=<address_file.yaml>
```

## Running an Example



###  STM32F469I Uart Example

To give an idea how to use Halucinator an example is provided in `test/STM32/example`.

#### Setup
Note: This was done prior and the files are in the repo in `test/STM/example`.
If you just want to run the example without building it just go to Running UART Example below.

This procedure should be followed for other binaries.
In list below after the colon (:) denotes the file/cmd .


2. Copy binary to a dir of you choice and cd to it:  `test/STM32/example`
3. Create binary file: `<halucinator_repo_root>/src/tools/make_bin.sh Uart_Hyperterminal_IT_O0.elf` creates `Uart_Hyperterminal_IT_O0.elf.bin`
4. Create Memory Layout (specifies memory map of chip): `Uart_Hyperterminal_IT_O0_memory.yaml`
5. Create Address File (maps function names to address): `Uart_Hyperterminal_IT_O0_addrs.yaml`
6. Create Intercept File (defines functions to intercept and what handler to use for it): `Uart_Hyperterminal_IT_O0_config.yaml`
7. (Optional) create shell script to run it: `run.sh`

Note: Symbols used in the address file can be created from an elf file with symbols
using `hal_make_addrs` This requires installing angr in halucinator's virtual environment.
This was used to create `Uart_Hyperterminal_IT_O0_addrs.yaml`

To use it the first time you would. Install angr (e.g. `pip install angr` from
the halucinator virtual environment)

```sh
hal_make_addrs -b <path to elf file>
```

#### Running UART Example

Start the UART Peripheral device,  this a script that will subscribe to the Uart
on the peripheral server and enable interacting with it.

```bash
hal_dev_uart -i=1073811456
```

In separate terminal start halucinator with the firmware.

```bash
workon halucinator
<halucinator_repo_root>$./halucinator -c=test/STM32/example/Uart_Hyperterminal_IT_O0_config.yaml \
  -c=test/STM32/example/Uart_Hyperterminal_IT_O0_addrs.yaml \
  -c=test/STM32/example/Uart_Hyperterminal_IT_O0_memory.yaml --log_blocks -n Uart_Example

or
<halucinator_repo_root>& test/STM32/example/run.sh
```
Note the --log_blocks and -n are optional.

You will eventually see in both terminals messages containing
```
 ****UART-Hyperterminal communication based on IT ****
 Enter 10 characters using keyboard :
```

Enter 10 Characters in the first terminal running `hal_dev_uart` press enter
should then see text echoed followed by.

```txt
 Example Finished
```

#### Stopping

Press `ctrl-c`. If for some reason this doesn't work kill it with `ctrl-z`
and `kill %`, or `killall -9 halucinator`

Logs are kept in the `tmp/<value of -n option>`. e.g `tmp/Uart_Example/`

## Config file

How the emulation is performed is controlled by a yaml config file.  It is passed
in using a the -c flag, which can be repeated with the config file being appended
and the later files overwriting any collisions from previous file.  The config
is specified as follows.  Default field values are in () and types are in <>

```yaml
machine:   # Optional, describes qemu machine used in avatar entry optional defaults in ()
           # if never specified default settings as below are used.
  arch: (cortex-m3)<str>,
  cpu_model: (cortex-m3)<str>,
  entry_addr: (None)<int>,  # Initial value to pc reg. Obtained from 0x0000_0004
                        # of memory named init_mem if it exists else memory
                        # named flash
  init_sp: (None)<int>,     # Initial value for sp reg, Obtained from 0x0000_0000
                        # of memory named init_mem if it exists else memory
                        # named flash
  gdb_exe: ('arm-none-eabi-gdb')<path> # Path to gdb to use


memories:  #List of the memories to add to the machine
  - name: <str>,       # Required
    base_addr:  <int>, # Required
    size: <int>,       # Required
    perimissions: (rwx)<r--|rw-|r-x>, # Optional
    file: filename<path>   # Optional Filename to populate memory with, use full path or
                      # path relative to this config file, blank memory used if not specified
    emulate: class<AvatarPeripheral subclass>    # Class to emulate memory

peripherals:  # Optional, A list of memories, except emulate field required

intercepts:  # Optional, list of intercepts to places
  - class:  <BPHandler subclass>,  # Required use full import path
    function: <str>     # Required: Function name in @bp_handler([]) used to
                        #   determine class method used to handle this intercept
    addr: (from symbols)<int>  # Optional, Address of where to place this intercept,
                               # generally recommend not setting this value, but
                               # instead setting symbol and adding entry to
                               # symbols for this makes config files more portable
    symbol: (Value of function)<str>  # Optional, Symbol name use to determine address
    class_args: ({})<dict>  # Optional dictionary of args to pass to class's
                       # __init__ method, keys are parameter names
    registration_args: ({})<dict>  # Optional: Arguments passed to register_handler
                              # method when adding this method
    run_once: (false)<bool> # Optional: Set to true if only want intercept to run once
    watchpoint: (false)<bool> # Optional: Set to true if this is a memory watch point

symbols:  # Optional, dictionary mapping addresses to symbol names, used to
          # determine addresses for symbol values in intercepts
  addr0<int>: symbol_name<str>
  addr1<int>: symbol1_name<str>

elf_program:  # For more info on this section see doc/c_intercepts.md
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

options: # Optional, Key:Value pairs you want accessible during emulation

```

The symbols in the config can also be specified using one or more symbols files
passed in using -s. This is a csv file each line defining a symbol as shown below

```csv
symbol_name<str>, start_addr<int>, last_addr<int>
```