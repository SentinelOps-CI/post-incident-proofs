use std::io::{self, Read};
use std::process::ExitCode;

use base64::{engine::general_purpose::STANDARD as B64, Engine};
use clap::{Parser, Subcommand};
use post_incident_kernel::{
    envelope_structurally_valid, is_acyclic, is_retained_subsequence, sha256_digest,
};
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Parser, Debug)]
#[command(name = "post-incident-kernel", about = "PIP-ITE Rust kernel")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// SHA-256 digest of stdin JSON {"data_b64": "..."} or raw stdin with --raw
    Digest {
        #[arg(long)]
        raw: bool,
    },
    /// DAG check from stdin JSON {"edges":[{"from":"a","to":"b"}, ...]}
    DagCheck,
    /// Order subsequence check {"full":[...],"retained":[...]}
    OrderCheck,
    /// Envelope structural validate {"envelope":{...}}
    EnvelopeCheck,
}

#[derive(Deserialize)]
struct DigestIn {
    data_b64: String,
}

#[derive(Deserialize)]
struct Edge {
    from: String,
    to: String,
}

#[derive(Deserialize)]
struct DagIn {
    edges: Vec<Edge>,
}

#[derive(Deserialize)]
struct OrderIn {
    full: Vec<String>,
    retained: Vec<String>,
}

fn read_stdin() -> io::Result<String> {
    let mut buf = String::new();
    io::stdin().read_to_string(&mut buf)?;
    Ok(buf)
}

fn fail(message: &str) -> ExitCode {
    println!(
        "{}",
        serde_json::to_string_pretty(&json!({
            "status": "error",
            "code": "parse_failed",
            "message": message
        }))
        .expect("serialize error payload")
    );
    ExitCode::from(2)
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let input = match read_stdin() {
        Ok(s) => s,
        Err(err) => return fail(&format!("stdin read failed: {err}")),
    };

    let result = match cli.command {
        Commands::Digest { raw } => {
            let digest = if raw {
                sha256_digest(input.as_bytes())
            } else {
                let parsed: DigestIn = match serde_json::from_str(&input) {
                    Ok(v) => v,
                    Err(err) => return fail(&format!("digest input JSON invalid: {err}")),
                };
                let bytes = match B64.decode(parsed.data_b64.as_bytes()) {
                    Ok(b) => b,
                    Err(err) => return fail(&format!("data_b64 decode failed: {err}")),
                };
                sha256_digest(&bytes)
            };
            json!({ "status": "ok", "digest": digest })
        }
        Commands::DagCheck => {
            let parsed: DagIn = match serde_json::from_str(&input) {
                Ok(v) => v,
                Err(err) => return fail(&format!("dag-check input JSON invalid: {err}")),
            };
            let edges: Vec<(String, String)> =
                parsed.edges.into_iter().map(|e| (e.from, e.to)).collect();
            json!({ "status": "ok", "acyclic": is_acyclic(&edges) })
        }
        Commands::OrderCheck => {
            let parsed: OrderIn = match serde_json::from_str(&input) {
                Ok(v) => v,
                Err(err) => return fail(&format!("order-check input JSON invalid: {err}")),
            };
            json!({
                "status": "ok",
                "preserved": is_retained_subsequence(&parsed.full, &parsed.retained)
            })
        }
        Commands::EnvelopeCheck => {
            let parsed: Value = match serde_json::from_str(&input) {
                Ok(v) => v,
                Err(err) => return fail(&format!("envelope-check input JSON invalid: {err}")),
            };
            let env = parsed.get("envelope").cloned().unwrap_or(parsed);
            json!({ "status": "ok", "valid": envelope_structurally_valid(&env) })
        }
    };
    println!(
        "{}",
        serde_json::to_string_pretty(&result).expect("serialize")
    );
    ExitCode::SUCCESS
}
