
## Layout of the drivers directory

Directories in this directory should follow this convention for both C and header files.
The `src` and `include` should mirror each other.

### QEMU Directory

The `qemu` directory contains drivers and their associated headers for drivers for qemu devices.
The directories should mirror the directories in qemu using the same names, and the 
names of the files should be the names used to instantiate the device on qemu's command line or
the `qemu_name` used in memory config files.  Underscores should replace `-` in the names. 
For example,  the `virtio-net-device` would be in in `qemu/net/virt_net_device.(c|h)`.


### RTOS/HAL directories

The `src` and `include` directories will also have OS/RTOS/HAL directories where intercepts are
specified.  Files with in the directory should be named to enable readily identify the API being 
targeted and the driver they are mapping to.(eg sysClk_2_sp804.c) They may directly call qemu 
drivers.  Functions names should be such that they clearly identify the targeted method they intend 
to intercept.


### Interfaces Headers

In the `include` there are special files (e.g. `qemu/ZZ_interface.h`) where ZZ is a device or 
capability (e.g, net, sema) the OS provides.  These define interface between qemu drivers and 
OS/HAL. Anytime a driver calls out to the OS it should use a function defined in an interface file. 
There is no src file for this instead each OS/HAL should define `xx_DEV_interface.c` files `xx` 
identifies the RTOS/HAL (e.g. vxworks). That implements these functions.  These are function that 
the driver calls to obtain needed OS support.