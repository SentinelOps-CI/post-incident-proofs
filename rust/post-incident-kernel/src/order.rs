/// Retained events must form an order-preserving subsequence of the full event list.
pub fn is_retained_subsequence(full: &[String], retained: &[String]) -> bool {
    if retained.is_empty() {
        return true;
    }
    let mut i = 0usize;
    for item in full {
        if item == &retained[i] {
            i += 1;
            if i == retained.len() {
                return true;
            }
        }
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn subsequence_ok() {
        let full = vec!["a".into(), "b".into(), "c".into(), "d".into()];
        let retained = vec!["a".into(), "c".into()];
        assert!(is_retained_subsequence(&full, &retained));
    }

    #[test]
    fn reordered_fails() {
        let full = vec!["a".into(), "b".into(), "c".into()];
        let retained = vec!["c".into(), "a".into()];
        assert!(!is_retained_subsequence(&full, &retained));
    }
}
