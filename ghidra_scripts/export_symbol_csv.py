# Exports function names in ghidra project to CSV file suitable for use with HALucinator
# @category Halucinator
# @keybinding
# @menupath
# @toolbar
"""
Exports function names in ghidra project to CSV file suitable for use with HALucinator
"""


if __name__ == "__main__":
    # pylint: disable=undefined-variable
    functionMgr = currentProgram.getFunctionManager()
    monitor.initialize(functionMgr.getFunctionCount())
    filename = askString(
        "Function Symbol Table CSV Output File Name",
        "Enter Full Path for where to save Function Symbol Table Output File Name",
    )
    with open(filename, "w") as outfile:
        function = getFirstFunction()
        while function is not None:
            monitor.checkCanceled()
            monitor.incrementProgress(1)
            name = function.getName()
            startAddr = function.getEntryPoint().offset
            endAddr = (
                function.getEntryPoint().offset + function.getBody().getNumAddresses()
            )

            # pylint: disable=consider-using-f-string
            outfile.write("%s, 0x%x, 0x%x\n" % (name, startAddr, endAddr))
            function = getFunctionAfter(function)
