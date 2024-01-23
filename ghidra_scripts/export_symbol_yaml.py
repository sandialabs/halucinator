#This script prints the symbol table to file to a yaml file used by HALucinator.
#@category Halucinator
#@keybinding 
#@menupath 
#@toolbar 

import ghidra, java
from java.awt import Color
import time, copy
from collections import OrderedDict
SEC_TO_TIMEOUT = 30



if __name__ == "__main__" :
  functionMgr = currentProgram.getFunctionManager()
  monitor.initialize(functionMgr.getFunctionCount())
  filename = askString("Function Symbol Table Yaml Output File Name", "Enter Full Path for where to save Function Symbol Table Output File Name (yaml format)")
  with open(filename, "w") as outfile:
    outfile.write("symbols:\n")
    function = getFirstFunction()
    while function is not None:
      monitor.checkCanceled()
      monitor.incrementProgress(1)
      name = function.getName()
      startAddr = hex(int(function.getEntryPoint().toString(), 16))
      outfile.write("  %s: %s\n" %(startAddr, name))
      function = getFunctionAfter(function)
        # print_program_info(currentProgram)
  