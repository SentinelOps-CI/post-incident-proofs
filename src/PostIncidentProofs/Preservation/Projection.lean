/-
  Selected state projection equality.
-/
namespace PostIncidentProofs.Preservation.Projection

/-- Executable equality on association lists (normalized upstream). -/
def projectionEq (a b : List (String × String)) : Bool :=
  decide (a = b)

/-- Inductive equality mirror. -/
def ProjectionEquiv (a b : List (String × String)) : Prop :=
  a = b

theorem projectionEq_true_implies_equiv
    (a b : List (String × String))
    (h : projectionEq a b = true) :
    ProjectionEquiv a b := by
  simp [projectionEq, ProjectionEquiv, decide_eq_true_iff] at h
  exact h

theorem projectionEq_refl (a : List (String × String)) :
    projectionEq a a = true := by
  simp [projectionEq]

/-- Conformance anchors. -/
def projA : List (String × String) := [("status", "failed"), ("code", "E1")]
def projB : List (String × String) := [("status", "failed"), ("code", "E1")]
def projC : List (String × String) := [("status", "ok"), ("code", "E1")]

theorem example_proj_ok : projectionEq projA projB = true := by
  native_decide

theorem example_proj_bad : projectionEq projA projC = false := by
  native_decide

theorem example_proj_sound : ProjectionEquiv projA projB :=
  projectionEq_true_implies_equiv projA projB example_proj_ok

end PostIncidentProofs.Preservation.Projection
