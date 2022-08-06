# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

from collections import defaultdict

import yaml

from halucinator.util.elf_sym_hal_getter import build_addr_to_sym_lookup


def get_names_for_addrs(stats_file, binary):

    with open(stats_file, "rb") as infile:
        stats = yaml.safe_load(infile)

    sym_lut = build_addr_to_sym_lookup(binary)

    funcs = defaultdict(list)
    for addr_set in stats["MMIO_addr_pc"]:
        mmio_addr, pc_addr, d = addr_set.split(",")
        pc_addr = int(pc_addr, 16)
        if pc_addr in sym_lut:
            function_name = sym_lut[pc_addr].name
            funcs[function_name].append(mmio_addr)
        else:
            funcs["$unknown_function"].append(mmio_addr)

    for func, data in list(funcs.items()):
        print("%s : %s" % (func, str(data)))


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("-s", "--stats", required=True, help="stats.yaml file from QEMU run")
    p.add_argument(
        "-b",
        "--bin",
        required=False,
        default=None,
        help=(
            "Elf file to get symbols from. If provided will"
            + " attempt to map addresses to function names"
        ),
    )

    args = p.parse_args()
    get_names_for_addrs(args.stats, args.bin)
