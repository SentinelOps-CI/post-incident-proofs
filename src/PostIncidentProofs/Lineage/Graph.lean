/-
  Finite DAG model for incident lineage graphs.
  Trusted parsers live outside Lean; this module receives typed normalized inputs.
-/
namespace PostIncidentProofs.Lineage.Graph

structure Edge where
  src : String
  dst : String
  deriving Repr, DecidableEq

structure Graph where
  nodes : List String
  edges : List Edge
  deriving Repr

/-- Membership helper. -/
def containsNode (nodes : List String) (n : String) : Bool :=
  nodes.contains n

/-- Every edge endpoint appears in `nodes`. -/
def refsResolve (g : Graph) : Bool :=
  g.edges.all fun e => containsNode g.nodes e.src && containsNode g.nodes e.dst

/-- Remove one occurrence of `x` from a list. -/
def removeOne : List String → String → List String
  | [], _ => []
  | y :: ys, x => if y == x then ys else y :: removeOne ys x

/-- Out-neighbors of `n`. -/
def successors (edges : List Edge) (n : String) : List String :=
  (edges.filter (fun e => e.src == n)).map (fun e => e.dst)

/-- Count inbound edges to `n`. -/
def inDegree (edges : List Edge) (n : String) : Nat :=
  (edges.filter (fun e => e.dst == n)).length

/-- Kahn-style layer peel: nodes with indegree 0 among remaining. -/
partial def kahnFuel (fuel : Nat) (nodes : List String) (edges : List Edge) : Bool :=
  match fuel with
  | 0 => nodes.isEmpty
  | fuel'+1 =>
    if nodes.isEmpty then true
    else
      let zeros := nodes.filter (fun n => inDegree edges n == 0)
      if zeros.isEmpty then false
      else
        let n := zeros.head!
        let nodes' := removeOne nodes n
        let edges' := edges.filter (fun e => e.src != n)
        kahnFuel fuel' nodes' edges'

/-- Acyclicity via bounded Kahn iteration (fuel = |nodes|+1). -/
def isAcyclic (g : Graph) : Bool :=
  kahnFuel (g.nodes.length + 1) g.nodes g.edges

/-- Combined structural OK predicate used by deciders. -/
def structurallyValid (g : Graph) : Bool :=
  refsResolve g && isAcyclic g

/-- If Kahn reports acyclic on empty graph, property holds. -/
theorem isAcyclic_nil : isAcyclic ⟨[], []⟩ = true := by
  native_decide

/-- Resolved refs on empty edge set. -/
theorem refsResolve_no_edges (nodes : List String) :
    refsResolve ⟨nodes, []⟩ = true := by
  simp [refsResolve]

/-- Soundness (executable mirror): true result implies refs resolve. -/
theorem structurallyValid_implies_refs (g : Graph)
    (h : structurallyValid g = true) : refsResolve g = true := by
  simp [structurallyValid] at h
  exact h.1

/-- Soundness: true result implies acyclicity bit is true. -/
theorem structurallyValid_implies_acyclic (g : Graph)
    (h : structurallyValid g = true) : isAcyclic g = true := by
  simp [structurallyValid] at h
  exact h.2

/-- Concrete DAG fixture used as a conformance anchor. -/
def exampleDag : Graph :=
  { nodes := ["a", "b", "c"]
    edges := [⟨"a", "b"⟩, ⟨"b", "c"⟩] }

theorem exampleDag_acyclic : isAcyclic exampleDag = true := by
  native_decide

theorem exampleDag_valid : structurallyValid exampleDag = true := by
  native_decide

/-- Concrete cyclic fixture. -/
def exampleCycle : Graph :=
  { nodes := ["a", "b"]
    edges := [⟨"a", "b"⟩, ⟨"b", "a"⟩] }

theorem exampleCycle_not_acyclic : isAcyclic exampleCycle = false := by
  native_decide

end PostIncidentProofs.Lineage.Graph
