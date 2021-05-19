# Diabase Engineering H-Series Cura Extension

## Functionality
This is a Python-based post-processing script that can be installed and run with Cura 4.9 and above. This extension modifies G-Code that is outputted by cura to allow it to be used by a Diabase Engineering H-Series machine.

### Current Functions:
* Deletes the opening T# commands
* Deletes all M82 commands
* Changes G10 P# commands to G10 P(#+1) commands
* Replaces M104 T# S$$$ commands with G10 P(#+1) S$$$ R($$$-50) commands
* Removes all remaining T# commands
* Comments out all M109 commands

### Future Functions
* Remove post-toolchange Retraction
* Replace post-toolchange Extrusions with “G11”
* Replace final retraction with “G10”
* Swap XY move with Z move after toolchange.
* Pre-heat tools before use

## Instalation
Download the .py file directly, then save it. 

## Instructions for use
