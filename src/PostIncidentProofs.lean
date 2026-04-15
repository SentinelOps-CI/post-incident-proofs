import PostIncidentProofs.Logging.Core
import PostIncidentProofs.Logging.Verification
import PostIncidentProofs.Rate.Model
import PostIncidentProofs.Rate.Verification
import PostIncidentProofs.Version.Diff
import PostIncidentProofs.Version.Verification
import PostIncidentProofs.Dashboard.Generator
import PostIncidentProofs.Bundle.Builder
import PostIncidentProofs.Security.ThreatModel
import PostIncidentProofs.Benchmark.Performance
import PostIncidentProofs.Chaos.Engine
import PostIncidentProofs.Observability.Metrics

namespace PostIncidentProofs

def verify_log_chain (chain : List Logging.LogEntry) (key : ByteArray) : Bool :=
  Logging.verify_chain_integrity chain key

def verify_rate_limit (state : Rate.RateLimitState) : Bool :=
  match Rate.Verification.verify_state state 0 with
  | Rate.Verification.VerificationResult.Valid => true
  | _ => false

def apply_diff (state : Version.State) (diff : Version.Diff) : Version.State :=
  Version.apply_diff state diff

def revert_diff (state : Version.State) (diff : Version.Diff) : Version.State :=
  Version.revert_diff state diff

def generate_dashboard (specs : List Dashboard.Spec) : String :=
  Dashboard.generate_dashboard_json specs

def create_incident_bundle
  (logs : List Logging.LogEntry)
  (specs : List String)
  (window : Utils.Time.Window) : Bundle.Builder.IncidentBundle :=
  Bundle.Builder.create_bundle logs specs window

def verify_incident_bundle (bundle : Bundle.Builder.IncidentBundle) : Bool :=
  Bundle.Builder.verify_bundle bundle

def run_security_tests : IO Security.ThreatModel.SecurityMetrics :=
  Security.ThreatModel.runSecurityTests

def validate_security_properties : IO Bool := do
  let m ← run_security_tests
  pure (m.rate_limit_false_negatives == 0.0)

def run_performance_benchmarks : IO (List Benchmark.BenchmarkResult) :=
  Benchmark.runAllBenchmarks

def validate_performance_slas : IO Bool := do
  let results ← run_performance_benchmarks
  pure (results.all (fun r => r.success))

def run_chaos_tests (config : Chaos.Engine.ChaosConfig) : IO (List Chaos.Engine.ChaosTestResult) :=
  Chaos.Engine.runChaosTestSuite config

def validate_system_resilience : IO Bool := do
  let results ← run_chaos_tests {}
  pure (results.all (fun r => r.success))

def collect_system_metrics : IO (List Observability.Metrics.Metric) :=
  Observability.Metrics.collectSystemMetrics

def run_health_checks : IO (List Observability.Metrics.HealthCheck) :=
  Observability.Metrics.runHealthChecks

def create_trace_span (operation_name : String) (parent_span_id : Option String := none) : IO Observability.Metrics.TraceSpan :=
  Observability.Metrics.createTraceSpan operation_name parent_span_id

def finish_trace_span (span : Observability.Metrics.TraceSpan) : Observability.Metrics.TraceSpan :=
  Observability.Metrics.finishTraceSpan span

def add_trace_tag (span : Observability.Metrics.TraceSpan) (key : String) (value : String) : Observability.Metrics.TraceSpan :=
  Observability.Metrics.addTraceTag span key value

def add_trace_log (span : Observability.Metrics.TraceSpan) (message : String) : Observability.Metrics.TraceSpan :=
  Observability.Metrics.addTraceLog span message

end PostIncidentProofs
