import PostIncidentProofs

def main (_args : List String) : IO UInt32 := do
  let metrics ← PostIncidentProofs.collect_system_metrics
  let health ← PostIncidentProofs.run_health_checks
  IO.println s!"observability: metrics={metrics.length} health_checks={health.length}"
  pure 0
