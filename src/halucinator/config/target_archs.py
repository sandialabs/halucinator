"""
Archs specifies the halucinator specific configuration needed to support various
target architectures.
"""

import os

from avatar2 import ARM_CORTEX_M3, ARM, ARM64, PPC32, PPC_MPC8544DS
from halucinator.qemu_targets import (
    ARMQemuTarget,
    ARMv7mQemuTarget,
    ARM64QemuTarget,
    PowerPCQemuTarget,
)
import halucinator


_QEMU_DEFAULT_LOC = os.path.join(
    os.path.split(os.path.split(halucinator.__path__[0])[0])[0], "deps/build-qemu"
)


## To add a target to HALUCINATOR register it here
HALUCINATOR_TARGETS = {
    "cortex-m3": {
        "avatar_arch": ARM_CORTEX_M3,
        "qemu_target": ARMv7mQemuTarget,
        "qemu_env_var": "HALUCINATOR_QEMU_ARM",
        "qemu_default_path": os.path.join(
            _QEMU_DEFAULT_LOC, "arm-softmmu/qemu-system-arm"
        ),
    },
    "arm": {
        "avatar_arch": ARM,
        "qemu_target": ARMQemuTarget,
        "qemu_env_var": "HALUCINATOR_QEMU_ARM",
        "qemu_default_path": os.path.join(
            _QEMU_DEFAULT_LOC, "arm-softmmu/qemu-system-arm"
        ),
    },
    "arm64": {
        "avatar_arch": ARM64,
        "qemu_target": ARM64QemuTarget,
        "qemu_env_var": "HALUCINATOR_QEMU_ARM64",
        "qemu_default_path": os.path.join(
            _QEMU_DEFAULT_LOC, "aarch64-softmmu/qemu-system-aarch64"
        ),
    },
    "powerpc": {
        "avatar_arch": PPC32,
        "qemu_target": PowerPCQemuTarget,
        "qemu_env_var": "HALUCINATOR_QEMU_POWERPC",
        "qemu_default_path": os.path.join(
            _QEMU_DEFAULT_LOC, "ppc-softmmu/qemu-system-ppc"
        ),
    },
    "powerpc:MPC8XX": {
        "avatar_arch": PPC_MPC8544DS,
        "qemu_target": PowerPCQemuTarget,
        "qemu_env_var": "HALUCINATOR_QEMU_POWERPC",
        "qemu_default_path": os.path.join(
            _QEMU_DEFAULT_LOC, "ppc-softmmu/qemu-system-ppc"
        ),
    },
}
