import os
_VERSION = "1.0.0"
# link to the correct paths for the warcraft executables
WAR3_FOLDER = "E:\\Games\\Warcraft III"
WAR3_EXE = os.path.join(WAR3_FOLDER,"x86_64\\Warcraft III.exe")
WE_EXE = os.path.join(WAR3_FOLDER,"x86_64\\World Editor.exe")

# place your python source files in this directory. The python file matching your map is the script entry point
PYTHON_SOURCE_FOLDER = "pysrc"

# place your maps in the following directory
MAP_FOLDER = "maps"

# the built maps will be output in the dist directory
DIST_FOLDER = "dist"

# the folder where the common.j / blizzard.j / common.ai are located
JASS_FOLDER = "jass"

# developer debugging for python to lua translation
SHOW_AST = False