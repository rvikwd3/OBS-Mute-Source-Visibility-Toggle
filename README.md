# OBS Mute Source Visibility Toggle

This repo contains [a script](https://github.com/rvikwd3/OBS-Mute-Source-Visibility-Toggle/blob/master/obs_mute_source_visibility_toggle.py) to toggle the visibility of a chosen OBS Studio Source **in the current scene** based on the "mute" state of an OBS Studio audio source. The state is automatically read by a Python script which then toggles the OBS Display Source.

## Script Installation and Setup
The script only works with OBS Studio versions 21.x and later. If you have an older version you will need to update.

### Python Configuration
As of this writing OBS seems to have issues with the newest versions of Python (3.7+). This script was developed and tested using Python 3.6.8.

You need [Python 3.6](https://www.python.org/downloads/) installed on your PC. The bit version of your Python installation must match your OBS installation - use "x86-64" for 64 bit OBS Studio and "x86" for 32 bit OBS Studio. In the menu in OBS Studio, go to `Tools` and then `Scripts`. Then in the "Python Settings" tab, set the path to point to the Python installation folder.

Add the mute source visibility toggle script to the "Scripts" window using the '+' icon on the bottom left. Select the script in the "Loaded Scripts" panel, and if everything is set up correctly you should see the script properties show up on the right.

### Script Options
Fill out the configuration settings in the script properties:

* **Audio Source**: the audio source to monitor for changes to its 'mute' status.
* **Video Source**: the display source to toggle visibility on changing the audio source 'mute' status.

For added transition effects you can set `Show Transition` and `Hide Transition` effects of the Display Source Scene Item.

## License
The contents of this repository are licensed under the terms of the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

### Acknowledgements
Based off of [Dave Madison's](https://github.com/dmadison) [OBS-Mute-Indicator](https://github.com/dmadison/OBS-Mute-Indicator) script.
