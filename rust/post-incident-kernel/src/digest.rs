use sha2::{Digest, Sha256};

/// Return `sha256:<hex>` for raw bytes.
pub fn sha256_digest(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    format!("sha256:{}", hex::encode(hasher.finalize()))
}

pub fn verify_digest(data: &[u8], declared: &str) -> bool {
    sha256_digest(data) == declared
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_empty_digest() {
        assert_eq!(
            sha256_digest(b""),
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
    }
}
