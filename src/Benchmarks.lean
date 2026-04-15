import PostIncidentProofs.Benchmark.Performance

def main (_args : List String) : IO UInt32 := do
  let results ← PostIncidentProofs.Benchmark.runAllBenchmarks
  let allOk := results.all (fun r => r.success)
  IO.println s!"benchmarks: ran {results.length} checks"
  pure (if allOk then 0 else 1)
