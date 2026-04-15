import PostIncidentProofs.Rate.Model
import PostIncidentProofs.Rate.Verification

def main (_args : List String) : IO UInt32 := do
  let cfg : PostIncidentProofs.Rate.RateLimitConfig := {
    max_requests := 10
    window_seconds := 60
    tenant_id := "default"
  }
  let ok := PostIncidentProofs.Rate.Verification.verify_algorithm_correctness cfg
  IO.println s!"rate_verifier: {if ok then "PASS" else "FAIL"}"
  pure (if ok then 0 else 1)
