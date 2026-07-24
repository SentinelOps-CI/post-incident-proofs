use serde_json::Value;

/// Structural check for PCS ArtifactIntegrity.v1-shaped envelopes (no crypto verify here).
pub fn envelope_structurally_valid(envelope: &Value) -> bool {
    let Some(obj) = envelope.as_object() else {
        return false;
    };
    if obj.get("schema_version").and_then(|v| v.as_str()) != Some("v1") {
        return false;
    }
    if obj.get("canonicalization_version").and_then(|v| v.as_str()) != Some("v1") {
        return false;
    }
    let Some(digest) = obj.get("artifact_digest").and_then(|v| v.as_str()) else {
        return false;
    };
    if !digest.starts_with("sha256:") || digest.len() != 71 {
        return false;
    }
    let Some(sig) = obj.get("signature").and_then(|v| v.as_object()) else {
        return false;
    };
    if sig.get("algorithm").and_then(|v| v.as_str()) != Some("ed25519") {
        return false;
    }
    for key in ["key_id", "signed_at", "value"] {
        if sig
            .get(key)
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .is_empty()
        {
            return false;
        }
    }
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn valid_shape() {
        let env = json!({
            "schema_version": "v1",
            "artifact_type": "IncidentSourceRecord",
            "canonicalization_version": "v1",
            "artifact_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "signature": {
                "algorithm": "ed25519",
                "key_id": "test-key",
                "signed_at": "2026-01-01T00:00:00Z",
                "value": "AQID"
            }
        });
        assert!(envelope_structurally_valid(&env));
    }
}
