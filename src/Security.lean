import PostIncidentProofs

def main (_args : List String) : IO UInt32 := do
  let ok ← PostIncidentProofs.validate_security_properties
  IO.println s!"security: {if ok then "PASS" else "FAIL"}"
  pure (if ok then 0 else 1)
