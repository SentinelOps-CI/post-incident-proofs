namespace PostIncidentProofs.Utils.Time

abbrev Time := UInt64

structure Duration where
  nanos : UInt64
  deriving Repr, BEq, DecidableEq

namespace Duration

def milliseconds (ms : UInt64) : Duration := { nanos := ms * 1000000 }
def seconds (s : UInt64) : Duration := { nanos := s * 1000000000 }
def minutes (m : UInt64) : Duration := seconds (m * 60)
def toSeconds (d : Duration) : Float := d.nanos.toFloat / 1000000000.0

end Duration

instance : Sub Time where
  sub a b := if a >= b then a - b else b - a

def monotonic_nanos : UInt64 := 1000000
def unix_timestamp : UInt64 := 1700000000
def getMonotonicTime : Time := monotonic_nanos

structure Window where
  start : UInt64
  stop : UInt64
  deriving Repr

def Window.endTs (window : Window) : UInt64 := window.stop

def Window.from_duration (start : UInt64) (duration_seconds : UInt64) : Window :=
  { start := start, stop := start + duration_seconds }

def Window.sliding (duration_seconds : UInt64) : Window :=
  Window.from_duration (unix_timestamp - duration_seconds) duration_seconds

def Window.contains (window : Window) (timestamp : UInt64) : Bool :=
  timestamp >= window.start && timestamp <= window.stop

def format_timestamp (timestamp : UInt64) : String := toString timestamp
def nanos_to_seconds (nanos : UInt64) : Float := nanos.toFloat / 1000000000.0

end PostIncidentProofs.Utils.Time
