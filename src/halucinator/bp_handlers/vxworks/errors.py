# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.

'''Module for error printing'''
import logging

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler

log = logging.getLogger(__name__)

errnos = {
    0x1: "EPERM",
    0x2: "ENOENT",
    0x3: "ESRCH",
    0x4: "EINTR",
    0x5: "EIO",
    0x6: "ENXIO",
    0x7: "E2BIG",
    0x8: "ENOEXEC",
    0x9: "EBADF",
    0xa: "ECHILD",
    0xb: "EAGAIN",
    0xc: "ENOMEM",
    0xd: "EACCES",
    0xe: "EFAULT",
    0xf: "ENOTEMPTY",
    0x10: "EBUSY",
    0x11: "EEXIST",
    0x12: "EXDEV",
    0x13: "ENODEV",
    0x14: "ENOTDIR",
    0x15: "EISDIR",
    0x16: "EINVAL",
    0x17: "ENFILE",
    0x18: "EMFILE",
    0x19: "ENOTTY",
    0x1a: "ENAMETOOLONG",
    0x1b: "EFBIG",
    0x1c: "ENOSPC",
    0x1d: "ESPIPE",
    0x1e: "EROFS",
    0x1f: "EMLINK",
    0x20: "EPIPE",
    0x21: "EDEADLK",
    0x22: "ENOLCK",
    0x23: "ENOTSUP",
    0x24: "EMSGSIZE",
    0x25: "EDOM",
    0x26: "ERANGE",
    0x28: "EDESTADDRREQ",
    0x29: "EPROTOTYPE",
    0x2a: "ENOPROTOOPT",
    0x2b: "EPROTONOSUPPORT",
    0x2c: "ESOCKTNOSUPPORT",
    0x2d: "EOPNOTSUPP",
    0x2e: "EPFNOSUPPORT",
    0x2f: "EAFNOSUPPORT",
    0x30: "EADDRINUSE",
    0x31: "EADDRNOTAVAIL",
    0x32: "ENOTSOCK",
    0x33: "ENETUNREACH",
    0x34: "ENETRESET",
    0x35: "ECONNABORTED",
    0x36: "ECONNRESET",
    0x37: "ENOBUFS",
    0x38: "EISCONN",
    0x39: "ENOTCONN",
    0x3a: "ESHUTDOWN",
    0x3b: "ETOOMANYREFS",
    0x3c: "ETIMEDOUT",
    0x3d: "ECONNREFUSED",
    0x3e: "ENETDOWN",
    0x3f: "ETXTBSY",
    0x40: "ELOOP",
    0x41: "EHOSTUNREACH",
    0x42: "ENOTBLK",
    0x43: "EHOSTDOWN",
    0x44: "EINPROGRESS",
    0x45: "EALREADY",
    0x46: "EWOULDBLOCK",
    0x47: "ENOSYS",
    0x48: "ECANCELED",
    0x4a: "ENOSR",
    0x4b: "ENOSTR",
    0x4c: "EPROTO",
    0x4d: "EBADMSG",
    0x4e: "ENODATA",
    0x4f: "ETIME",
    0x50: "ENOMSG",
    0x51: "ERRMAX",
    0x30065: "S_taskLib_NAME_NOT_FOUND",
    0x30066: "S_taskLib_TASK_HOOK_TABLE_FULL",
    0x30067: "S_taskLib_TASK_HOOK_NOT_FOUND",
    0x30068: "S_taskLib_TASK_SWAP_HOOK_REFERENCED",
    0x30069: "S_taskLib_TASK_SWAP_HOOK_SET",
    0x3006a: "S_taskLib_TASK_SWAP_HOOK_CLEAR",
    0x3006b: "S_taskLib_TASK_VAR_NOT_FOUND",
    0x3006c: "S_taskLib_TASK_UNDELAYED",
    0x3006d: "S_taskLib_ILLEGAL_PRIORITY",
    0x70001: "S_dsmLib_UNKNOWN_INSTRUCTION",
    0xc0001: "S_ioLib_NO_DRIVER",
    0xc0002: "S_ioLib_UNKNOWN_REQUEST",
    0xc0003: "S_ioLib_DEVICE_ERROR",
    0xc0004: "S_ioLib_DEVICE_TIMEOUT",
    0xc0005: "S_ioLib_WRITE_PROTECTED",
    0xc0006: "S_ioLib_DISK_NOT_PRESENT",
    0xc0007: "S_ioLib_NO_FILENAME",
    0xc0008: "S_ioLib_CANCELLED",
    0xc0009: "S_ioLib_NO_DEVICE_NAME_IN_PATH",
    0xc000a: "S_ioLib_NAME_TOO_LONG",
    0xc000b: "S_ioLib_UNFORMATED",
    0xc000c: "S_ioLib_CANT_OVERWRITE_DIR",
    0xd0001: "S_iosLib_DEVICE_NOT_FOUND",
    0xd0002: "S_iosLib_DRIVER_GLUT",
    0xd0003: "S_iosLib_INVALID_FILE_DESCRIPTOR",
    0xd0004: "S_iosLib_TOO_MANY_OPEN_FILES",
    0xd0005: "S_iosLib_CONTROLLER_NOT_PRESENT",
    0xd0006: "S_iosLib_DUPLICATE_DEVICE_NAME",
    0xd0007: "S_iosLib_INVALID_ETHERNET_ADDRESS",
    0xe0001: "S_loadLib_ROUTINE_NOT_INSTALLED",
    0xe0002: "S_loadLib_TOO_MANY_SYMBOLS",
    0x110001: "S_memLib_NOT_ENOUGH_MEMORY",
    0x110002: "S_memLib_INVALID_NBYTES",
    0x110003: "S_memLib_BLOCK_ERROR",
    0x110004: "S_memLib_NO_PARTITION_DESTROY",
    0x110005: "S_memLib_PAGE_SIZE_UNAVAILABLE",
    0x140001: "S_rt11FsLib_VOLUME_NOT_AVAILABLE",
    0x140002: "S_rt11FsLib_DISK_FULL",
    0x140003: "S_rt11FsLib_FILE_NOT_FOUND",
    0x140004: "S_rt11FsLib_NO_FREE_FILE_DESCRIPTORS",
    0x140005: "S_rt11FsLib_INVALID_NUMBER_OF_BYTES",
    0x140006: "S_rt11FsLib_FILE_ALREADY_EXISTS",
    0x140007: "S_rt11FsLib_BEYOND_FILE_LIMIT",
    0x140008: "S_rt11FsLib_INVALID_DEVICE_PARAMETERS",
    0x140009: "S_rt11FsLib_NO_MORE_FILES_ALLOWED_ON_DISK",
    0x14000a: "S_rt11FsLib_ENTRY_NUMBER_TOO_BIG",
    0x14000b: "S_rt11FsLib_NO_BLOCK_DEVICE",
    0x160065: "S_semLib_INVALID_STATE",
    0x160066: "S_semLib_INVALID_OPTION",
    0x160067: "S_semLib_INVALID_QUEUE_TYPE",
    0x160068: "S_semLib_INVALID_OPERATION",
    0x1c0001: "S_symLib_SYMBOL_NOT_FOUND",
    0x1c0002: "S_symLib_NAME_CLASH",
    0x1c0003: "S_symLib_TABLE_NOT_EMPTY",
    0x1c0004: "S_symLib_SYMBOL_STILL_IN_TABLE",
    0x1c000c: "S_symLib_INVALID_SYMTAB_ID",
    0x1c000d: "S_symLib_INVALID_SYM_ID_PTR",
    0x230001: "S_usrLib_NOT_ENOUGH_ARGS",
    0x250001: "S_remLib_ALL_PORTS_IN_USE",
    0x250002: "S_remLib_RSH_ERROR",
    0x250003: "S_remLib_IDENTITY_TOO_BIG",
    0x250004: "S_remLib_RSH_STDERR_SETUP_FAILED",
    0x290001: "S_netDrv_INVALID_NUMBER_OF_BYTES",
    0x290002: "S_netDrv_SEND_ERROR",
    0x290003: "S_netDrv_RECV_ERROR",
    0x290004: "S_netDrv_UNKNOWN_REQUEST",
    0x290005: "S_netDrv_BAD_SEEK",
    0x290006: "S_netDrv_SEEK_PAST_EOF_ERROR",
    0x290007: "S_netDrv_BAD_EOF_POSITION",
    0x290008: "S_netDrv_SEEK_FATAL_ERROR",
    0x290009: "S_netDrv_WRITE_ONLY_CANNOT_READ",
    0x29000a: "S_netDrv_READ_ONLY_CANNOT_WRITE",
    0x29000b: "S_netDrv_READ_ERROR",
    0x29000c: "S_netDrv_WRITE_ERROR",
    0x29000d: "S_netDrv_NO_SUCH_FILE_OR_DIR",
    0x29000e: "S_netDrv_PERMISSION_DENIED",
    0x29000f: "S_netDrv_IS_A_DIRECTORY",
    0x290010: "S_netDrv_UNIX_FILE_ERROR",
    0x290011: "S_netDrv_ILLEGAL_VALUE",
    0x2b0001: "S_inetLib_ILLEGAL_INTERNET_ADDRESS",
    0x2b0002: "S_inetLib_ILLEGAL_NETWORK_NUMBER",
    0x2c0001: "S_routeLib_ILLEGAL_INTERNET_ADDRESS",
    0x2c0002: "S_routeLib_ILLEGAL_NETWORK_NUMBER",
    0x2d0001: "S_nfsDrv_INVALID_NUMBER_OF_BYTES",
    0x2d0002: "S_nfsDrv_BAD_FLAG_MODE",
    0x2d0003: "S_nfsDrv_CREATE_NO_FILE_NAME",
    0x2d0004: "S_nfsDrv_FATAL_ERR_FLUSH_INVALID_CACHE",
    0x2d0005: "S_nfsDrv_WRITE_ONLY_CANNOT_READ",
    0x2d0006: "S_nfsDrv_READ_ONLY_CANNOT_WRITE",
    0x2d0007: "S_nfsDrv_NOT_AN_NFS_DEVICE",
    0x2d0008: "S_nfsDrv_NO_HOST_NAME_SPECIFIED",
    0x2d0009: "S_nfsDrv_PERMISSION_DENIED",
    0x2d000a: "S_nfsDrv_NO_SUCH_FILE_OR_DIR",
    0x2d000b: "S_nfsDrv_IS_A_DIRECTORY",
    0x2e0001: "S_nfsLib_NFS_AUTH_UNIX_FAILED",
    0x2e0002: "S_nfsLib_NFS_INAPPLICABLE_FILE_TYPE",
    0x310001: "S_errnoLib_NO_STAT_SYM_TBL",
    0x320001: "S_hostLib_UNKNOWN_HOST",
    0x320002: "S_hostLib_HOST_ALREADY_ENTERED",
    0x320003: "S_hostLib_INVALID_PARAMETER",
    0x350001: "S_if_sl_INVALID_UNIT_NUMBER",
    0x350002: "S_if_sl_UNIT_UNINITIALIZED",
    0x350003: "S_if_sl_UNIT_ALREADY_INITIALIZED",
    0x360001: "S_loginLib_UNKNOWN_USER",
    0x360002: "S_loginLib_USER_ALREADY_EXISTS",
    0x360003: "S_loginLib_INVALID_PASSWORD",
    0x370001: "S_scsiLib_DEV_NOT_READY",
    0x370002: "S_scsiLib_WRITE_PROTECTED",
    0x370003: "S_scsiLib_MEDIUM_ERROR",
    0x370004: "S_scsiLib_HARDWARE_ERROR",
    0x370005: "S_scsiLib_ILLEGAL_REQUEST",
    0x370006: "S_scsiLib_BLANK_CHECK",
    0x370007: "S_scsiLib_ABORTED_COMMAND",
    0x370008: "S_scsiLib_VOLUME_OVERFLOW",
    0x370009: "S_scsiLib_UNIT_ATTENTION",
    0x37000a: "S_scsiLib_SELECT_TIMEOUT",
    0x37000b: "S_scsiLib_LUN_NOT_PRESENT",
    0x37000c: "S_scsiLib_ILLEGAL_BUS_ID",
    0x37000d: "S_scsiLib_NO_CONTROLLER",
    0x37000e: "S_scsiLib_REQ_SENSE_ERROR",
    0x37000f: "S_scsiLib_DEV_UNSUPPORTED",
    0x370010: "S_scsiLib_ILLEGAL_PARAMETER",
    0x370011: "S_scsiLib_INVALID_PHASE",
    0x370012: "S_scsiLib_ABORTED",
    0x370013: "S_scsiLib_ILLEGAL_OPERATION",
    0x370014: "S_scsiLib_DEVICE_EXIST",
    0x370015: "S_scsiLib_DISCONNECTED",
    0x370016: "S_scsiLib_BUS_RESET",
    0x370017: "S_scsiLib_INVALID_TAG_TYPE",
    0x370018: "S_scsiLib_SOFTWARE_ERROR",
    0x370019: "S_scsiLib_NO_MORE_THREADS",
    0x37001a: "S_scsiLib_UNKNOWN_SENSE_DATA",
    0x37001b: "S_scsiLib_INVALID_BLOCK_SIZE",
    0x380001: "S_dosFsLib_32BIT_OVERFLOW",
    0x380002: "S_dosFsLib_DISK_FULL",
    0x380003: "S_dosFsLib_FILE_NOT_FOUND",
    0x380004: "S_dosFsLib_NO_FREE_FILE_DESCRIPTORS",
    0x380005: "S_dosFsLib_NOT_FILE",
    0x380006: "S_dosFsLib_NOT_SAME_VOLUME",
    0x380007: "S_dosFsLib_NOT_DIRECTORY",
    0x380008: "S_dosFsLib_DIR_NOT_EMPTY",
    0x380009: "S_dosFsLib_FILE_EXISTS",
    0x38000a: "S_dosFsLib_INVALID_PARAMETER",
    0x38000b: "S_dosFsLib_NAME_TOO_LONG",
    0x38000c: "S_dosFsLib_UNSUPPORTED",
    0x38000d: "S_dosFsLib_VOLUME_NOT_AVAILABLE",
    0x38000e: "S_dosFsLib_INVALID_NUMBER_OF_BYTES",
    0x38000f: "S_dosFsLib_ILLEGAL_NAME",
    0x380010: "S_dosFsLib_CANT_DEL_ROOT",
    0x380011: "S_dosFsLib_READ_ONLY",
    0x380012: "S_dosFsLib_ROOT_DIR_FULL",
    0x380013: "S_dosFsLib_NO_LABEL",
    0x380014: "S_dosFsLib_NO_CONTIG_SPACE",
    0x380015: "S_dosFsLib_FD_OBSOLETE",
    0x380016: "S_dosFsLib_DELETED",
    0x380017: "S_dosFsLib_INTERNAL_ERROR",
    0x380018: "S_dosFsLib_WRITE_ONLY",
    0x380019: "S_dosFsLib_ILLEGAL_PATH",
    0x38001a: "S_dosFsLib_ACCESS_BEYOND_EOF",
    0x38001b: "S_dosFsLib_DIR_READ_ONLY",
    0x38001c: "S_dosFsLib_UNKNOWN_VOLUME_FORMAT",
    0x38001d: "S_dosFsLib_ILLEGAL_CLUSTER_NUMBER",
    0x390001: "S_selectLib_NO_SELECT_SUPPORT_IN_DRIVER",
    0x390002: "S_selectLib_NO_SELECT_CONTEXT",
    0x390003: "S_selectLib_WIDTH_OUT_OF_RANGE",
    0x3a0001: "S_hashLib_KEY_CLASH",
    0x3b0001: "S_qLib_Q_CLASS_ID_ERROR",
    0x3d0001: "S_objLib_OBJ_ID_ERROR",
    0x3d0002: "S_objLib_OBJ_UNAVAILABLE",
    0x3d0003: "S_objLib_OBJ_DELETED",
    0x3d0004: "S_objLib_OBJ_TIMEOUT",
    0x3d0005: "S_objLib_OBJ_NO_METHOD",
    0x3e0001: "S_qPriHeapLib_NULL_HEAP_ARRAY",
    0x3f0001: "S_qPriBMapLib_NULL_BMAP_LIST",
    0x410001: "S_msgQLib_INVALID_MSG_LENGTH",
    0x410002: "S_msgQLib_NON_ZERO_TIMEOUT_AT_INT_LEVEL",
    0x410003: "S_msgQLib_INVALID_QUEUE_TYPE",
    0x420001: "S_classLib_CLASS_ID_ERROR",
    0x420002: "S_classLib_NO_CLASS_DESTROY",
    0x430001: "S_intLib_NOT_ISR_CALLABLE",
    0x430002: "S_intLib_VEC_TABLE_WP_UNAVAILABLE",
    0x450001: "S_cacheLib_INVALID_CACHE",
    0x460001: "S_rawFsLib_VOLUME_NOT_AVAILABLE",
    0x460002: "S_rawFsLib_END_OF_DEVICE",
    0x460003: "S_rawFsLib_NO_FREE_FILE_DESCRIPTORS",
    0x460004: "S_rawFsLib_INVALID_NUMBER_OF_BYTES",
    0x460005: "S_rawFsLib_ILLEGAL_NAME",
    0x460006: "S_rawFsLib_NOT_FILE",
    0x460007: "S_rawFsLib_READ_ONLY",
    0x460008: "S_rawFsLib_FD_OBSOLETE",
    0x460009: "S_rawFsLib_NO_BLOCK_DEVICE",
    0x46000a: "S_rawFsLib_BAD_SEEK",
    0x46000b: "S_rawFsLib_INVALID_PARAMETER",
    0x46000c: "S_rawFsLib_32BIT_OVERFLOW",
    0x470001: "S_arpLib_INVALID_ARGUMENT",
    0x470002: "S_arpLib_INVALID_HOST",
    0x470003: "S_arpLib_INVALID_ENET_ADDRESS",
    0x470004: "S_arpLib_INVALID_FLAG",
    0x480001: "S_smLib_MEMORY_ERROR",
    0x480002: "S_smLib_INVALID_CPU_NUMBER",
    0x480003: "S_smLib_NOT_ATTACHED",
    0x480004: "S_smLib_NO_REGIONS",
    0x490001: "S_bootpLib_INVALID_ARGUMENT",
    0x490002: "S_bootpLib_INVALID_COOKIE",
    0x490003: "S_bootpLib_NO_BROADCASTS",
    0x490004: "S_bootpLib_PARSE_ERROR",
    0x490005: "S_bootpLib_INVALID_TAG",
    0x490006: "S_bootpLib_TIME_OUT",
    0x490007: "S_bootpLib_MEM_ERROR",
    0x490008: "S_bootpLib_NOT_INITIALIZED",
    0x490009: "S_bootpLib_BAD_DEVICE",
    0x4a0001: "S_icmpLib_TIMEOUT",
    0x4a0002: "S_icmpLib_NO_BROADCAST",
    0x4a0003: "S_icmpLib_INVALID_INTERFACE",
    0x4a0004: "S_icmpLib_INVALID_ARGUMENT",
    0x4b0001: "S_tftpLib_INVALID_ARGUMENT",
    0x4b0002: "S_tftpLib_INVALID_DESCRIPTOR",
    0x4b0003: "S_tftpLib_INVALID_COMMAND",
    0x4b0004: "S_tftpLib_INVALID_MODE",
    0x4b0005: "S_tftpLib_UNKNOWN_HOST",
    0x4b0006: "S_tftpLib_NOT_CONNECTED",
    0x4b0007: "S_tftpLib_TIMED_OUT",
    0x4b0008: "S_tftpLib_TFTP_ERROR",
    0x4c0001: "S_proxyArpLib_INVALID_PARAMETER",
    0x4c0002: "S_proxyArpLib_INVALID_INTERFACE",
    0x4c0003: "S_proxyArpLib_INVALID_PROXY_NET",
    0x4c0004: "S_proxyArpLib_INVALID_CLIENT",
    0x4c0005: "S_proxyArpLib_INVALID_ADDRESS",
    0x4c0006: "S_proxyArpLib_TIMEOUT",
    0x4e0001: "S_smPktLib_SHARED_MEM_TOO_SMALL",
    0x4e0002: "S_smPktLib_MEMORY_ERROR",
    0x4e0003: "S_smPktLib_DOWN",
    0x4e0004: "S_smPktLib_NOT_ATTACHED",
    0x4e0005: "S_smPktLib_INVALID_PACKET",
    0x4e0006: "S_smPktLib_PACKET_TOO_BIG",
    0x4e0007: "S_smPktLib_INVALID_CPU_NUMBER",
    0x4e0008: "S_smPktLib_DEST_NOT_ATTACHED",
    0x4e0009: "S_smPktLib_INCOMPLETE_BROADCAST",
    0x4e000a: "S_smPktLib_LIST_FULL",
    0x4e000b: "S_smPktLib_LOCK_TIMEOUT",
    0x4f0001: "S_loadEcoffLib_HDR_READ",
    0x4f0002: "S_loadEcoffLib_OPTHDR_READ",
    0x4f0003: "S_loadEcoffLib_SCNHDR_READ",
    0x4f0004: "S_loadEcoffLib_READ_SECTIONS",
    0x4f0005: "S_loadEcoffLib_LOAD_SECTIONS",
    0x4f0006: "S_loadEcoffLib_RELOC_READ",
    0x4f0007: "S_loadEcoffLib_SYMHDR_READ",
    0x4f0008: "S_loadEcoffLib_EXTSTR_READ",
    0x4f0009: "S_loadEcoffLib_EXTSYM_READ",
    0x4f000a: "S_loadEcoffLib_GPREL_REFERENCE",
    0x4f000b: "S_loadEcoffLib_JMPADDR_ERROR",
    0x4f000c: "S_loadEcoffLib_NO_REFLO_PAIR",
    0x4f000d: "S_loadEcoffLib_UNRECOGNIZED_RELOCENTRY",
    0x4f000e: "S_loadEcoffLib_REFHALF_OVFL",
    0x4f000f: "S_loadEcoffLib_UNEXPECTED_SYM_CLASS",
    0x4f0010: "S_loadEcoffLib_UNRECOGNIZED_SYM_CLASS",
    0x4f0011: "S_loadEcoffLib_FILE_READ_ERROR",
    0x4f0012: "S_loadEcoffLib_FILE_ENDIAN_ERROR",
    0x500001: "S_loadAoutLib_TOO_MANY_SYMBOLS",
    0x520001: "S_bootLoadLib_ROUTINE_NOT_INSTALLED",
    0x530001: "S_loadLib_FILE_READ_ERROR",
    0x530002: "S_loadLib_REALLOC_ERROR",
    0x530003: "S_loadLib_JMPADDR_ERROR",
    0x530004: "S_loadLib_NO_REFLO_PAIR",
    0x530005: "S_loadLib_GPREL_REFERENCE",
    0x530006: "S_loadLib_UNRECOGNIZED_RELOCENTRY",
    0x530007: "S_loadLib_REFHALF_OVFL",
    0x530008: "S_loadLib_FILE_ENDIAN_ERROR",
    0x530009: "S_loadLib_UNEXPECTED_SYM_CLASS",
    0x53000a: "S_loadLib_UNRECOGNIZED_SYM_CLASS",
    0x53000b: "S_loadLib_HDR_READ",
    0x53000c: "S_loadLib_OPTHDR_READ",
    0x53000d: "S_loadLib_SCNHDR_READ",
    0x53000e: "S_loadLib_READ_SECTIONS",
    0x53000f: "S_loadLib_LOAD_SECTIONS",
    0x530010: "S_loadLib_RELOC_READ",
    0x530011: "S_loadLib_SYMHDR_READ",
    0x530012: "S_loadLib_EXTSTR_READ",
    0x530013: "S_loadLib_EXTSYM_READ",
    0x530014: "S_loadLib_NO_RELOCATION_ROUTINE",
    0x540001: "S_vmLib_NOT_PAGE_ALIGNED",
    0x540002: "S_vmLib_BAD_STATE_PARAM",
    0x540003: "S_vmLib_BAD_MASK_PARAM",
    0x540004: "S_vmLib_ADDR_IN_GLOBAL_SPACE",
    0x540005: "S_vmLib_TEXT_PROTECTION_UNAVAILABLE",
    0x540006: "S_vmLib_NO_FREE_REGIONS",
    0x540007: "S_vmLib_ADDRS_NOT_EQUAL",
    0x550001: "S_mmuLib_INVALID_PAGE_SIZE",
    0x550002: "S_mmuLib_NO_DESCRIPTOR",
    0x550003: "S_mmuLib_INVALID_DESCRIPTOR",
    0x550005: "S_mmuLib_OUT_OF_PMEGS",
    0x550006: "S_mmuLib_VIRT_ADDR_OUT_OF_BOUNDS",
    0x560001: "S_moduleLib_MODULE_NOT_FOUND",
    0x560002: "S_moduleLib_HOOK_NOT_FOUND",
    0x560003: "S_moduleLib_BAD_CHECKSUM",
    0x560004: "S_moduleLib_MAX_MODULES_LOADED",
    0x570001: "S_unldLib_MODULE_NOT_FOUND",
    0x570002: "S_unldLib_TEXT_IN_USE",
    0x580001: "S_smObjLib_NOT_INITIALIZED",
    0x580002: "S_smObjLib_NOT_A_GLOBAL_ADRS",
    0x580003: "S_smObjLib_NOT_A_LOCAL_ADRS",
    0x580004: "S_smObjLib_SHARED_MEM_TOO_SMALL",
    0x580005: "S_smObjLib_TOO_MANY_CPU",
    0x580006: "S_smObjLib_LOCK_TIMEOUT",
    0x580007: "S_smObjLib_NO_OBJECT_DESTROY",
    0x590001: "S_smNameLib_NOT_INITIALIZED",
    0x590002: "S_smNameLib_NAME_TOO_LONG",
    0x590003: "S_smNameLib_NAME_NOT_FOUND",
    0x590004: "S_smNameLib_VALUE_NOT_FOUND",
    0x590005: "S_smNameLib_NAME_ALREADY_EXIST",
    0x590006: "S_smNameLib_DATABASE_FULL",
    0x590007: "S_smNameLib_INVALID_WAIT_TYPE",
    0x5b0001: "S_m2Lib_INVALID_PARAMETER",
    0x5b0002: "S_m2Lib_ENTRY_NOT_FOUND",
    0x5b0003: "S_m2Lib_TCPCONN_FD_NOT_FOUND",
    0x5b0004: "S_m2Lib_INVALID_VAR_TO_SET",
    0x5b0005: "S_m2Lib_CANT_CREATE_SYS_SEM",
    0x5b0006: "S_m2Lib_CANT_CREATE_IF_SEM",
    0x5b0007: "S_m2Lib_CANT_CREATE_ROUTE_SEM",
    0x5b0008: "S_m2Lib_ARP_PHYSADDR_NOT_SPECIFIED",
    0x5b0009: "S_m2Lib_IF_TBL_IS_EMPTY",
    0x5b000a: "S_m2Lib_IF_CNFG_CHANGED",
    0x5b000b: "S_m2Lib_TOO_BIG",
    0x5b000c: "S_m2Lib_BAD_VALUE",
    0x5b000d: "S_m2Lib_READ_ONLY",
    0x5b000e: "S_m2Lib_GEN_ERR",
    0x5c0001: "S_aioPxLib_DRV_NUM_INVALID",
    0x5c0002: "S_aioPxLib_AIO_NOT_DEFINED",
    0x5c0003: "S_aioPxLib_IOS_NOT_INITIALIZED",
    0x5c0004: "S_aioPxLib_NO_AIO_DEVICE",
    0x5e0001: "S_mountLib_ILLEGAL_MODE",
    0x600001: "S_loadSomCoffLib_HDR_READ",
    0x600002: "S_loadSomCoffLib_AUXHDR_READ",
    0x600003: "S_loadSomCoffLib_SYM_READ",
    0x600004: "S_loadSomCoffLib_SYMSTR_READ",
    0x600005: "S_loadSomCoffLib_OBJ_FMT",
    0x600006: "S_loadSomCoffLib_SPHDR_ALLOC",
    0x600007: "S_loadSomCoffLib_SPHDR_READ",
    0x600008: "S_loadSomCoffLib_SUBSPHDR_ALLOC",
    0x600009: "S_loadSomCoffLib_SUBSPHDR_READ",
    0x60000a: "S_loadSomCoffLib_SPSTRING_ALLOC",
    0x60000b: "S_loadSomCoffLib_SPSTRING_READ",
    0x60000c: "S_loadSomCoffLib_INFO_ALLOC",
    0x60000d: "S_loadSomCoffLib_LOAD_SPACE",
    0x60000e: "S_loadSomCoffLib_RELOC_ALLOC",
    0x60000f: "S_loadSomCoffLib_RELOC_READ",
    0x600010: "S_loadSomCoffLib_RELOC_NEW",
    0x600011: "S_loadSomCoffLib_RELOC_VERSION",
    0x610001: "S_loadElfLib_HDR_READ",
    0x610002: "S_loadElfLib_HDR_ERROR",
    0x610003: "S_loadElfLib_PHDR_MALLOC",
    0x610004: "S_loadElfLib_PHDR_READ",
    0x610005: "S_loadElfLib_SHDR_MALLOC",
    0x610006: "S_loadElfLib_SHDR_READ",
    0x610007: "S_loadElfLib_READ_SECTIONS",
    0x610008: "S_loadElfLib_LOAD_SECTIONS",
    0x610009: "S_loadElfLib_LOAD_PROG",
    0x61000a: "S_loadElfLib_SYMTAB",
    0x61000b: "S_loadElfLib_RELA_SECTION",
    0x61000c: "S_loadElfLib_SCN_READ",
    0x61000d: "S_loadElfLib_SDA_MALLOC",
    0x61000f: "S_loadElfLib_SST_READ",
    0x610014: "S_loadElfLib_JMPADDR_ERROR",
    0x610015: "S_loadElfLib_GPREL_REFERENCE",
    0x610016: "S_loadElfLib_UNRECOGNIZED_RELOCENTRY",
    0x610017: "S_loadElfLib_RELOC",
    0x610018: "S_loadElfLib_UNSUPPORTED",
    0x610019: "S_loadElfLib_REL_SECTION",
    0x620001: "S_mbufLib_ID_INVALID",
    0x620002: "S_mbufLib_ID_EMPTY",
    0x620003: "S_mbufLib_SEGMENT_NOT_FOUND",
    0x620004: "S_mbufLib_LENGTH_INVALID",
    0x620005: "S_mbufLib_OFFSET_INVALID",
    0x630001: "S_pingLib_NOT_INITIALIZED",
    0x630002: "S_pingLib_TIMEOUT",
    0x650001: "S_pppSecretLib_NOT_INITIALIZED",
    0x650002: "S_pppSecretLib_SECRET_DOES_NOT_EXIST",
    0x650003: "S_pppSecretLib_SECRET_EXISTS",
    0x660001: "S_pppHookLib_NOT_INITIALIZED",
    0x660002: "S_pppHookLib_HOOK_DELETED",
    0x660003: "S_pppHookLib_HOOK_ADDED",
    0x660004: "S_pppHookLib_HOOK_UNKNOWN",
    0x660005: "S_pppHookLib_INVALID_UNIT",
    0x670001: "S_tapeFsLib_NO_SEQ_DEV",
    0x670002: "S_tapeFsLib_ILLEGAL_TAPE_CONFIG_PARM",
    0x670003: "S_tapeFsLib_SERVICE_NOT_AVAILABLE",
    0x670004: "S_tapeFsLib_INVALID_BLOCK_SIZE",
    0x670005: "S_tapeFsLib_ILLEGAL_FILE_SYSTEM_NAME",
    0x670006: "S_tapeFsLib_ILLEGAL_FLAGS",
    0x670007: "S_tapeFsLib_FILE_DESCRIPTOR_BUSY",
    0x670008: "S_tapeFsLib_VOLUME_NOT_AVAILABLE",
    0x670009: "S_tapeFsLib_BLOCK_SIZE_MISMATCH",
    0x67000a: "S_tapeFsLib_INVALID_NUMBER_OF_BYTES",
    0x680001: "S_snmpdLib_VIEW_CREATE_FAILURE",
    0x680002: "S_snmpdLib_VIEW_INSTALL_FAILURE",
    0x680003: "S_snmpdLib_VIEW_MASK_FAILURE",
    0x680004: "S_snmpdLib_VIEW_DEINSTALL_FAILURE",
    0x680005: "S_snmpdLib_VIEW_LOOKUP_FAILURE",
    0x680006: "S_snmpdLib_MIB_ADDITION_FAILURE",
    0x680007: "S_snmpdLib_NODE_NOT_FOUND",
    0x680008: "S_snmpdLib_INVALID_SNMP_VERSION",
    0x680009: "S_snmpdLib_TRAP_CREATE_FAILURE",
    0x68000a: "S_snmpdLib_TRAP_BIND_FAILURE",
    0x68000b: "S_snmpdLib_TRAP_ENCODE_FAILURE",
    0x68000c: "S_snmpdLib_INVALID_OID_SYNTAX",
    0x690001: "S_pcmciaLib_BATTERY_DEAD",
    0x690002: "S_pcmciaLib_BATTERY_WARNING",
    0x6a0001: "S_dhcpcLib_NOT_INITIALIZED",
    0x6a0002: "S_dhcpcLib_BAD_DEVICE",
    0x6a0003: "S_dhcpcLib_MAX_LEASES_REACHED",
    0x6a0004: "S_dhcpcLib_MEM_ERROR",
    0x6a0005: "S_dhcpcLib_BAD_COOKIE",
    0x6a0006: "S_dhcpcLib_NOT_BOUND",
    0x6a0007: "S_dhcpcLib_BAD_OPTION",
    0x6a0008: "S_dhcpcLib_OPTION_NOT_PRESENT",
    0x6a0009: "S_dhcpcLib_TIMER_ERROR",
    0x6a000a: "S_dhcpcLib_OPTION_NOT_STORED",
    0x6b0001: "S_resolvLib_NO_RECOVERY",
    0x6b0002: "S_resolvLib_TRY_AGAIN",
    0x6b0003: "S_resolvLib_HOST_NOT_FOUND",
    0x6b0004: "S_resolvLib_NO_DATA",
    0x6b0005: "S_resolvLib_BUFFER_2_SMALL",
    0x6b0006: "S_resolvLib_INVALID_PARAMETER",
    0x6b0007: "S_resolvLib_INVALID_ADDRESS",
    0x6d0001: "S_muxLib_LOAD_FAILED",
    0x6d0002: "S_muxLib_NO_DEVICE",
    0x6d0003: "S_muxLib_INVALID_ARGS",
    0x6d0004: "S_muxLib_ALLOC_FAILED",
    0x6d0005: "S_muxLib_ALREADY_BOUND",
    0x6d0006: "S_muxLib_UNLOAD_FAILED",
    0x6d0007: "S_muxLib_NOT_A_TK_DEVICE",
    0x6d0008: "S_muxLib_NO_TK_DEVICE",
    0x6d0009: "S_muxLib_END_BIND_FAILED",
    0x6e0001: "S_m2RipLib_IFACE_NOT_FOUND",
    0x700001: "S_dhcpsLib_NOT_INITIALIZED",
    0x710001: "S_sntpcLib_INVALID_PARAMETER",
    0x710002: "S_sntpcLib_INVALID_ADDRESS",
    0x710003: "S_sntpcLib_TIMEOUT",
    0x710004: "S_sntpcLib_VERSION_UNSUPPORTED",
    0x710005: "S_sntpcLib_SERVER_UNSYNC",
    0x720001: "S_sntpsLib_INVALID_PARAMETER",
    0x720002: "S_sntpsLib_INVALID_ADDRESS",
    0x730001: "S_netBufLib_MEMSIZE_INVALID",
    0x730002: "S_netBufLib_CLSIZE_INVALID",
    0x730003: "S_netBufLib_NO_SYSTEM_MEMORY",
    0x730004: "S_netBufLib_MEM_UNALIGNED",
    0x730005: "S_netBufLib_MEMSIZE_UNALIGNED",
    0x730006: "S_netBufLib_MEMAREA_INVALID",
    0x730007: "S_netBufLib_MBLK_INVALID",
    0x730008: "S_netBufLib_NETPOOL_INVALID",
    0x730009: "S_netBufLib_INVALID_ARGUMENT",
    0x73000a: "S_netBufLib_NO_POOL_MEMORY",
    0x740001: "S_cdromFsLib_ALREADY_INIT",
    0x740003: "S_cdromFsLib_DEVICE_REMOVED",
    0x740004: "S_cdromFsLib_SUCH_PATH_TABLE_SIZE_NOT_SUPPORTED",
    0x740005: "S_cdromFsLib_ONE_OF_VALUES_NOT_POWER_OF_2",
    0x740006: "S_cdromFsLib_UNNOWN_FILE_SYSTEM",
    0x740007: "S_cdromFsLib_INVAL_VOL_DESCR",
    0x740008: "S_cdromFsLib_INVALID_PATH_STRING",
    0x740009: "S_cdromFsLib_MAX_DIR_HIERARCHY_LEVEL_OVERFLOW",
    0x74000a: "S_cdromFsLib_NO_SUCH_FILE_OR_DIRECTORY",
    0x74000b: "S_cdromFsLib_INVALID_DIRECTORY_STRUCTURE",
    0x74000c: "S_cdromFsLib_INVALID_FILE_DESCRIPTOR",
    0x74000d: "S_cdromFsLib_READ_ONLY_DEVICE",
    0x74000e: "S_cdromFsLib_END_OF_FILE",
    0x74000f: "S_cdromFsLib_INV_ARG_VALUE",
    0x740010: "S_cdromFsLib_SEMTAKE_ERROR",
    0x740011: "S_cdromFsLib_SEMGIVE_ERROR",
    0x740012: "S_cdromFsLib_VOL_UNMOUNTED",
    0x740013: "S_cdromFsLib_INVAL_DIR_OPER",
    0x740014: "S_cdromFsLib_READING_FAILURE",
    0x740015: "S_cdromFsLib_INVALID_DIR_REC_STRUCT",
    0x750001: "S_loadLib_FILE_READ_ERROR",
    0x750002: "S_loadLib_REALLOC_ERROR",
    0x750003: "S_loadLib_JMPADDR_ERROR",
    0x750004: "S_loadLib_NO_REFLO_PAIR",
    0x750005: "S_loadLib_GPREL_REFERENCE",
    0x750006: "S_loadLib_UNRECOGNIZED_RELOCENTRY",
    0x750007: "S_loadLib_REFHALF_OVFL",
    0x750008: "S_loadLib_FILE_ENDIAN_ERROR",
    0x750009: "S_loadLib_UNEXPECTED_SYM_CLASS",
    0x75000a: "S_loadLib_UNRECOGNIZED_SYM_CLASS",
    0x75000b: "S_loadLib_HDR_READ",
    0x75000c: "S_loadLib_OPTHDR_READ",
    0x75000d: "S_loadLib_SCNHDR_READ",
    0x75000e: "S_loadLib_READ_SECTIONS",
    0x75000f: "S_loadLib_LOAD_SECTIONS",
    0x750010: "S_loadLib_RELOC_READ",
    0x750011: "S_loadLib_SYMHDR_READ",
    0x750012: "S_loadLib_EXTSTR_READ",
    0x750013: "S_loadLib_EXTSYM_READ",
    0x760001: "S_distLib_NOT_INITIALIZED",
    0x760002: "S_distLib_NO_OBJECT_DESTROY",
    0x760003: "S_distLib_UNREACHABLE",
    0x760004: "S_distLib_UNKNOWN_REQUEST",
    0x760005: "S_distLib_OBJ_ID_ERROR",
    0x770001: "S_distNameLib_NAME_TOO_LONG",
    0x770002: "S_distNameLib_ILLEGAL_LENGTH",
    0x770003: "S_distNameLib_INVALID_WAIT_TYPE",
    0x770004: "S_distNameLib_DATABASE_FULL",
    0x770005: "S_distNameLib_INCORRECT_LENGTH",
    0x780001: "S_msgQDistGrpLib_NAME_TOO_LONG",
    0x780002: "S_msgQDistGrpLib_INVALID_OPTION",
    0x780003: "S_msgQDistGrpLib_DATABASE_FULL",
    0x780004: "S_msgQDistGrpLib_NO_MATCH",
    0x790001: "S_msgQDistLib_INVALID_PRIORITY",
    0x790002: "S_msgQDistLib_INVALID_MSG_LENGTH",
    0x790003: "S_msgQDistLib_INVALID_TIMEOUT",
    0x790004: "S_msgQDistLib_NOT_GROUP_CALLABLE",
    0x790005: "S_msgQDistLib_RMT_MEMORY_SHORTAGE",
    0x790006: "S_msgQDistLib_OVERALL_TIMEOUT",
    0x7a0001: "S_if_ul_INVALID_UNIT_NUMBER",
    0x7a0002: "S_if_ul_UNIT_UNINITIALIZED",
    0x7a0003: "S_if_ul_UNIT_ALREADY_INITIALIZED",
    0x7a0004: "S_if_ul_NO_UNIX_DEVICE",
    0x7b0001: "S_miiLib_PHY_LINK_DOWN",
    0x7b0002: "S_miiLib_PHY_NULL",
    0x7b0003: "S_miiLib_PHY_NO_ABLE",
    0x7b0004: "S_miiLib_PHY_AN_FAIL",
    0x7c0001: "S_poolLib_ARG_NOT_VALID",
    0x7c0002: "S_poolLib_INVALID_POOL_ID",
    0x7c0003: "S_poolLib_NOT_POOL_ITEM",
    0x7c0004: "S_poolLib_POOL_IN_USE",
    0x7c0005: "S_poolLib_STATIC_POOL_EMPTY",
    0x7d0001: "S_setLib_LIB_INIT",
    0x7d0002: "S_setLib_LIB_NOT_INIT",
    0x7d0003: "S_setLib_ARG_NOT_VALID",
    0x7d0004: "S_setLib_OBJ_NOT_IN_SET",
    0x7e0001: "S_dmsLib_DMS_INIT",
    0x7e0002: "S_dmsLib_DMS_NOT_INIT",
    0x7e0003: "S_dmsLib_ARG_NOT_VALID",
    0x7e0004: "S_dmsLib_NAME_NOT_UNIQUE",
    0x7e0005: "S_dmsLib_NAME_UNKNOWN",
    0x7e0006: "S_dmsLib_DRIVER_UNKNOWN",
    0x7e0007: "S_dmsLib_BASIS_UNKNOWN",
    0x7e0008: "S_dmsLib_NO_CONNECT",
    0x7e0009: "S_dmsLib_NO_DISCONNECT",
    0x7e000a: "S_dmsLib_OBJ_ID_ERROR",
    0x7e000b: "S_dmsLib_ATTR_NOT_VALID",
    0x7e000c: "S_dmsLib_NOT_SUPPORTED",
    0x7e000d: "S_dmsLib_DRIVER_INACTIVE",
    0x7e000e: "S_dmsLib_INVALID_CLASS",
    0x800001: "S_igmpRouterLib_NOT_INITIALIZED",
    0x800002: "S_igmpRouterLib_VIF_OUT_OF_RANGE",
    0x800003: "S_igmpRouterLib_NO_FREE_VIFS",
    0x800004: "S_igmpRouterLib_INVALID_PORT_NUM",
    0x800005: "S_igmpRouterLib_NOT_ALL_IFS_DOWN",
    0x800006: "S_igmpRouterLib_THRESHOLD_REQUIRED",
    0x810001: "S_devCfgLib_DCFG_INIT",
    0x810002: "S_devCfgLib_DCFG_NOT_INIT",
    0x810003: "S_devCfgLib_PARAM_VAL_NOT_VALID",
    0x810004: "S_devCfgLib_DEVICE_NOT_FOUND",
    0x810005: "S_devCfgLib_PARAM_NOT_FOUND",
    0x810006: "S_devCfgLib_NO_NVRAM_SPACE",
    0x810007: "S_devCfgLib_NO_NVRAM",
    0x850001: "S_cbioLib_INVALID_CBIO_DEV_ID",
    0x860000: "S_eventLib_NULL_TASKID_AT_INT_LEVEL",
    0x870001: "S_fastPathLib_ALREADY_EXISTS",
    0x870002: "S_fastPathLib_ALREADY_REGISTERED",
    0x870003: "S_fastPathLib_INTERNAL_ERROR",
    0x870004: "S_fastPathLib_INVALID_ARG",
    0x870005: "S_fastPathLib_INVALID_OBJ",
    0x870006: "S_fastPathLib_INVALID_PARAMS",
    0x870007: "S_fastPathLib_INVALID_PROTO",
    0x870008: "S_fastPathLib_INVALID_STATE",
    0x870009: "S_fastPathLib_NOT_FOUND",
    0x87000a: "S_fastPathLib_NOT_INITIALIZED",
    0x880001: "S_ftpLib_ILLEGAL_VALUE",
    0x880002: "S_ftpLib_TRANSIENT_RETRY_LIMIT_EXCEEDED",
    0x880003: "S_ftpLib_FATAL_TRANSIENT_RESPONSE",
    0x8800dd: "S_ftpLib_REMOTE_SERVER_STATUS_221",
    0x8800e2: "S_ftpLib_REMOTE_SERVER_STATUS_226",
    0x880101: "S_ftpLib_REMOTE_SERVER_STATUS_257",
    0x8801a6: "S_ftpLib_REMOTE_SERVER_ERROR_422",
    0x8801a9: "S_ftpLib_REMOTE_SERVER_ERROR_425",
    0x8801c2: "S_ftpLib_REMOTE_SERVER_ERROR_450",
    0x8801c3: "S_ftpLib_REMOTE_SERVER_ERROR_451",
    0x8801c4: "S_ftpLib_REMOTE_SERVER_ERROR_452",
    0x8801f4: "S_ftpLib_REMOTE_SERVER_ERROR_500",
    0x8801f5: "S_ftpLib_REMOTE_SERVER_ERROR_501",
    0x8801f6: "S_ftpLib_REMOTE_SERVER_ERROR_502",
    0x8801f7: "S_ftpLib_REMOTE_SERVER_ERROR_503",
    0x8801f8: "S_ftpLib_REMOTE_SERVER_ERROR_504",
    0x880208: "S_ftpLib_REMOTE_SERVER_ERROR_520",
    0x880209: "S_ftpLib_REMOTE_SERVER_ERROR_521",
    0x880212: "S_ftpLib_REMOTE_SERVER_ERROR_530",
    0x880226: "S_ftpLib_REMOTE_SERVER_ERROR_550",
    0x880227: "S_ftpLib_REMOTE_SERVER_ERROR_551",
    0x880228: "S_ftpLib_REMOTE_SERVER_ERROR_552",
    0x880229: "S_ftpLib_REMOTE_SERVER_ERROR_553",
    0x88022a: "S_ftpLib_REMOTE_SERVER_ERROR_554"
}

def get_error_type(errno):
    '''Look up the error to print'''
    if errno in errnos.keys():
        return errnos[errno]
    return "ERROR_TYPE_UNDEFINED_%s"%(hex(errno))

class BColors:
    '''
        pretty coloring for the error to stick out
    '''
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ERROR(BPHandler):
    '''bp_handler for errors'''
    def __init__(self):
        self.last_error = None

    @bp_handler(['errnoSet'])
    def errno_set(self, qemu, bp_handler):
        if qemu.regs.r0 != 0:
            error_type = get_error_type(qemu.regs.r0)
            lr = qemu.regs.lr
            sym = qemu.get_symbol_name(lr)
            sym = "%s (%s)"%(hex(lr), sym) if sym is not None else hex(lr)
            error = "Errno Set :%s from %s"%(error_type, sym)
            if self.last_error != error:
                self.last_error = error
                log.info(BColors.WARNING + error + BColors.ENDC)
        return False, None

    @bp_handler(['__errno'])
    def __errno(self, qemu, bp_handler):
        log.debug(hex(qemu.regs.r0))
        errno = qemu.read_memory(qemu.regs.r0,4)
        if errno != 0:
            error_type = get_error_type(errno)
            log.info("Errno: %s from %s"%(error_type,hex(qemu.regs.lr)))
            log.debug(BColors.WARNING + "Errno: %s from %s",
                (error_type, hex(qemu.regs.lr)) + BColors.ENDC)
        return False, None


    @bp_handler(['ios_error', 'sys_err'])
    def sys_err(self, qemu, bp_handler):
        '''
            Handles ios_error and sys_err
        '''
        callee = qemu.regs.lr
        arg1 = qemu.get_arg(0)
        arg2 = qemu.get_arg(1)
        log.error(f"System Error called from {callee}: args({arg1}, {arg2}")

        return False, None
    @bp_handler(['logInit'])
    def logInit(self, qemu, bp_handler):
        print('------------------------------------ LOG INIT -------------------------------------------------')

        # This code will attempt to do the following:
        # 1) Open a log file (/d0/SYSTEM/custom_sfe.log)
        # 2) Get the returned file descriptor, write 'foo' to the file
        # 3) Close the file (with a hardcoded file descriptor)
        # 4) Print the return value from close

        logname = '/d0/SYSTEM/custom_sfe.log'
        alloced = qemu.hal_alloc(len(logname))
        logname_addr = alloced.base_addr
        print("logname addr: 0x%08x" % logname_addr)
        qemu.write_memory(logname_addr, 1, bytearray(logname.encode('utf-8')), len(logname))

        data = qemu.read_memory(logname_addr, 1, len(logname))
        for i in range(len(data)):
            print("%c" % data[i])

        return qemu.call('open', [logname_addr, 0x202, 0], self, 'open_done')

    @bp_handler(['open_done'])
    def open_done(self, qemu, bp_handler):
        fd = qemu.get_arg(0)

        print('------------------------------------ OPEN DONE -------------------------------------------------')
        print('\tfd: 0x%08x' % fd)

        writeStr = 'foo'
        alloced = qemu.hal_alloc(len(writeStr))
        addr = alloced.base_addr
        print("str addr: 0x%08x" % addr)

        return qemu.call('write', [fd, addr, len(writeStr)], self, 'write_done')

    @bp_handler(['write_done'])
    def write_done(self, qemu, bp_handler):
        ret = qemu.get_arg(0)

        print('------------------------------------ WRITE DONE -------------------------------------------------')
        print('\tret: %d' % ret)

        return qemu.call('close', [4], self, 'close_done')


    @bp_handler(['close_done'])
    def close_done(self, qemu, bp_handler):
        ret = qemu.regs.r0

        print('------------------------------------ CLOSE DONE -------------------------------------------------')
        print('\tret: %d' % ret)

        return True, None
