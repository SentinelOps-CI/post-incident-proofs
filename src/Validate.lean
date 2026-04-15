import PostIncidentProofs

def main (_args : List String) : IO UInt32 := do
  let sec ← PostIncidentProofs.validate_security_properties
  let perf ← PostIncidentProofs.validate_performance_slas
  let chaos ← PostIncidentProofs.validate_system_resilience
  let ok := sec && perf && chaos
  IO.println s!"validate: {if ok then "PASS" else "FAIL"}"
  pure (if ok then 0 else 1)
