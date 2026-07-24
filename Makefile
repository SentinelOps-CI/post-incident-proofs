.PHONY: help build test benchmark security observability validate ci release ite ite-python ite-rust ite-lint lint-adr

help:
	@echo "Available targets: build test benchmark security observability validate ci release ite ite-python ite-rust ite-lint lint-adr"

build:
	lake build

test:
	lake exe tests

benchmark:
	lake exe benchmarks

security:
	lake exe security

observability:
	lake exe observability

validate:
	lake exe validate

lint-adr:
	python scripts/lint_adr_presence.py

ite-lint:
	python scripts/lint_adr_presence.py
	python scripts/lint_no_sorry.py
	python scripts/verify_pcs_pin.py
	ruff check python/post_incident python/tests
	mypy python/post_incident

ite-python:
	python -m pytest python/tests -q

ite-rust:
	cargo fmt --manifest-path rust/post-incident-kernel/Cargo.toml --check
	cargo clippy --manifest-path rust/post-incident-kernel/Cargo.toml -- -D warnings
	cargo test --manifest-path rust/post-incident-kernel/Cargo.toml

ite: ite-lint build ite-rust ite-python
	@echo "ITE pipeline completed"

ci: build test security observability validate benchmark
	@echo "Legacy CI pipeline completed"

release: ci
	@mkdir -p dist
	tar -czf dist/post-incident-proofs-source.tar.gz src lakefile.lean lean-toolchain README.md
	@echo "Release artifact created at dist/post-incident-proofs-source.tar.gz"
