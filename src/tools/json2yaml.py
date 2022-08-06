# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import json
import os

import yaml


def json2yaml(json_file):
    yaml_file = os.path.splitext(json_file)[0] + ".yaml"
    with open(json_file, "rb") as jfile:
        with open(yaml_file, "wb") as yfile:
            yaml.safe_dump(json.load(jfile), yfile, allow_unicode=True)


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("-i", dest="in_file", required=True, help="Json file to convert")
    args = p.parse_args()
    json2yaml(args.in_file)
