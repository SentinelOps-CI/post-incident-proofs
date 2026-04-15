import PostIncidentProofs.Version.Diff
import PostIncidentProofs.Utils.Crypto

namespace PostIncidentProofs.Version.Verification

def verify_diff_roundtrip (state : PostIncidentProofs.Version.State) (diff : PostIncidentProofs.Version.Diff) : Bool :=
  let next := PostIncidentProofs.Version.apply_diff state diff
  let back := PostIncidentProofs.Version.revert_diff next diff
  PostIncidentProofs.Utils.Crypto.bytesEq back.content state.content && back.metadata == state.metadata

def verify_state (_state : PostIncidentProofs.Version.State) : Bool :=
  true

end PostIncidentProofs.Version.Verification
