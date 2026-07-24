/-
  Executable Lean mirrors of runtime preservation deciders + soundness wrappers.
-/
import PostIncidentProofs.Lineage.Graph
import PostIncidentProofs.Preservation.Order
import PostIncidentProofs.Preservation.Projection

namespace PostIncidentProofs.Preservation.Deciders

open PostIncidentProofs.Lineage.Graph
open PostIncidentProofs.Preservation.Order
open PostIncidentProofs.Preservation.Projection

/-- Decider: retained event order. -/
def decideOrder (full retained : List String) : Bool :=
  isRetainedSubsequence full retained

theorem decideOrder_sound
    (full retained : List String)
    (h : decideOrder full retained = true) :
    IsSubsequence full retained :=
  soundness full retained h

/-- Decider: projection equality. -/
def decideProjection (a b : List (String × String)) : Bool :=
  projectionEq a b

theorem decideProjection_sound
    (a b : List (String × String))
    (h : decideProjection a b = true) :
    ProjectionEquiv a b :=
  projectionEq_true_implies_equiv a b h

/-- Decider: transformation graph acyclicity + ref resolution. -/
def decideAcyclic (g : Graph) : Bool :=
  structurallyValid g

theorem decideAcyclic_sound_refs
    (g : Graph)
    (h : decideAcyclic g = true) :
    refsResolve g = true :=
  structurallyValid_implies_refs g h

theorem decideAcyclic_sound_acyclic
    (g : Graph)
    (h : decideAcyclic g = true) :
    isAcyclic g = true :=
  structurallyValid_implies_acyclic g h

/-- Undeclared source check: observed ⊆ declared. -/
def decideNoUndeclared (declared observed : List String) : Bool :=
  observed.all (fun d => declared.contains d)

theorem decideNoUndeclared_nil_observed (declared : List String) :
    decideNoUndeclared declared [] = true := by
  simp [decideNoUndeclared]

/-- Soundness: a true decider result means the Bool subset check holds. -/
theorem decideNoUndeclared_sound
    (declared observed : List String)
    (h : decideNoUndeclared declared observed = true) :
    observed.all (fun d => declared.contains d) = true := by
  simpa [decideNoUndeclared] using h

theorem decideNoUndeclared_example :
    decideNoUndeclared ["a", "b"] ["a"] = true := by
  native_decide


/-- Conformance evaluation gate (#eval targets). -/
def conformanceOrderOk : Bool :=
  decideOrder ["e1", "e2", "e3", "e4"] ["e1", "e3"]

def conformanceOrderBad : Bool :=
  decideOrder ["e1", "e2", "e3", "e4"] ["e3", "e1"]

def conformanceProjOk : Bool :=
  decideProjection [("k", "v")] [("k", "v")]

def conformanceAcyclicOk : Bool :=
  decideAcyclic exampleDag

def conformanceAcyclicBad : Bool :=
  decideAcyclic exampleCycle

theorem conformance_order_ok_holds : conformanceOrderOk = true := by
  native_decide

theorem conformance_order_bad_holds : conformanceOrderBad = false := by
  native_decide

theorem conformance_proj_ok_holds : conformanceProjOk = true := by
  native_decide

theorem conformance_acyclic_ok_holds : conformanceAcyclicOk = true := by
  native_decide

theorem conformance_acyclic_bad_holds : conformanceAcyclicBad = false := by
  native_decide

end PostIncidentProofs.Preservation.Deciders
