# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

"""
    Import this file and yaml to change yaml's default integer writing to hex
    Useage:
    import hexyaml
    import yaml

    use yaml as normal
"""

import yaml


def hexint_presenter(dumper, data):
    return dumper.represent_int(hex(data))


yaml.add_representer(int, hexint_presenter)
