import PostIncidentProofs.Utils.Crypto

namespace PostIncidentProofs.Logging

inductive LogLevel where
  | TRACE | DEBUG | INFO | WARN | ERROR | FATAL
  deriving Repr, BEq, DecidableEq

instance : ToString LogLevel where
  toString
    | LogLevel.TRACE => "TRACE"
    | LogLevel.DEBUG => "DEBUG"
    | LogLevel.INFO => "INFO"
    | LogLevel.WARN => "WARN"
    | LogLevel.ERROR => "ERROR"
    | LogLevel.FATAL => "FATAL"

structure LogEntry where
  timestamp : UInt64
  level : LogLevel
  message : String
  counter : UInt64
  hmac : ByteArray

def LogEntry.mk' (timestamp : UInt64) (level : LogLevel) (message : String) (counter : UInt64) : LogEntry :=
  { timestamp := timestamp, level := level, message := message, counter := counter, hmac := ByteArray.empty }

def LogEntry.compute_hmac (entry : LogEntry) (key : ByteArray) : ByteArray :=
  let payload := s!"{entry.timestamp}:{entry.level}:{entry.message}:{entry.counter}"
  PostIncidentProofs.Utils.Crypto.hmac_sha256 key payload.toUTF8

def LogEntry.verify_hmac (entry : LogEntry) (key : ByteArray) : Bool :=
  PostIncidentProofs.Utils.Crypto.bytesEq entry.hmac (entry.compute_hmac key)

abbrev LogChain := List LogEntry

def verify_chain_hmacs (chain : LogChain) (key : ByteArray) : Bool :=
  chain.all (fun entry => entry.verify_hmac key)

def verify_chain_counters (chain : LogChain) : Bool :=
  match chain with
  | [] => true
  | first :: rest =>
    let rec go (prev : UInt64) (remaining : List LogEntry) : Bool :=
      match remaining with
      | [] => true
      | entry :: tail => if prev < entry.counter then go entry.counter tail else false
    go first.counter rest

def verify_chain_integrity (chain : LogChain) (key : ByteArray) : Bool :=
  verify_chain_hmacs chain key && verify_chain_counters chain

def verify_hmac_fast (entry : LogEntry) (key_hash : ByteArray) : Bool :=
  entry.verify_hmac key_hash

def verify_hmac_batch (entries : List LogEntry) (key : ByteArray) : Bool :=
  entries.all (fun e => e.verify_hmac key)

def LogEntry.toJson (entry : LogEntry) : String :=
  "timestamp=" ++ toString entry.timestamp ++ ",level=" ++ toString entry.level ++ ",message=" ++ entry.message ++ ",counter=" ++ toString entry.counter

def LogEntry.fromJson (_json : String) : Option LogEntry := none

def LogChain.toJsonl (chain : LogChain) : String :=
  String.intercalate "\n" (chain.map LogEntry.toJson)

def LogChain.fromJsonl (_jsonl : String) : Option LogChain := none

theorem counter_monotone_placeholder (_chain : LogChain) (_key : ByteArray) : True := by
  trivial

end PostIncidentProofs.Logging
