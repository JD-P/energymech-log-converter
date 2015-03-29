import json

import time

from datetime import timedelta

from calendar import timegm

from utilities.time2seconds import time2seconds


def convert(filepath, log_format, utc_offset=None):
  """Run ToyKeeperConverter's conversion function and return the result."""
  return ToyKeeperConverter.toykeeper_conv(filepath, log_format, utc_offset)


class ToyKeeperConverter():
  """Converts a custom log format of the form iso standard date, nick and message to json or sqlite."""
  def toykeeper_conv(cls, filepath, log_format, utc_offset):
    logfile = open(filepath, 'r', encoding='latin-1')
    loglines = logfile.readlines()
    line_id = 0
    current_date = loglines[0].split(" ")[0]
    queue = output_queue()
    queue.add_iter(iter(("{\n", "\n}")))
    queue.add(0)
    queue.tick()
    line = loglines[0]

    def process_line(line_id, line, offset):
      components = (lambda space_split : (space_split[0], space_split[1], 
                                          space_split[2].split("\t")[0], 
                                          space_split[2].split("\t")[1])) \
                                          (line.split(" ", 2))
      (date, timestamp, hostmask, contents) = (components[0], components[1], 
                                               components[2], components[3])
      line_type = cls.toykeeper_json(hostmask, contents)
      (offset_timestamp, offset_datestamp) = cls.calculate_offset(date, timestamp, offset)
      converted_line = cls.construct(line_id, line_type, offset_timestamp, hostmask, contents)
      return {"converted_line":converted_line, "offset_datestamp":offset_datestamp, 
              "date":date, "timestamp":timestamp, "hostmask":hostmask, "contents":contents}
    iter_id = queue.add_iter(iter(("\n\n  " + str(process_line(line_id, line, utc_offset)["offset_datestamp"]) + ":\n    [", "\n    ],")))
    queue.add(iter_id)
    queue.add(iter_id)
    cls.output(queue.tick())
    line_id += 1
    for line in loglines[1:]:
      line_elements = process_line(line_id, line, utc_offset)
      if line_elements["date"] > current_date:
        current_date = line_elements["date"]
        cls.output(queue.tick())
        iter_id = queue.add_iter(iter(("\n    ],", 
                                       "\n\n  " + str(line_elements["offset_datestamp"]) + ":\n    [")))
        queue.add(iter_id)
        queue.add(iter_id)
        cls.output(queue.tick())
      cls.output(json.dumps((" " * 6) + str(line_elements["converted_line"]) + ",\n"))
      line_id += 1  
    cls.output(queue.tick())
    return None
  
  def toykeeper_json(hostmask, contents):
    """Classify lines according to their contents and return a dictionary of the 
    form {line_id:line_type...}
    
    Keyword arguments:
      hostmask | The hostmask given as the source for the line. 
      contents | The actual message of the line.
    """
    line_types = {}
    if hostmask[0] + hostmask[-1] == "<>":
      line_type = "PRIVMSG"
    elif hostmask[0] + hostmask[-1] == "[]" and contents[0:6] == "ACTION":
      line_type = "ACTION"
    elif hostmask[0] + hostmask[-1] == "--":
      content_split = contents.split(" ")
      if hostmask == "-dircproxy-":
        if contents == "You connected\n":
          line_type = "CONNECTED"
        elif contents == "You disconnected\n":
          line_type = "DISCONNECTED"
      elif contents == "You joined the channel\n":
        line_type = "JOINED"
      """Notices use '--' to denote themselves and have no distinguishing marks besides, 
      we start by filtering out those with lengths too short for the 
      other tests.
      """
      elif len(content_split) < 3: 
        line_type = "NOTICE"
      elif content_split[2] == "joined":
        line_type = "JOIN"
      elif content_split[2] == "left":
        line_type = "PART"
      elif content_split[1] + content_split[2] == "kickedoff":
        line_type = "KICK"
      elif content_split[0][0] + content_split[0][-1] == "[]":
        line_type = "NOTICE"
      try:
        if content_split[1] + content_split[2]  == "changedmode:" or content_split[2] + content_split[3] == "changedmode:":
          line_type = "SETMODE"
        elif content_split[1] + content_split[2] == "changedtopic:" or content_split[2] + content_split[3] == "changedtopic:":
          line_type = "TOPIC"
      except IndexError:
        line_type = "NOTICE"
      if contents[0:4] == "CTCP":
        line_type = "CTCP"
      else:
        line_type = "NOTICE"
    return line_type

  def construct(line_id, line_type, time_, hostmask, contents):
    """Construct a line suitable for output in line with the generic python format energymech log converter uses."""
    def type_is(linetype): return (line_type == linetype)
    universal = (line_id, line_type, time_)
    contents = contents[:-1] # Strip trailing newlines
    hostmask = hostmask[1:-1] # Strip buffer characters '<>', '[]', '--'
    if type_is("PRIVMSG") or type_is("ACTION") or type_is("NOTICE") or type_is("CTCP"):
      return universal + (hostmask, contents)

    content_split = contents.split(" ")
    if type_is("JOIN") or type_is("PART"):
      userhost = cls.hostmask_stripper(content_split[1])
      (nick, user, hostname) = (content_split[0], userhost[0], userhost[1])
      hostmask = cls.construct_hostmask(nick, user, hostname)
      return universal + (hostmask,)
    elif type_is("KICK"):
      kick_split = contents.split(" ", 6)
      userhost = cls.hostmask_stripper(kick_split[5])
      (nick, user, hostname) = (kick_split[4], userhost[0], userhost[1])
      hostmask = cls.construct_hostmask(nick, user, hostname)
      (nick_kicked, kick_message) = (kick_split[0], kick_split[6])
      return universal + (nick_kicked, hostmask, kick_message)
    elif type_is("SETMODE"):
      setmode_split = contents.split(" ", 3) # The size of setmode varies so we assume it's the shorter version to avoid a ValueError
      if setmode_split[2] == "mode:":
        (set_by, mode_string) = (setmode_split[0], setmode_split[3])
        return universal + (set_by, mode_string)
      elif setmode_split[3] == "mode:":
        setmode_split = contents.split(" ", 4)
        userhost = cls.hostmask_stripper(setmode_split[1])
        nick = setmode_split[0]
        user = hostmask_split[0]
        hostname = hostmask_split[1]
        set_by = cls.construct_hostmask(nick, user, hostname)
        return universal + (set_by, setmode_split[4])
    elif type_is("TOPIC"):
      topic_split = contents.split(" ", 3) # The size of topicsplit varies so we assume it's the shorter version to avoid a ValueError
      if topic_split[2] == "topic:":
        (changed_by, topic) = (topic_split[0], topic_split[3])
        return universal + (changed_by, topic)
      elif topic_split[3] == "topic:":
        topic_split = contents.split(" ", 4)
        userhost = cls.hostmask_stripper(topic_split[1])
        (nick, user, hostname, topic) = (topic_split[0], userhost[0], 
                                         userhost[1], topic_split[4])
        changed_by = cls.construct_hostmask(nick, user, hostname)
        return universal + (changed_by, topic)
    elif type_is("JOINED") or type_is("CONNECTED") or type_is("DISCONNECTED"):
      return universal
    else:
      raise ValueError("Given type was not in the types of message handled by the toykeeper converter.")

  def hostmask_stripper(cls, userhost):
    """Strip characters from a set of hostmask components to prepare them for processing by construct_hostmask. (USER@HOSTNAME) OR (~USER@HOSTNAME)"""
    userhost_components = userhost[1:-1].split("@")
    if userhost_components[0][0] == "~":
      return (userhost_components[0][1:], userhost_components[1])
    else:
      return (userhost_components[0], userhost_components[1])

  def construct_hostmask(nick, user, hostname):
    """Takes a nick,user,hostname combo and constructs a string representing it like such: user!~username@127.0.0.1"""
    return nick + "!~" + user + "@" + "hostname"  

  def calculate_offset(date, time_, offset):
    """Take date, time and offset and calculate the final time from UTC.
    Keyword arguments:
      date: A string representing the date in %Y-%m-%d format.
      time: A string representing the time that can be accepted by time2seconds
      offset: A timedelta representing the UTC offset.
    """
    timestamp = int(time.mktime(time.strptime(date, "%Y-%m-%d"))) + time2seconds(time_)
    if offset == None:
      return (time2seconds(time_), int(time.mktime(time.strptime(date, "%Y-%m-%d"))))
    else:
      try:  
        offset_timestamp = timestamp - ((int(offset)) * (60 ** 2))
      except ValueError:
        raise ValueError("Offset" + str(offset) + " was not a properly formatted UTC offset.")
    offset_gmtime = time.gmtime(offset_timestamp)
    time_ = time2seconds(time.strftime("%H:%M:%S", offset_gmtime))
    date = offset_gmtime[:3] + (0,0,0) + offset_gmtime[6:9]
    datestamp = timegm(date)
    return (time_, datestamp)

  def output(cls, string):
    """Handles output for files and to standard output. (Currently a wrapper around 
    print() for when I make something that's less of a hack.)
    """
    print(string, end="")

class output_queue():
  """Implements an output queue of iterators."""
  def __init__(self):
    self._queue = []
    self._iterators = {}

  def tick(self):
    """Outputs an item from the next iterator in the queue."""
    next_output = self._queue.pop()
    next_item = next(self._iterators[next_output])
    print(next_item)

  def add(self, iter_id):
    """Set an iterator to be executed at the next tick.
    Keyword arguments:
      iter_id | A unique ID assigned to every iterator added to iterators.
    """
    self._queue.append(iter_id)

  def add_iter(self, iterator):
    """Add an iterator to the set of iterators that are in this queue."""
    iter_id = len(self._iterators)
    self._iterators[iter_id] = iterator
    return iter_id

  def upcoming(self, position):
    """Return the iter_id in queue at position."""
    return self._queue[position]

  def pop_iter(self, iter_id):
    """Return the iterator from iterators with the given iter_id."""
    return self._iterators.pop(iter_id)
