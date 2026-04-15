import PostIncidentProofs
import PostIncidentProofs.Utils.Crypto

def main (_args : List String) : IO UInt32 := do
  let key := PostIncidentProofs.Utils.Crypto.generate_hmac_key
  let entry := PostIncidentProofs.Logging.LogEntry.mk' 1 PostIncidentProofs.Logging.LogLevel.INFO "test" 1
  let signed := { entry with hmac := entry.compute_hmac key }
  let logOk := PostIncidentProofs.verify_log_chain [signed] key
  let rateCfg : PostIncidentProofs.Rate.RateLimitConfig := { max_requests := 10, window_seconds := 60, tenant_id := "t" }
  let rateState := PostIncidentProofs.Rate.RateLimitState.new rateCfg
  let rateOk := PostIncidentProofs.verify_rate_limit rateState
  let allOk := logOk && rateOk
  IO.println s!"tests: {if allOk then "PASS" else "FAIL"}"
  pure (if allOk then 0 else 1)
