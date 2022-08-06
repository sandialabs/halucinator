# This script prints the symbol table functions to a yaml file. Right now it only prints functions, change if you want full symbol table.
# @Christopher Wright
# @category Binalysis
# @keybinding
# @menupath
# @toolbar

import ghidra, java
from java.awt import Color
import time, copy
from collections import OrderedDict

SEC_TO_TIMEOUT = 30


def print_program_info(currentProgram):
    program_name = currentProgram.getName()
    creation_date = currentProgram.getCreationDate()
    language_id = currentProgram.getLanguageID()
    compiler_spec_id = currentProgram.getCompilerSpec().getCompilerSpecID()
    print(
        "Program Info:\tbinary name: %s\t\tArchitecture_Compiler: \
          %s_%s\tCreation Date:(%s)\n"
        % (program_name, language_id, compiler_spec_id, creation_date)
    )


if __name__ == "__main__":
    print_program_info(currentProgram)
    functionMgr = currentProgram.getFunctionManager()
    monitor.initialize(functionMgr.getFunctionCount())
    filename = askString(
        "Function Symbol Table Yaml Output File Name",
        "Enter Full Path for where to save Function Symbol Table Output File Name (yaml format)",
    )
    with open(filename, "w") as outfile:
        outfile.write("functions:\n")
        function = getFirstFunction()
        while function is not None:
            monitor.checkCanceled()
            monitor.incrementProgress(1)
            name = function.getName()
            if "task" in name:
                startAddr = hex(int(function.getEntryPoint().toString(), 16))
                endAddr = str(
                    hex(
                        int(function.getEntryPoint().toString(), 16)
                        + function.getBody().getNumAddresses()
                    )
                ).rstrip("L")
                # this prints the start and end address to then run through log2graph.py
                outfile.write(
                    "  - start_addr: %s\n    end_addr: %s\n    name: %s\n"
                    % (startAddr, endAddr, name)
                )
                # this prints the halucinator file for printing the link register
                outfile.write(
                    " - class: halucinator.bp_handlers.generic.armv7m_param_log.ARMv7MEABILogger\n   registration_args: {ret_val: null, no_intercept: true, lr: true}\n   addr:  %s\n   function: %s\n"
                    % (startAddr, name)
                )
            function = getFunctionAfter(function)
            # print_program_info(currentProgram)
    numSymbols = currentProgram.getSymbolTable().getNumSymbols()
    monitor.initialize(numSymbols)
    filename = askString(
        "Symbol Table CSV Output File Name",
        "Enter Full Path for where to save Symbol Table Output File Name",
    )
    with open(filename, "w") as outfile:
        for symbol in currentProgram.getSymbolTable().getDefinedSymbols():
            monitor.checkCanceled()
            monitor.incrementProgress(1)
            if symbol.getSymbolType() == ghidra.program.model.symbol.SymbolType.FUNCTION:
                outfile.write("%s, %s\n" % (symbol.name, symbol.address))
