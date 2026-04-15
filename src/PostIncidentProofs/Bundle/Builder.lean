import PostIncidentProofs.Logging.Core
import PostIncidentProofs.Utils.Crypto
import PostIncidentProofs.Utils.Time

namespace PostIncidentProofs.Bundle.Builder

structure BundleContents where
  logs : List PostIncidentProofs.Logging.LogEntry
  specs : List String
  proof_hashes : List (String × ByteArray)
  html_timeline : String
  metadata : List (String × String)

structure IncidentBundle where
  id : String
  created_at : UInt64
  time_window : PostIncidentProofs.Utils.Time.Window
  size_bytes : UInt64
  hash : ByteArray
  contents : BundleContents

inductive ValidationResult where
  | Valid
  | InvalidSize : UInt64 → UInt64 → ValidationResult
  | InvalidHash : String → ValidationResult
  | InvalidWindow : String → ValidationResult
  | InvalidSchema : String → ValidationResult
  deriving Repr

private def escapeJson (s : String) : String :=
  s.replace "\\" "\\\\" |>.replace "\"" "\\\"" |>.replace "\n" "\\n"

def create_bundle
  (logs : List PostIncidentProofs.Logging.LogEntry)
  (specs : List String)
  (window : PostIncidentProofs.Utils.Time.Window) : IncidentBundle :=
  let payload := String.intercalate "|" (specs.map escapeJson)
  let hash := PostIncidentProofs.Utils.Crypto.sha256 payload.toUTF8
  {
    id := s!"bundle-{PostIncidentProofs.Utils.Time.unix_timestamp}"
    created_at := PostIncidentProofs.Utils.Time.unix_timestamp
    time_window := window
    size_bytes := (logs.length * 256 + specs.length * 128).toUInt64
    hash := hash
    contents := { logs := logs, specs := specs, proof_hashes := [], html_timeline := "", metadata := [("schema_version", "1.0")] }
  }

def validate_bundle (bundle : IncidentBundle) : ValidationResult :=
  if bundle.size_bytes <= 5 * 1024 * 1024 then ValidationResult.Valid else ValidationResult.InvalidSize bundle.size_bytes (5 * 1024 * 1024)

def verify_bundle (bundle : IncidentBundle) : Bool :=
  match validate_bundle bundle with
  | ValidationResult.Valid => true
  | _ => false

def check_sentinelops_compliance (bundle : IncidentBundle) : Bool :=
  bundle.contents.metadata.any (fun (k, v) => k == "schema_version" && v == "1.0")

def generate_audit_report (bundle : IncidentBundle) : String :=
  s!"Bundle ID: {bundle.id}\nSize: {bundle.size_bytes}\nValid: {verify_bundle bundle}"

end PostIncidentProofs.Bundle.Builder
