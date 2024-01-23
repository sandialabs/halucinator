# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
"""
This is the halucinator entry point
"""

from argparse import ArgumentParser
import logging
from multiprocessing import Lock
import threading
import os
import sys
import argparse
import signal

from avatar2 import Avatar
from avatar2.peripherals.avatar_peripheral import AvatarPeripheral
from .peripheral_models import generic as peripheral_emulators

from .bp_handlers import intercepts
from .peripheral_models import peripheral_server as periph_server
from .util.profile_hals import State_Recorder
from .util import cortex_m_helpers as CM_helpers
from . import hal_stats
from . import hal_log, hal_config


log = logging.getLogger(__name__)
hal_log.setLogConfig()


PATCH_MEMORY_SIZE = 4096
INTERCEPT_RETURN_INSTR_ADDR = 0x20000000 - PATCH_MEMORY_SIZE
__HAL_EXIT_CODE = 0


def get_qemu_target(
    name,
    config,
    firmware=None,
    log_basic_blocks=False,
    gdb_port=1234,
    singlestep=False,
    qemu_args=None,
):  # pylint: disable=too-many-arguments
    """
    Instantiates QEMU instance that is used to run firmware using Avatar
    """
    outdir = os.path.join("tmp", name)
    hal_stats.set_filename(outdir + "/stats.yaml")

    # Get info from config
    avatar_arch = config.machine.get_avatar_arch()

    avatar = Avatar(arch=avatar_arch, output_directory=outdir)
    avatar.config = config
    avatar.cpu_model = config.machine.cpu_model

    qemu_path = config.machine.get_qemu_path()
    log.info("GDB_PORT: %s", gdb_port)
    log.info("QEMU Path: %s", qemu_path)

    qemu_target = config.machine.get_qemu_target()
    qemu = avatar.add_target(
        qemu_target,
        machine=config.machine.machine,
        cpu_model=config.machine.cpu_model,
        gdb_executable=config.machine.gdb_exe,
        gdb_port=gdb_port,
        qmp_port=gdb_port + 1,
        firmware=firmware,
        executable=qemu_path,
        entry_address=config.machine.entry_addr,
        name=name,
        qmp_unix_socket=f"/tmp/{name}-qmp",
    )

    if log_basic_blocks == "irq":
        qemu.additional_args = [
            "-d",
            "in_asm,exec,int,cpu,guest_errors,avatar,trace:nvic*",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks == "regs":
        qemu.additional_args = [
            "-d",
            "in_asm,exec,cpu",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks == "regs-nochain":
        qemu.additional_args = [
            "-d",
            "in_asm,exec,cpu,nochain",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks == "exec":
        qemu.additional_args = [
            "-d",
            "exec",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks == "trace-nochain":
        qemu.additional_args = [
            "-d",
            "in_asm,exec,nochain",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks == "trace":
        qemu.additional_args = [
            "-d",
            "in_asm,exec",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]
    elif log_basic_blocks:
        qemu.additional_args = [
            "-d",
            "in_asm",
            "-D",
            os.path.join(outdir, "qemu_asm.log"),
        ]

    if singlestep:
        qemu.additional_args.append("-singlestep")
    if qemu_args is not None:
        qemu.additional_args.extend(qemu_args.split())

    return avatar, qemu


def setup_memory(avatar, memory, record_memories=None):
    """
    Sets up memory regions for the emualted devices
    Args:
        avatar(Avatar):
        name(str):    Name for the memory
        memory(HALMemoryConfigdict):
    """
    if memory.emulate is not None:
        emulate = getattr(peripheral_emulators, memory.emulate)
    else:
        emulate = None
    log.info(
        "Adding Memory: %s Addr: 0x%08x Size: 0x%08x",
        memory.name,
        memory.base_addr,
        memory.size,
    )
    avatar.add_memory_range(
        memory.base_addr,
        memory.size,
        name=memory.name,
        file=memory.file,
        permissions=memory.permissions,
        emulate=emulate,
        qemu_name=memory.qemu_name,
        irq=memory.irq_config,
        qemu_properties=memory.properties,
    )

    if record_memories is not None:
        if "w" in memory.permissions:
            record_memories.append((memory.base_addr, memory.size))


def fix_cortex_m_thumb_bit(config):
    """
    Fixes and bug in QEMU that makes so thumb bit doesn't get set on CPSR. Manually set it up
    """

    # Bug in QEMU about init stack pointer/entry point this works around
    if config.machine.arch == "cortex-m3":
        mem = (
            config.memories["init_mem"]
            if "init_mem" in config.memories
            else config.memories["flash"]
        )
        if mem is not None and mem.file is not None:
            config.machine.init_sp, entry_addr = CM_helpers.get_sp_and_entry(mem.file)
        # Only use the discoved entry point if one not explicitly set
        if config.machine.entry_addr is None:
            config.machine.entry_addr = entry_addr


def register_intercepts(config, avatar, qemu):
    """
    Create and registers the intercepts, must be called after avatar.init_targets()
    """
    # Instantiate the BP Handler Classes
    added_classes = []
    for intercept in config.intercepts:
        bp_cls = intercepts.get_bp_handler(intercept)
        if issubclass(bp_cls.__class__, AvatarPeripheral):
            name, addr, size, per = bp_cls.get_mmio_info()
            if bp_cls not in added_classes:
                log.info(
                    "Adding Memory Region for %s, (Name: %s, Addr: %s, Size:%s)",
                    bp_cls.__class__.__name__,
                    name,
                    hex(addr),
                    hex(size),
                )
                avatar.add_memory_range(
                    addr,
                    size,
                    name=name,
                    permissions=per,
                    forwarded=True,
                    forwarded_to=bp_cls,
                )
                added_classes.append(bp_cls)

    # Register Avatar watchman for Break points and watch points
    avatar.watchmen.add_watchman(
        "BreakpointHit", "before", intercepts.interceptor, is_async=True
    )
    avatar.watchmen.add_watchman(
        "WatchpointHit", "before", intercepts.interceptor, is_async=True
    )

    # Register the BP handlers
    for intercept in config.intercepts:
        if intercept.bp_addr is not None:
            log.info("Registering Intercept: %s", intercept)
            intercepts.register_bp_handler(qemu, intercept)


def emulate_binary(
    config,
    target_name=None,
    log_basic_blocks=None,
    rx_port=5555,
    tx_port=5556,
    gdb_port=1234,
    elf_file=None,
    db_name=None,
    singlestep=False,
    qemu_args=None,
    gdb_server_port=9999,
    print_qemu_command=None,
):  # pylint: disable=too-many-arguments,too-many-locals
    """
    Start emulation of the firmware
    """

    avatar, qemu = get_qemu_target(
        target_name,
        config,
        log_basic_blocks=log_basic_blocks,
        gdb_port=gdb_port,
        singlestep=singlestep,
        qemu_args=qemu_args,
    )
    if print_qemu_command:
        print("QEMU Command")
        print(" ".join(qemu.assemble_cmd_line()))
        sys.exit(0)

    if "remove_bitband" in config.options and config.options["remove_bitband"]:
        log.info("Removing Bitband")
        qemu.remove_bitband = True

    # Setup Memory Regions
    record_memories = []
    for memory in config.memories.values():
        setup_memory(avatar, memory, record_memories)

    # Add recorder to avatar
    # Used for debugging peripherals
    if elf_file is not None:
        if db_name is None:
            db_name = ".".join(
                (os.path.splitext(elf_file)[0], str(target_name), "sqlite")
            )

        avatar.recorder = State_Recorder(db_name, qemu, record_memories, elf_file)
    else:
        avatar.recorder = None

    qemu.gdb_port = gdb_port
    avatar.config = config
    log.info("Initializing Avatar Targets")
    avatar.init_targets()

    if gdb_server_port is not None and gdb_server_port >= 0:
        avatar.load_plugin("gdbserver")
        # pylint: disable=no-member
        avatar.spawn_gdb_server(qemu, gdb_server_port, do_forwarding=False)

    register_intercepts(config, avatar, qemu)

    # Do post qemu creation initialization
    config.initialize_target(qemu)

    # Work around Avatar-QEMU's improper init of Cortex-M3
    if config.machine.arch == "cortex-m3":
        qemu.regs.cpsr |= 0x20  # Make sure the thumb bit is set
        qemu.regs.sp = config.machine.init_sp  # Set SP as Qemu doesn't init correctly
        qemu.set_vector_table_base(config.machine.vector_base)

    _start_execution(avatar, qemu, rx_port, tx_port, gdb_server_port)


def _start_execution(avatar, qemu, rx_addr, tx_addr, gdb_server_port):
    """
    Starts the actual execution of qemu,
    peripheral server with handlers to enable clean
    exiting
    """
    # Emulate the Binary
    periph_server.start(rx_addr, tx_addr, qemu)

    # Removed because of issues in python 3.10 which is default in ubuntu 22.04
    # exit_code_lock = Lock()

    def halucinator_shutdown(exit_code):
        """
        Perform a clean shutdown of halucinator
        """
        global __HAL_EXIT_CODE  # pylint: disable=global-statement
        # with exit_code_lock:

        if threading.current_thread() != threading.main_thread():
            # Main thread must kill everything
            signal.raise_signal(signal.SIGINT)
        else:
            __HAL_EXIT_CODE = exit_code
            avatar.stop()
            avatar.shutdown()
            periph_server.stop()
            sys.exit(__HAL_EXIT_CODE)

    def int_signal_handler(sig, frame):  # pylint: disable=unused-argument
        print(f"Halucinator Exiting with status {__HAL_EXIT_CODE}!")
        halucinator_shutdown(__HAL_EXIT_CODE)

    signal.signal(signal.SIGINT, int_signal_handler)
    qemu.halucinator_shutdown = halucinator_shutdown
    log.info("Letting QEMU Run")

    if gdb_server_port is not None:
        print(f"GDB Server Running on localhost:{gdb_server_port}")
        print("Connect GDB and continue to run")
    else:
        qemu.cont()
    try:
        periph_server.run_server()  # Blocks Forever
    except KeyboardInterrupt:
        pass
    halucinator_shutdown(0)


def main():
    """
    Halucinator Main
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        action="append",
        required=True,
        help="Config file(s) used to run emulation files are "
        "appended to each other with later files taking precedence",
    )
    parser.add_argument(
        "-s",
        "--symbols",
        action="append",
        default=[],
        help="CSV file with each row having symbol, first_addr, last_addr",
    )
    parser.add_argument(
        "--log_blocks",
        default=False,
        const=True,
        nargs="?",
        help="Enables QEMU's logging of basic blocks, "
        "options [irq, regs, exec, trace, trace-nochain]",
    )
    parser.add_argument(
        "--singlestep",
        default=False,
        const=True,
        nargs="?",
        help="Enables QEMU single stepping instructions",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="HALucinator",
        help="Name of target for avatar, used for logging",
    )
    parser.add_argument(
        "-r",
        "--rx_port",
        default=5555,
        type=int,
        help="Port number to receive zmq messages for IO on",
    )
    parser.add_argument(
        "-t",
        "--tx_port",
        default=5556,
        type=int,
        help="Port number to send IO messages via zmq",
    )
    parser.add_argument("-p", "--gdb_port", default=1234, type=int, help="GDB_Port")
    parser.add_argument(
        "-d",
        "--gdb_server_port",
        default=None,
        type=int,
        help="Port to run GDB Server port",
    )
    parser.add_argument(
        "-e", "--elf", default=None, help="Elf file, required to use recorder"
    )
    parser.add_argument(
        "--print_qemu_command",
        action="store_true",
        default=None,
        help="Just print the QEMU Command",
    )
    parser.add_argument(
        "-q",
        "--qemu_args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Additional arguments for QEMU",
    )

    args = parser.parse_args()

    # Build configuration
    config = hal_config.HalucinatorConfig()
    for conf_file in args.config:
        log.info("Parsing config file: %s", conf_file)
        config.add_yaml(conf_file)

    for csv_file in args.symbols:
        log.info("Parsing csv symbol file: %s", csv_file)
        config.add_csv_symbols(csv_file)

    if not config.prepare_and_validate():
        log.error("Config invalid")
        sys.exit(-1)

    if config.elf_program is not None:
        args.qemu_args.append(f"-device loader,file={config.elf_program.elf_filename}")

    qemu_args = None
    if args.qemu_args:
        qemu_args = " ".join(args.qemu_args)

    emulate_binary(
        config,
        args.name,
        args.log_blocks,
        args.rx_port,
        args.tx_port,
        elf_file=args.elf,
        gdb_port=args.gdb_port,
        singlestep=args.singlestep,
        qemu_args=qemu_args,
        gdb_server_port=args.gdb_server_port,
        print_qemu_command=args.print_qemu_command,
    )


if __name__ == "__main__":
    main()
