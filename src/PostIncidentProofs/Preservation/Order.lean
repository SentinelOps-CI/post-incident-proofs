/-
  Retained event order: retained must be an order-preserving subsequence.
-/
namespace PostIncidentProofs.Preservation.Order

/-- Executable subsequence checker (mirrors Rust/Python). -/
def isRetainedSubsequence : List String → List String → Bool
  | _, [] => true
  | [], _ :: _ => false
  | x :: xs, y :: ys =>
      if x = y then isRetainedSubsequence xs ys
      else isRetainedSubsequence xs (y :: ys)

/-- Empty retained list is always a subsequence. -/
theorem retained_nil (full : List String) :
    isRetainedSubsequence full [] = true := by
  cases full <;> rfl

/-- Soundness for the Bool decider on equal lists. -/
theorem subsequence_self : ∀ xs : List String, isRetainedSubsequence xs xs = true
  | [] => rfl
  | x :: xs => by
      simp [isRetainedSubsequence]
      exact subsequence_self xs

/-- Inductive characterization. -/
inductive IsSubsequence : List String → List String → Prop
  | nil (xs : List String) : IsSubsequence xs []
  | skip (x : String) (xs ys : List String) (h : IsSubsequence xs ys) :
      IsSubsequence (x :: xs) ys
  | take (x : String) (xs ys : List String) (h : IsSubsequence xs ys) :
      IsSubsequence (x :: xs) (x :: ys)

/-- Bool true implies inductive subsequence (soundness of the executable decider). -/
theorem of_bool_true :
    ∀ (full retained : List String),
      isRetainedSubsequence full retained = true → IsSubsequence full retained
  | full, [], _ => IsSubsequence.nil full
  | [], y :: ys, h => by
      simp [isRetainedSubsequence] at h
  | x :: xs, y :: ys, h => by
      simp [isRetainedSubsequence] at h
      split at h
      · next heq =>
          have ih := of_bool_true xs ys h
          simpa [heq] using IsSubsequence.take x xs ys ih
      · next _ =>
          exact IsSubsequence.skip x xs (y :: ys) (of_bool_true xs (y :: ys) h)

/-- If decider returns true then the inductive property holds. -/
theorem soundness
    (full retained : List String)
    (h : isRetainedSubsequence full retained = true) :
    IsSubsequence full retained :=
  of_bool_true full retained h

/-- Concrete String vectors used as conformance anchors. -/
def fullExample : List String := ["e1", "e2", "e3", "e4"]
def retainedOk : List String := ["e1", "e3"]
def retainedBad : List String := ["e3", "e1"]

theorem example_order_ok :
    isRetainedSubsequence fullExample retainedOk = true := by
  native_decide

theorem example_order_bad :
    isRetainedSubsequence fullExample retainedBad = false := by
  native_decide

theorem example_order_sound :
    IsSubsequence fullExample retainedOk :=
  soundness fullExample retainedOk example_order_ok

end PostIncidentProofs.Preservation.Order
