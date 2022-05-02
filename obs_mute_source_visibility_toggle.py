#
# Project     OBS Mute Source Visibility Toggle
# @author     Ravikiran Kawade
# @link       github.com/rvikwd3/OBS-Mute-Source-Visibility-Toggle
# @license    GPLv3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import obspython as obs

# ------------------------------------------

# Script Properties

debug = True
audio_source_name = "deselected"  # Audio source name to monitor
video_source_name = "deselected" # Source to toggle on Audio source mute/unmute

# Global Variables

sources_loaded = False  # Set to True when sources are loaded
callback_name = None  # Source name for the current muted callback

# ------------------------------------------

# Utilities

# Print to script log
def debug_print(*input):
  if debug == True:
    print(*input)

# Return a list of audio sources
def list_audio_sources():
  audio_sources = []
  sources = obs.obs_enum_sources() # Needs to be released

  for source in sources:
    if obs.obs_source_get_type(source) == obs.OBS_SOURCE_TYPE_INPUT:
			# output flag bit field: https://obsproject.com/docs/reference-sources.html?highlight=sources#c.obs_source_info.output_flags
      capabilities = obs.obs_source_get_output_flags(source)
      has_audio = capabilities & obs.OBS_SOURCE_AUDIO

      if has_audio:
        audio_sources.append(obs.obs_source_get_name(source))
  obs.source_list_release(sources)  # Release source list
  return audio_sources

# Return a list of video sources
def list_video_sources():
  video_sources = []
  sources = obs.obs_enum_sources() # Needs to be released

  for source in sources:
    if obs.obs_source_get_type(source) == obs.OBS_SOURCE_TYPE_INPUT:
			# output flag bit field: https://obsproject.com/docs/reference-sources.html?highlight=sources#c.obs_source_info.output_flags
      capabilities = obs.obs_source_get_output_flags(source)
      has_video = capabilities & obs.OBS_SOURCE_VIDEO

      if has_video:
        video_sources.append(obs.obs_source_get_name(source))
  obs.source_list_release(sources)  # Release source list
  return video_sources

# ------------------------------------------

# Video display toggle functions

# Set video source visibility
def set_source_visibility(sourceName, visibility):
  current_scene = obs.obs_frontend_get_current_scene()
  source = obs.obs_get_source_by_name(sourceName) # Needs to be released
  if source is None:  # Check if source exists
    debug_print(f"Could not get source \"{sourceName}\"")
    return  # Does the empty source need to be released before returning early?

  scene = obs.obs_scene_from_source(current_scene)  # Needs to be released
  scene_item = obs.obs_scene_find_source_recursive(scene, sourceName)
  
  if scene_item:
    debug_print(f"Found sceneItem for source name \"{sourceName}\"")
    scene_item_visibility_state = obs.obs_sceneitem_visible(scene_item)
    obs.obs_sceneitem_set_visible(scene_item, visibility) # Set scene item visibility
  else:
    debug_print(f"Could not find source \"{sourceName}\" in current scene")

  obs.obs_scene_release(scene)  # Release scene object
  obs.obs_source_release(source)  # Release source object
  
# ------------------------------------------

# Mute indicator functions

# Get mute state for given audio source
def get_muted_state(sourceName):
  source = obs.obs_get_source_by_name(sourceName) # Needs to be released
  if source is None:
    return None
  muted = obs.obs_source_muted(source)
  obs.obs_source_release(source)  # Release source
  return muted

# When mute state changes, toggle display source visibility
def mute_toggle_callback(calldata):
  debug_print("Mute state toggled")
  muted_state = obs.calldata_bool(calldata, "muted")  # True if muted, False if not

  if muted_state: # Set video source visible on mute
    set_source_visibility(video_source_name, True)
  else: # Set video source not visible on mute
    set_source_visibility(video_source_name, False)

# Add a callback as signal_handler for source Mute event
def create_mute_toggle_callback(sourceName):
  global callback_name
  if sourceName is None or sourceName == callback_name:
    # debug_print(f"cb name: {callback_name} | sourceName: {sourceName} | Audio source hasn't changed or callback is already set")
    return False  # Audio source hasn't changed or callback is already set
  if callback_name is not None: # Audio source has a previously set callback (audio source has changed)
    # debug_print(f"cb name: {callback_name} | sourceName: {sourceName} | Audio source has changed, remove the previous callback")
    remove_mute_toggle_callback(callback_name)  # Remove previously set callback
  if sourceName == "deselected":  # Audio source is deselected, stop looking for more sources (we still want previous callback to be removed)
    # debug_print(f"cb name: {callback_name} | sourceName: {sourceName} | Audio source is deselected, return True")
    return True

  source = obs.obs_get_source_by_name(sourceName) # Needs to be released
  if source is None:
    if sources_loaded:
      debug_print("ERROR: Could not create callback for ", sourceName)
    return False  # Sources are still loading, wait until next OBSTimer cycle

  # Create callback for sourceName
  handler = obs.obs_source_get_signal_handler(source)
  obs.signal_handler_connect(handler, "mute", mute_toggle_callback)
  callback_name = sourceName  # Save name for future reference
  debug_print("Added callback for \"{:s}\"".format(obs.obs_source_get_name(source)))

  # Get initial state and accordingly set source

  obs.obs_source_release(source)  # Release source
  return True

# Remove the callback as signal_handler for source Mute event
def remove_mute_toggle_callback(sourceName):
  global callback_name
  if sourceName is None or sourceName == "deselected":
    return False  # No callback is set
  
  source = obs.obs_get_source_by_name(sourceName) # Needs to be released
  if source is None:
    debug_print("ERROR: Could not create callback for ", sourceName)
    return False

  handler = obs.obs_source_get_signal_handler(source)
  obs.signal_handler_disconnect(handler, "mute", mute_toggle_callback)
  debug_print("Removed callback for \"{:s}\"".format(obs.obs_source_get_name(source)))
  callback_name = None
  
  obs.obs_source_release(source)  # Release source
  return True

# Try to create a callback for audio_source_name
# Is called by OBSTimer repeatedly until all the sources are loaded and the callback is set
def source_loading():
  global sources_loaded
  source = obs.obs_get_source_by_name(audio_source_name)  # Needs to be released | Property-defined audio_source_name
  if (source and create_mute_toggle_callback(audio_source_name)) or audio_source_name == "deselected":
    sources_loaded = True # Sources have been loaded, no need to reload source_loading
    obs.remove_current_callback() # Remove this source_loading timer
  else:
    debug_print("Waiting to load sources...")
    debug_print("Current audio_source_name: ", audio_source_name)

  obs.obs_source_release(source)

# ------------------------------------------

# OBS Script Functions

def script_description():
  return "<b>OBS Mute Indicator Source Script</b>" + \
    "<hr>" + \
    "Python script for checking if the \"mute\" state of an audio source is muted" + \
    "<br/>" + \
    "On toggling the mute state, an Image is toggled as well" + \
    "<br/><br/>" + \
    "Ravikiran Kawade" + \
    "<br/>" + \
    "github.com/rvikwd3"

def script_load(settings):
  obs.timer_add(source_loading, 10)
  debug_print("OBS Mute Indicator Source Script Loaded")

def script_unload():
  obs.timer_remove(source_loading)
  remove_mute_toggle_callback(callback_name)  # Remove the callback if it exists
  debug_print("OBS Mute Indicator Source Script Unloaded")

def script_properties():
  props = obs.obs_properties_create()
  audio_sources = list_audio_sources()  # Generate list of audio sources
  video_sources = list_video_sources()  # Generate list of video sources
  audio_source_list = obs.obs_properties_add_list(props, "audio_source", "Audio source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
  video_source_list = obs.obs_properties_add_list(props, "video_source", "Video source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

  # Add audio source names as well as an empty one
  obs.obs_property_list_add_string(audio_source_list, "", "deselected")
  for audio_source_name in audio_sources:
    obs.obs_property_list_add_string(audio_source_list, audio_source_name, audio_source_name)

  # Add video source names as well as an empty one
  obs.obs_property_list_add_string(video_source_list, "", "deselected")
  for video_source_name in video_sources:
    obs.obs_property_list_add_string(video_source_list, video_source_name, video_source_name)

  # Add testing buttons and debug toggle
  obs.obs_properties_add_bool(props, "debug", "Print Debug Messages")

  return props

def script_update(settings):
  global debug, audio_source_name, video_source_name

  debug = obs.obs_data_get_bool(settings, "debug")  # For printing debug messages
  audio_source_name = obs.obs_data_get_string(settings, "audio_source") # Setting a new source requires creating a new callback
  video_source_name = obs.obs_data_get_string(settings, "video_source") # Update global var video_source_name with updated dropdown selection

  if sources_loaded:
    create_mute_toggle_callback(audio_source_name)  # Create a mute_toggle callback for new audio_source_name