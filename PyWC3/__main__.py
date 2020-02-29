from argparse import ArgumentParser
from PyWC3 import Map
import sys
import os
import json
from __version__ import __version__ as version
def create_arg_parser():
    """Create and initialize an argument parser object"""
    parser = ArgumentParser(description="Python Warcraft III Mapscript Generator.")
    parser.add_argument("map", metavar="map", type=str,
                        help="The map folder in the maps directory.",
                        nargs="?", default="")
    parser.add_argument("--build", help="Generate lua code and build the map in the dist directory.",
                        dest="build",action="store_true")
    parser.add_argument("--debug", help="Print python ast tree before code.",
                        dest="debug", action="store_true")
    parser.add_argument("--run", help="Run Warcraft III.",
                        dest="run",action="store_true")
    parser.add_argument("--edit", help="Run Warcraft III World Editor.",
                        dest="edit", action="store_true")
    parser.add_argument("--update-jass", help="Translate the jass source files. Do this when a new WC3 version comes out",
                        dest="jass", action="store_true")
    parser.add_argument("--init-python", help="Generate the python source file.",
                        dest="initpy", action="store_true")
    parser.add_argument("--mpq", help="Save map as mpq.",
                        dest="mpq", action="store_true")
    return parser

def main():
    """Entry point function to the translator"""
    # with open("setup.py")
    print("PyWC3 version {} by Bart Limburg\n".format(version))
    try:
        with open("config.json","r") as f:
            cfg = json.load(f)
    except:
        raise Exception("Configuration file config.json not found in location: {}".format(os.getcwd()))
    parser = create_arg_parser()
    argv = parser.parse_args()
    mapfile = argv.map
    if mapfile:
        m = Map(mapfile,show_ast=argv.debug or cfg['SHOW_AST'],save_mpq=argv.mpq or cfg['SAVE_AS_MPQ'])

        m.generate_definitions_file()

        if(not (argv.build or argv.run or argv.edit or argv.initpy)):
            print("Incorrect usage: please pass --build, --run or --edit as follows: python PyWC3 map.w3x --build --run")
        if argv.initpy:
            m.generate_python_source()
        if argv.build:
            print("Building map {}".format(mapfile))
            m.build()

        if argv.run:
            print("Running Warcraft III <{}>".format(m.file))
            m.run()

        if argv.edit:
            print("Running Warcraft III World Editor <{}>".format(m.file))
            m.edit()
            m.generate_definitions_file()
    elif argv.jass:
        from PyWC3 import Jass
        Jass.convertCommonJ()
        Jass.convertCommonAI()
        Jass.convertBlizzardJ()
    else:
        print("Incorrect usage: please pass a mapfile to the script: python PyWC3 map.w3x --build --run")

if __name__ == "__main__":
    sys.exit(main())
