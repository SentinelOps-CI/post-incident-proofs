namespace PostIncidentProofs.Rate

structure RateLimitConfig where
  max_requests : UInt64
  window_seconds : UInt64
  tenant_id : String
  deriving Repr

structure RequestRecord where
  timestamp : UInt64
  count : UInt64
  deriving Repr

structure RateLimitState where
  config : RateLimitConfig
  window : List RequestRecord
  current_count : UInt64
  last_cleanup : UInt64
  deriving Repr

inductive RateLimitDecision where
  | Allow | Deny
  deriving Repr, BEq, DecidableEq

def RateLimitState.new (config : RateLimitConfig) : RateLimitState :=
  { config := config, window := [], current_count := 0, last_cleanup := 0 }

def RateLimitState.cleanup_window (state : RateLimitState) (current_time : UInt64) : RateLimitState :=
  let cutoff := if current_time > state.config.window_seconds then current_time - state.config.window_seconds else 0
  let valid := state.window.filter (fun r => r.timestamp > cutoff)
  let count := valid.foldl (fun acc r => acc + r.count) 0
  { state with window := valid, current_count := count, last_cleanup := current_time }

def RateLimitState.check_request (state : RateLimitState) (timestamp : UInt64) : RateLimitDecision :=
  let state' := state.cleanup_window timestamp
  if state'.current_count < state'.config.max_requests then RateLimitDecision.Allow else RateLimitDecision.Deny

def RateLimitState.add_request (state : RateLimitState) (timestamp : UInt64) (count : UInt64) : RateLimitState :=
  let state' := state.cleanup_window timestamp
  { state' with window := { timestamp := timestamp, count := count } :: state'.window, current_count := state'.current_count + count }

def RateLimitState.check_request_fast (state : RateLimitState) (timestamp : UInt64) : RateLimitDecision :=
  state.check_request timestamp

def RateLimitState.add_requests_batch (state : RateLimitState) (requests : List (UInt64 × UInt64)) : RateLimitState :=
  requests.foldl (fun s (t, c) => s.add_request t c) state

def RateLimitState.get_stats (state : RateLimitState) (current_time : UInt64) : (UInt64 × UInt64 × Float) :=
  let s := state.cleanup_window current_time
  let rps := if s.config.window_seconds == 0 then 0.0 else s.current_count.toFloat / s.config.window_seconds.toFloat
  (s.current_count, s.config.max_requests, rps)

structure MultiTenantRateLimit where
  tenants : List (String × RateLimitState)
  deriving Repr

def MultiTenantRateLimit.check_tenant_request (state : MultiTenantRateLimit) (tenant_id : String) (timestamp : UInt64) : RateLimitDecision :=
  match state.tenants.find? (fun (id, _) => id == tenant_id) with
  | some (_, tenantState) => tenantState.check_request timestamp
  | none => RateLimitDecision.Allow

def MultiTenantRateLimit.add_tenant_request
  (state : MultiTenantRateLimit) (tenant_id : String) (timestamp : UInt64) (count : UInt64) : MultiTenantRateLimit :=
  { tenants := state.tenants.map (fun (id, tenantState) =>
      if id == tenant_id then (id, tenantState.add_request timestamp count) else (id, tenantState)) }

def simulate_burst_traffic (config : RateLimitConfig) (burst_size : UInt64) (_duration_seconds : UInt64) : List RateLimitDecision :=
  let state := RateLimitState.new config
  (List.range burst_size.toNat).map (fun i => state.check_request i.toUInt64)

def validate_chaos_test (decisions : List RateLimitDecision) (expected_allows : UInt64) : Bool :=
  let actual : UInt64 := (decisions.filter (fun d => d == RateLimitDecision.Allow)).length.toUInt64
  actual <= expected_allows + 1

theorem rate_limit_enforcement_placeholder (_state : RateLimitState) (_timestamp : UInt64) : True := by
  trivial

end PostIncidentProofs.Rate
