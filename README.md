# PyWC3 - Python for Warcraft III
PyWC3 is a comprehensive method for Warcraft III modding using python. The code is translated to lua but allows us to 
 use the more modern features of python (for specifics see [pythonlua](http://www.github.com/Blimba/python-lua/)). 
 Summary of features (when using advised software):
 - Code Completion & Syntax highlighting of your favourite IDE
 - Support for maps as "folders" as well as "mpq"
 - Quick maptesting through command line interface
 - Expanding list of modules in the standard library (I welcome people to develop missing modules by pull requests!)
 
## Requirements
- Python 3.7 or higher.
- [pythonlua](http://www.github.com/Blimba/python-lua/) version 1.2.0 or higher 
## Setting up
It is highly recommended to install python using a distribution such as 
[Anaconda](https://www.anaconda.com/distribution/), which comes preinstalled with packages required by this project
(except pythonlua, which you will need to install manually). For code completion, I advise using a modern IDE such as 
[PyCharm](https://www.jetbrains.com/pycharm/). 
In addition, you will be able to use IPython, which is one way of quickly building and testing custom Warcraft III maps 
created with this project. Please make sure that the python program is accessible in the `PATH` variable 
([how?](https://geek-university.com/python/add-python-to-the-windows-path/)).

In addition, [pythonlua](http://www.github.com/Blimba/python-lua/) is required for translating python code to lua, 
the scripting language used by Warcraft III. Install the pythonlua project using the instructions in the project, 
 or simply copy the folder `pythonlua`from it to the folder `PyWC3`.

To start a new map project, open the World Editor (with a new map, or a map with only GUI triggers) like you normally 
would, go to `Scenario > Map Options` and set `Scripting Language` to Lua. Save your map, making sure to select 
`Warcraft III Scenario Folder (- Expansion)` as the format. Save this map to the `maps/` folder. Alternatively,
you can use the `Warcraft III Scenario (- Expansion)` (MPQ) format as long as you have the 
[MPQEDitor.exe](http://www.zezula.net/en/mpq/download.html) in the `mpqeditor` folder.


### config.json  

The config.json file contains file references used by the project. It has the general structure:  
```json
{
    "WAR3_EXE": "C:\\Games\\Warcraft III\\x86_64\\Warcraft III.exe",
    "WE_EXE": "C:\\Games\\Warcraft III\\x86_64\\World Editor.exe",
    "WINDOWMODE": "windowed",

    "MPQ_EXE": "mpqeditor\\mpqeditor.exe",
    "SAVE_AS_MPQ": true,

    "MAP_FOLDER": "maps",
    "DIST_FOLDER": "dist",
    "JASS_FOLDER": "jass",

    "PYTHON_SOURCE_FOLDER": "pysrc",
    "DEF_SUBFOLDER": "df",

    "SHOW_AST": false
}
``` 
where `WAR3_EXE` and `WE_EXE` point to the warcraft executables. `WINDOWMODE` can be fullscreen or windowed to use as
launch mode for Warcraft III. `MAP_FOLDER` is the folder where the original map can be found, which should be saved as 
a folder format. `DIST_FOLDER` is where the built map files can be found after PyWC3 has been executed. `JASS_FOLDER` 
contains the Blizzard Jass code definitions, which help us with code completion. Every new version of Warcraft III 
requires us to [translate these](#jass-translate) to make sure our definitions are up to date.

`MPQ_EXE` points to the location of the [MPQEDitor.exe](http://www.zezula.net/en/mpq/download.html) which we can use
to load/save the map in mpq format. Loading folder/mpq is automatic based on the type we supply, and the way the map is
saved depends on the `SAVE_AS_MPQ` flag.

`PYTHON_SOURCE_FOLDER` contains all of the maps code, as well as standard libraries which can be included into the 
map script. The entrypoint for the python code is {mapfile}.py, where {mapfile} is the name of the map file. This script
in its most basic shape (Hello world) looks like this:

```python
from std.index import *
            
            
def test():
    print("hello world")
    
    
AddScriptHook(test, MAIN_AFTER)
```
The script file can be generated automatically by using a command (see [Usage](#Usage)).

The `DEF_SUBFOLDER` is a folder within `PYTHON_SOURCE_FOLDER` where the definitions of blizzard functions are located.
The scripts are not included in the build, and are used only for code completion. `SHOW_AST` is used by the pythonlua
translator to print the abstract syntax tree. Can be used for debugging purposes if the lua code does not execute like
the python code would.

## Usage
### As a python application
Run a console / terminal (such as cmd.exe) and make sure the current working directory is in the main folder. Run PyWC3
using the following command: `python PyWC3 mapname.w3x --argv` where `mapname.w3x` is the folder name, and `--argv` is as follows:
- `--build` generate the new map files and script in the `DIST_FOLDER`
- `--run` start Warcraft III and run the map
- `--edit` start the Warcraft III World Editor to change all things except for the python script
- `--init-python` generate the map python script file when starting a new map
- `--update-jass` update the jass definitions in the jass files in the `JASS_FOLDER`
- `--debug` same as setting `SHOW_AST` to `true` in config.json.
  
argv can be combined to do multiple things, such as: `python PyWC3 mapname.w3x --build --run`
No matter what argv are added, the script will always read the original war3map.lua script file to check for World Editor
generated objects, which can then be used in the python scripts. The python script including the definitions can be 
imported by:
```python
from df.mapname import *  #mapname needs to be replaced by the actual map filename.
```
### As a module in IPython
To start IPython, run the IPython.bat script, which automatically imports PyWC3. Then, use the `Map()` module:
```python
m = Map("mapname.w3x")
m.build()
m.run()
m.edit()
m.generate_python_source()
m.generate_definitions_file()
```
The methods on the Map() object are explained above.

## jass translate

Whenever a new Warcraft III is released, we should update our function / constant defintions. 
This can be done by running the python script:

```
python PyWC3 --update-jass
```

without supplying a map filename to the script. Alternatively, in IPython, run:
```python
Jass.convert_all()
```
# Code completion
A very important part of modern programming is to have access to code completion. The translated jass code explained 
above is available to include in python only for code completion (obviously the functionality only exists within wc3).
To make code completion work, we have to include the translated definitions files into our python script:
```python
from df.commonj import *
from df.blizzardj import *
from df.commonai import *
```
After these three lines of code have been added to our project, our code completion will work in modern IDEs, such as
for example [PyCharm](https://www.jetbrains.com/pycharm/).

# Coding Features
- Hooking user functions to the mapscript by using `AddScriptHook(func, where)` where `where` can be CONFIG_BEFORE, 
CONFIG_AFTER, MAIN_BEFORE or MAIN_AFTER. BEFORE or AFTER means before or after the blizzard generated code runs.
The following import is required for the hook:
```python
from std.index import *
```
- Replacing the blizzard generated code can be done as follows: 
```python
def replaced():
    #user code goes here
    pass

main = replaced
# or
config = replaced
```
- A Timer module, which is very simple to use:
```python
from std.index import *
from std.timer import Timer
def timeout():
    t = Timer.get_expired()
    print(t.data)
    t.destroy()

def test():
    t = Timer()
    t.data = 5
    t.start(1.0,timeout)
AddScriptHook(test,MAIN_AFTER)
```
- A Unit module

Here is a bit of example code. Full documentation in progress...
```python
u = Unit(0, "hfoo", 0, 0)  # create a unit for player 0 (red) at x: 0, y: 0.
u.name = "My Footy"  # change the unit name
print(u.name)  # or print it
u.max_hp = 500
u.life = 50

# make a subclass that has a function that is called upon death
class EventUnit(Unit):
    def on_death(self):
        print(self.name,"has died")

u2 = EventUnit(0, "hpea", 128, 0)  # create a unit with an on_death event
u2.on_ordered = lambda self: print(self.name, "has been ordered")  # add an event for ordering

```