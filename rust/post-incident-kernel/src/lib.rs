//! PIP-ITE kernel: real SHA-256, DAG acyclicity, order subsequence, envelope shape.

pub mod dag;
pub mod digest;
pub mod envelope;
pub mod order;

pub use dag::is_acyclic;
pub use digest::{sha256_digest, verify_digest};
pub use envelope::envelope_structurally_valid;
pub use order::is_retained_subsequence;
