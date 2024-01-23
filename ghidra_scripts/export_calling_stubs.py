#!python2.7
# Exports the function stubs that allow building programs that call these
# functions.
# @category Halucinator
# @keybinding
# @menupath
# @toolbar
"""
Exports known functions to format so they can be called from c intercepts
"""
# python2.7 doesn't have f-strings
# pylint: disable=consider-using-f-string
import ghidra  # pylint: disable=import-error
from java.io import StringWriter  # pylint: disable=import-error

HEADER_NAME = "target_defs.h"

FUNC_FORMAT = """
{ret_type} TRGT_{name}({param_def}){{
    return (*({ret_type} (*)())(0x{addr}))({params});
}}
"""

PROTO_FORMAT = """
{ret_type} TRGT_{name}({param_def});
"""

VALID_TYPES = [
    "unsigned int",
    "sign char",
    "char",
    "unsigned char",
    "short",
    "int",
    "long",
    "float",
    "double",
    "uint32_t",
    "uint16_t",
    "uint8_t",
]

TYPE_MAPPINGS = {
    "undefined4": "uint32_t",
    "undefined2": "uint16_t",
    "undefined1": "uint8_t",
    "pointer32": "uint32_t*",
    "func": "uint32_t",
    "pointer": "uint32_t*",
}
DEFAULT_TYPE = "uint32_t"

FUNC_NAME_ILLEGALS = {
    ":": "_c",
    ";": "_s",
    "?": "_q",
    "~": "_t",
    "!": "_e",
    "$": "_M",
    "@": "_a",
    "%": "_p",
    "^": "_C",
    "&": "_A",
    "-": "_D",
    "=": "_E",
    "+": "_P",
    ".": "_d",
    "[": "_l",
    "]": "_j",
    "{": "_L",
    "}": "_J",
}


def handle_binary_data_types(data_type, dt_manager):
    """print all data types in binary"""
    sio = StringWriter()
    writer = ghidra.program.model.data.DataTypeWriter(dt_manager, sio)
    mon = ghidra.util.task.DummyCancellableTaskMonitor()
    cat_path = data_type.getCategoryPath()
    writer.write(dt_manager.getCategory(cat_path), mon)
    data_types = sio.toString()
    return data_types


def write_type_macros(outfile, fmgr, dt_manager):
    """
    Writes Macros for header file that redefines unknown types
    to know types
    """
    structs_printed = False
    param_types = set()

    data_types = None
    for func in fmgr.getFunctions(True):
        param_types.add(func.getReturnType().getName().strip(" *"))
        for param in func.getParameters():
            data_type = param.getDataType()
            if data_type not in param_types:
                param_types.add(data_type)
                if not structs_printed:
                    data_types = handle_binary_data_types(data_type, dt_manager)
                    structs_printed = True

    # first print all mappings that aren't in the built in data types
    # this prevents errors if our built-in types use something undefined
    for p_type_k, p_type_v in TYPE_MAPPINGS.items():
        if p_type_k not in param_types:
            outfile.write("typedef {} {};\n".format(p_type_v, p_type_k))

    # now print all the built-in data types. (From handle_binary_data_types)
    outfile.write(data_types)
    outfile.write("\n")
    return param_types


def get_params(func, macros):
    """
    Gets function parameters
    """
    params_list = []
    params_def = []
    for param in func.getParameters():
        p_name = param.getName()
        if p_name in macros:
            p_name += "_TRGT"
        params_list.append(p_name)
        params_def.append("{} {}".format(param.getDataType().getName(), p_name))
    return ",".join(params_list), ",".join(params_def)


def replace_invalid_chars(name):
    """
    Replace characters that are illegal to use in name in C
    """
    for illegal_char, replacement in FUNC_NAME_ILLEGALS.items():
        name = name.replace(illegal_char, replacement)
    return name


def write_functions(c_file, h_file, fmgr, macros):
    """
    Writes functions to the .c and .h header files
    """
    names = set()
    for func in fmgr.getFunctions(True):
        name = func.getName()
        name = replace_invalid_chars(name)
        addr = func.getEntryPoint()
        if name in names:
            name = "{}_0x{}".format(name, addr)

        params, params_def = get_params(func, macros)
        ret_type = func.getReturnType().getName()

        h_file.write(
            PROTO_FORMAT.format(ret_type=ret_type, name=name, param_def=params_def)
        )
        c_file.write(
            FUNC_FORMAT.format(
                ret_type=ret_type,
                name=name,
                addr=addr,
                params=params,
                param_def=params_def,
            )
        )
        names.add(name)


def main():
    """
    Will ask for directory to save the header file to and filename for the
    .c file.  Will then Write prototypes and a caller to the c file
    """
    fmgr = currentProgram.getFunctionManager()  # pylint: disable=undefined-variable
    dt_manager = (
        currentProgram.getDataTypeManager()  # pylint: disable=undefined-variable
    )
    h_file_loc = askDirectory(  # pylint: disable=undefined-variable
        "Directory to Save header file ({}) to ".format(HEADER_NAME), "Ok"
    )
    filename = askFile("C Filename", ".c")  # pylint: disable=undefined-variable
    c_filename = filename.getAbsolutePath()
    if not c_filename.endswith(".c"):
        c_filename += ".c"
    c_file = open(c_filename, "wt")  # pylint: disable=consider-using-with
    h_file_path = "{}/{}".format(h_file_loc.getAbsolutePath(), HEADER_NAME)
    h_file = open(h_file_path, "wt")  # pylint: disable=consider-using-with
    if not c_file or not h_file:
        print("Can't open file")
        return

    h_filename = HEADER_NAME
    upper_h_name = h_filename.replace(".", "_").upper()
    c_file.write("#include <{}>\n\n".format(h_filename))
    c_file.write(
        "// AUTOGENERATED from halucinator export_calling_stubs.py edit at own risk\n"
    )
    c_file.write(
        "// If something is wrong recommend fixing in ghidra and rerunning\n\n"
    )

    h_file.write("#ifndef {}\n".format(upper_h_name))
    h_file.write("#define {}\n\n".format(upper_h_name))
    h_file.write(
        "// AUTOGENERATED from halucinator export_calling_stubs.py edit at own risk\n"
    )
    h_file.write(
        "// If something is wrong recommend fixing in ghidra and rerunning\n\n"
    )
    h_file.write("#include <stdint.h>\n\n")
    macros = write_type_macros(h_file, fmgr, dt_manager)
    write_functions(c_file, h_file, fmgr, macros)

    h_file.write("#endif\n")

    print("Wrote C file to {}".format(c_filename))
    print("Wrote H file to {}".format(h_file_path))


main()
