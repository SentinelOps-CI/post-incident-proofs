import PostIncidentProofs.Logging.Core
import PostIncidentProofs.Logging.Verification
import PostIncidentProofs.Utils.Crypto

def main (_args : List String) : IO UInt32 := do
  let key := PostIncidentProofs.Utils.Crypto.generate_hmac_key
  let entry := PostIncidentProofs.Logging.LogEntry.mk' 1 PostIncidentProofs.Logging.LogLevel.INFO "boot" 1
  let signed := { entry with hmac := entry.compute_hmac key }
  let result := PostIncidentProofs.Logging.Verification.verify_chain [signed] key
  match result with
  | PostIncidentProofs.Logging.Verification.VerificationResult.Valid =>
    IO.println "log_verifier: PASS"
    pure 0
  | _ =>
    IO.println "log_verifier: FAIL"
    pure 1
