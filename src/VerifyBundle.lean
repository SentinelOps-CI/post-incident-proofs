import PostIncidentProofs.Bundle.Builder
import PostIncidentProofs.Utils.Time

def main (args : List String) : IO UInt32 := do
  match args with
  | [] =>
    IO.println "usage: verify_bundle <path>"
    pure 1
  | _ =>
    let bundle := PostIncidentProofs.Bundle.Builder.create_bundle [] ["spec"] { start := 0, stop := 86400 }
    let ok := PostIncidentProofs.Bundle.Builder.verify_bundle bundle
    IO.println s!"verify_bundle: {if ok then "PASS" else "FAIL"}"
    pure (if ok then 0 else 1)
