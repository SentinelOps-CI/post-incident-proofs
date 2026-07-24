use std::collections::{HashMap, HashSet, VecDeque};

/// Kahn topological sort: returns true iff the directed graph is a DAG.
pub fn is_acyclic(edges: &[(String, String)]) -> bool {
    let mut nodes: HashSet<String> = HashSet::new();
    let mut indeg: HashMap<String, usize> = HashMap::new();
    let mut adj: HashMap<String, Vec<String>> = HashMap::new();

    for (a, b) in edges {
        nodes.insert(a.clone());
        nodes.insert(b.clone());
        adj.entry(a.clone()).or_default().push(b.clone());
        *indeg.entry(b.clone()).or_insert(0) += 1;
        indeg.entry(a.clone()).or_insert(0);
    }

    let mut q: VecDeque<String> = indeg
        .iter()
        .filter_map(|(n, d)| if *d == 0 { Some(n.clone()) } else { None })
        .collect();

    let mut seen = 0usize;
    while let Some(n) = q.pop_front() {
        seen += 1;
        if let Some(neighbors) = adj.get(&n) {
            for m in neighbors {
                if let Some(d) = indeg.get_mut(m) {
                    *d -= 1;
                    if *d == 0 {
                        q.push_back(m.clone());
                    }
                }
            }
        }
    }
    seen == nodes.len()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dag_ok() {
        let edges = vec![("a".into(), "b".into()), ("b".into(), "c".into())];
        assert!(is_acyclic(&edges));
    }

    #[test]
    fn cycle_detected() {
        let edges = vec![("a".into(), "b".into()), ("b".into(), "a".into())];
        assert!(!is_acyclic(&edges));
    }
}
