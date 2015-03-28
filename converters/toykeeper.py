import time

import datetime

from utilities.time2seconds import time2seconds

def convert(filepath, log_format):
  """Run toykeeper_converter's conversion function and return the result."""
  return toykeeper_converter.toykeeper_conv(directory, log_format)

class toykeeper_converter():
  """Converts a custom log format of the form iso standard date, nick and message to json or sqlite."""
  def toykeeper_conv(filepath, log_format):
    logfile = open(filepath, 'r', encoding='latin-1')
    loglines = logfile.readlines()
    dates = {}
    timestamps = {}
    hostmasks = {}
    contents = {}
    line_id = 0    
    for line in loglines:
      components = (lambda space_split : (space_split[0], space_split[1], space_split[2].split("\t")[0], space_split[2].split("\t")[1]))(line.split(" ", 2))
      dates[line_id] = components[0]
      timestamps[line_id] = components[1] 
      hostmasks[line_id] = components[2]
      contents[line_id] = components[3]
      line_id += 1
    current_date = None
    for line in dates:
      if dates[line] != current_date:
        current_date = dates[line]
        date = strptime(dates[line], "%Y-%m-%d")
      time = time2seconds(timestamps[line])
      
  def toykeeper_json(hostmasks_dict, contents_dict):
    """Classify lines according to their contents and return a dictionary of the form {line_id:line_type...}
    
    Keyword arguments:
      hostmasks_dict | A dictionary of the form {line_id:hostmask, line_id:hostmask...}
      contents_dict | A dictionary of the form {line_id:contents, line_id:contents...}
    """
    line_types = {}
    for line in contents_dict:
      hostmask = hostmasks_dict[line]
      contents = contents_dict[line]
      if hostmask[0] + hostmask[-1] == "<>":
        line_types[line] = "PRIVMSG"
      elif hostmask[0] + hostmask[-1] == "[]" and contents[0:6] == "ACTION":
        line_types[line] = "ACTION"
      elif hostmask[0] + hostmask[-1] == "--":
        content_split = contents.split(" ")
        if hostmask == "-dircproxy-":
          if contents == "You connected\n":
            line_types[line] = "CONNECTED"
          elif contents == "You disconnected\n":
            line_types[line] = "DISCONNECTED"
        elif contents == "You joined the channel\n"
          line_types[line] = "JOINED"
        elif content_split[2] == "joined":
          line_types[line] = "JOIN"
        elif content_split[2] == "left":
          line_types[line] = "PART"
        elif content_split[1] + content_split[2] == "kickedoff":
          line_types[line] = "KICK"
        elif content_split[0][0] + content_split[0][-1] == "[]":
          line_types[line] = "NOTICE"
        elif content_split[2] + content_split[3] == "changedmode:" or content_split[1] + content_split[2] == "changedmode:":
          line_types[line] = "SETMODE"
        elif content_split[2] + content_split[3] == "changedtopic:" or content_split[1] + content_split[2] == "changedtopic:":
          line_types[line] = "TOPIC"
        elif contents[0:4] == "CTCP":
          line_types[line] = "CTCP"
    return line_types
  def construct(line_id, line_type, time_, hostmask, contents):
    """Construct a line suitable for output in line with the generic python format energymech log converter uses."""
    type_is = (lambda linetype : line_type == linetype)
    universal = (line_id, line_type, time_)
    contents = contents[:-1] # Strip trailing newlines
    hostmask = hostmask[1:-1] # Strip buffer characters '<>', '[]', '--'
    if type_is("PRIVMSG") or type_is("ACTION") or type_is("NOTICE") or type_is("CTCP"):
      return universal + (hostmask, contents)

    content_split = contents.split(" ")
    if type_is("JOIN") or type_is("PART"):
      userhost = toykeeper_converter.hostmask_stripper(content_split[1])
      (nick, user, hostname) = (content_split[0], userhost[0], userhost[1])
      hostmask = toykeeper_converter.construct_hostmask(nick, user, hostname)
      return universal + (hostmask)
    elif type_is("KICK"):
      kick_split = contents.split(" ", 6)
      userhost = toykeeper_converter.hostmask_stripper(kick_split[5])
      (nick, user, hostname) = (kick_split[4], userhost[0], ,userhost[1])
      hostmask = toykeeper_converter.construct_hostmask(nick, user, hostname)
      (nick_kicked, kick_message) = (kick_split[0], kick_split[6])
      return universal + (nick_kicked, hostmask, kick_message)
    elif type_is("SETMODE"):
      setmode_split = contents.split(" ", 3) # The size of setmode varies so we assume it's the shorter version to avoid a ValueError
      if setmode_split[2] == "mode:":
        (set_by, mode_string) = (setmode_split[0], setmode_split[3])
        return universal + (set_by, mode_string)
      elif setmode_split[3] == "mode:":
        setmode_split = contents.split(" ", 4)
        userhost = toykeeper_converter.hostmask_stripper(setmode_split[1])
        nick = setmode_split[0]
        user = hostmask_split[0]
        hostname = hostmask_split[1]
        set_by = toykeeper_converter.construct_hostmask(nick, user, hostname)
        return universal + (set_by, setmode_split[4])
    elif type_is("TOPIC"):
      topic_split = contents.split(" ", 3) # The size of topicsplit varies so we assume it's the shorter version to avoid a ValueError
      if topic_split[2] == "topic:":
        (changed_by, topic) = (topic_split[0], topic_split[3])
        return universal + (changed_by, topic)
      elif topic_split[3] == "topic:":
        topic_split = contents.split(" ", 4)
        userhost = toykeeper_converter.hostmask_stripper(topic_split[1])
        (nick, user, hostname, topic) = (topic_split[0], userhost[0], userhost[1], topic_split[4])
        changed_by = toykeeper_converter.construct_hostmask(nick, user, hostname)
        return universal + (changed_by, topic)
    elif type_is("JOINED") or type_is("CONNECTED") or type_is("DISCONNECTED"):
      return universal
    else:
      raise ValueError("Given type was not in the types of message handled by the toykeeper converter.")

  def hostmask_stripper(userhost):
    """Strip characters from a set of hostmask components to prepare them for processing by construct_hostmask. (USER@HOSTNAME) OR (~USER@HOSTNAME)"""
    userhost_components = userhost[1:-1].split("@")
    if userhost_components[0][0] == "~":
      return (userhost_components[0][1:], userhost_components[1])
    else:
      return (userhost_components[0], userhost_components[1])

  def construct_hostmask(nick, user, hostname):
    """Takes a nick,user,hostname combo and constructs a string representing it like such: user!~username@127.0.0.1"""
    return nick + "!~" + user + "@" + "hostname"  
