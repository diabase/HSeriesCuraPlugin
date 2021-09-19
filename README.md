# Diabase Engineering H-Series Cura Extension

## Functionality
This is a Python-based post-processing script that can be installed and run with Cura 4.9 and above. This extension modifies G-Code that is outputted by Cura to allow it to be used by a Diabase Engineering H-Series machine.

### Current Functions:
* Deletes the opening T# commands
* Deletes all M82 commands
* Changes G10 P# commands to G10 P(#+1) commands
* Replaces M104 T# S$$$ commands with G10 P(#+1) S$$$ R($$$-50) commands
* Removes all remaining T# commands
* Comments out all M109 commands
* Remove post-tool-change Retraction
* Replace post-tool-change Makeup with “G11”
* Replace pre-tool-change retraction with “G10”
* Swap XY move with Z move after tool-change.
* Pre-heat tools before use

## Installation Instructions
* Download the HSeriesPost.py file directly, then save it. 
* Open Cura(version 4.9 or later)
* Click the "Help" menu item on the far right-hand side of the top toolbar.
* Click "Show Configuration Folder".
* Locate the folder called "scripts", and open it. If there is no folder with this name, create one in the configuration folder.
* Place HSeriesPost.py into the scripts folder.
* Restart Cura.

## Instructions for use
* Click "Extensions" in the top toolbar
* Click "Post Processing"
* Click "Modify G-Code"
* Underneath the heading "Post Processing Scripts", locate and click "Add a script"
* Locate and click "Diabase Post Processor" in the dropdown
* Check desired settings in the right panel, then close the window.
* The script should now process the G-Codes produced by Cura. 

## Known Bugs/issues
* In theory, a perfect layer split could cause some functions in two to break. Based on where I have seen layer breaks, it seems like a layer break in this place would be impossible, but there would be no way to be sure without a much larger sample size. If this were to happen, a comment reading ";LAYER PROCESSING ERROR" Would be added in.
* The extension has not been extensively tested
