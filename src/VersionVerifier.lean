import PostIncidentProofs.Version.Diff
import PostIncidentProofs.Version.Verification

def main (_args : List String) : IO UInt32 := do
  let state := PostIncidentProofs.Version.State.new "s" "v1".toUTF8 []
  let diff := PostIncidentProofs.Version.Diff.Mod "s" "v2".toUTF8
  let ok := PostIncidentProofs.Version.Verification.verify_diff_roundtrip state diff
  IO.println s!"version_verifier: {if ok then "PASS" else "FAIL"}"
  pure (if ok then 0 else 1)
