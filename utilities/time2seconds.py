import string

import time

def time2seconds(time_string):
  """Convert a time string of the format HH:MM:SS or HH:MM to a timestamp in seconds."""
  if len(time_string) != 8 and len(time_string) != 5: # Check if length is consistent with HH:MM:SS or HH:MM respectively.
    raise ValueError("Time given to time2seconds() was not a time_string.")
  for character in time_string:
    if character in string.ascii_letters:
      raise ValueError("Time given to time2seconds() was not a time_string.")
  if len(time_string) == 8:
    time_elements = time.strptime(time_string,"%H:%M:%S")
    hours2minutes = time_elements.tm_hour * 60
    minutes2seconds = hours2minutes + time_elements.tm_min
    seconds = (minutes2seconds * 60) + time_elements.tm_sec
    return seconds
  elif len(time_string) == 5:
    time_elements = time.strptime(time_string, "%H:%M")
    hours2minutes = time.elements.tm_hour * 60
    minutes2seconds = hours2minutes + time_elements.tm_min
    seconds = minutes2seconds * 60
    return seconds
  else:
    raise ValueError("'time_string' was proper length and contained no alphanumeric characters, but was somehow not the proper length when it is checked again to determine which routine should be used to process the string.")
