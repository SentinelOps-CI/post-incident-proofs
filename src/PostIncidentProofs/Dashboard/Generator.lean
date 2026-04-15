namespace PostIncidentProofs.Dashboard

inductive SpecType where
  | LogTamper | RateLimit | VersionRollback | BundleIntegrity
  deriving Repr

structure Spec where
  name : String
  spec_type : SpecType
  theorem_ref : String
  threshold : Float
  window_seconds : UInt64
  deriving Repr

structure GridPosition where
  x : UInt64
  y : UInt64
  w : UInt64
  h : UInt64
  deriving Repr

structure Alert where
  name : String
  expr : String
  duration_for : String
  labels : List (String × String)
  annotations : List (String × String)
  deriving Repr

structure Panel where
  title : String
  panel_type : String
  query : String
  grid_pos : GridPosition
  alert : Option Alert
  deriving Repr

structure Dashboard where
  title : String
  version : UInt64
  panels : List Panel
  alerts : List Alert
  deriving Repr

def spec_to_panel (spec : Spec) : Panel :=
  { title := spec.name, panel_type := "stat", query := s!"{spec.name}_metric", grid_pos := { x := 0, y := 0, w := 12, h := 8 }, alert := none }

def generate_dashboard (specs : List Spec) : Dashboard :=
  { title := "Post-Incident-Proofs Dashboard", version := 1, panels := specs.map spec_to_panel, alerts := [] }

def generate_alert_rule (spec : Spec) : String :=
  s!"alert: {spec.name}\nexpr: {spec.name}_metric > {spec.threshold}\nfor: {spec.window_seconds}s"

def generate_alert_rules (specs : List Spec) : List String :=
  specs.map generate_alert_rule

def generate_dashboard_json (specs : List Spec) : String :=
  "dashboard=Post-Incident-Proofs Dashboard,panels=" ++ toString specs.length

def log_tamper_spec : Spec := { name := "log_tamper_detection", spec_type := SpecType.LogTamper, theorem_ref := "Logging", threshold := 0.0, window_seconds := 300 }
def rate_limit_spec : Spec := { name := "rate_limit_violation", spec_type := SpecType.RateLimit, theorem_ref := "Rate", threshold := 0.001, window_seconds := 60 }
def version_rollback_spec : Spec := { name := "version_rollback", spec_type := SpecType.VersionRollback, theorem_ref := "Version", threshold := 1.0, window_seconds := 3600 }
def bundle_integrity_spec : Spec := { name := "bundle_integrity", spec_type := SpecType.BundleIntegrity, theorem_ref := "Bundle", threshold := 0.0, window_seconds := 86400 }

end PostIncidentProofs.Dashboard
