import PostIncidentProofs.Utils.Time

namespace PostIncidentProofs.Observability.Metrics

inductive MetricType where
  | Counter | Gauge | Histogram | Summary
  deriving Repr, BEq, DecidableEq

structure Metric where
  name : String
  value : Float
  labels : List (String × String)
  timestamp : UInt64
  metric_type : MetricType
  deriving Repr

inductive HealthStatus where
  | Healthy | Degraded | Unhealthy | Unknown
  deriving Repr, BEq, DecidableEq

structure HealthCheck where
  name : String
  status : HealthStatus
  message : String
  last_check : UInt64
  response_time : PostIncidentProofs.Utils.Time.Duration
  details : List (String × String)
  deriving Repr

structure TraceSpan where
  trace_id : String
  span_id : String
  parent_span_id : Option String
  operation_name : String
  start_time : UInt64
  end_time : Option UInt64
  tags : List (String × String)
  logs : List (UInt64 × String)
  deriving Repr

def collectSystemMetrics : IO (List Metric) := do
  pure [
    { name := "post_incident_proofs_errors_total", value := 0, labels := [], timestamp := PostIncidentProofs.Utils.Time.getMonotonicTime, metric_type := MetricType.Counter },
    { name := "post_incident_proofs_cpu_usage_percent", value := 15.0, labels := [], timestamp := PostIncidentProofs.Utils.Time.getMonotonicTime, metric_type := MetricType.Gauge }
  ]

def runHealthChecks : IO (List HealthCheck) := do
  pure [
    { name := "core_runtime", status := HealthStatus.Healthy, message := "ok", last_check := PostIncidentProofs.Utils.Time.getMonotonicTime, response_time := PostIncidentProofs.Utils.Time.Duration.milliseconds 10, details := [] }
  ]

def createTraceSpan (operation_name : String) (parent_span_id : Option String := none) : IO TraceSpan := do
  pure { trace_id := "trace-1", span_id := "span-1", parent_span_id := parent_span_id, operation_name := operation_name, start_time := PostIncidentProofs.Utils.Time.getMonotonicTime, end_time := none, tags := [], logs := [] }

def finishTraceSpan (span : TraceSpan) : TraceSpan := { span with end_time := some PostIncidentProofs.Utils.Time.getMonotonicTime }
def addTraceTag (span : TraceSpan) (key : String) (value : String) : TraceSpan := { span with tags := (key, value) :: span.tags }
def addTraceLog (span : TraceSpan) (message : String) : TraceSpan := { span with logs := (PostIncidentProofs.Utils.Time.getMonotonicTime, message) :: span.logs }

def exportPrometheusMetrics (metrics : List Metric) : String :=
  String.intercalate "\n" (metrics.map (fun m => s!"{m.name} {m.value}"))

def generateHealthResponse (_checks : List HealthCheck) : String :=
  "{\"status\":\"healthy\"}"

def generateAlertingRules : String :=
  "groups:\n- name: post_incident_proofs\n  rules: []"

end PostIncidentProofs.Observability.Metrics
