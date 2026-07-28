import Lean.Data.Json

namespace PostIncidentProofs.Bundle.PFCore

/-- Required PF-Core emit-artifacts files (five-file layout). -/
def requiredArtifactFiles : List String := [
  "runtime_observation.json",
  "event.json",
  "trace.json",
  "certificate.json",
  "audit.jsonl"
]

structure PFCoreArtifacts where
  bundleDir : String
  pfCoreVersion : Option String
  deriving Repr

def parseArgs (args : List String) : Option PFCoreArtifacts := Id.run do
  let mut bundleDir? : Option String := none
  let mut version? : Option String := none
  let mut i := 0
  while h : i < args.length do
    let arg := args[i]
    if arg == "--bundle-dir" then
      if h' : i + 1 < args.length then
        bundleDir? := some args[i + 1]
        i := i + 2
        continue
      else
        return none
    if arg == "--pf-core-version" then
      if h' : i + 1 < args.length then
        version? := some args[i + 1]
        i := i + 2
        continue
      else
        return none
    if bundleDir?.isNone && !arg.startsWith "-" then
      bundleDir? := some arg
    i := i + 1
  match bundleDir? with
  | none => none
  | some dir => some { bundleDir := dir, pfCoreVersion := version? }

def bundleFilesPresent (bundleDir : String) : IO Bool := do
  for name in requiredArtifactFiles do
    let path := s!"{bundleDir}/{name}"
    if !(← System.FilePath.pathExists path) then
      return false
  return true

def runPythonVerifier (artifacts : PFCoreArtifacts) : IO UInt32 := do
  let script := "scripts/verify_pf_core_bundle.py"
  if !(← System.FilePath.pathExists script) then
    IO.println "verify_bundle: missing scripts/verify_pf_core_bundle.py"
    return 1
  let mut procArgs : Array String := #["--bundle-dir", artifacts.bundleDir]
  match artifacts.pfCoreVersion with
  | some v => procArgs := procArgs ++ #["--pf-core-version", v]
  | none => pure ()
  let proc ← IO.Process.spawn {
    cmd := "python3"
    args := #[script] ++ procArgs
    stdout := IO.Process.Stdio.inherited
    stderr := IO.Process.Stdio.inherited
  }
  let exitCode ← proc.wait
  return exitCode.toUInt32

def verifyPFCoreBundle (artifacts : PFCoreArtifacts) : IO UInt32 := do
  if !(← bundleFilesPresent artifacts.bundleDir) then
    IO.println s!"verify_bundle: missing PF-Core artifact files under {artifacts.bundleDir}"
    return 1
  runPythonVerifier artifacts

end PostIncidentProofs.Bundle.PFCore
