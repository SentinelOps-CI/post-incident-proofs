.PHONY: help build test benchmark security observability validate ci release

help:
	@echo "Available targets: build test benchmark security observability validate ci release"

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

ci: build test security observability validate benchmark
	@echo "CI pipeline completed"

release: ci
	@mkdir -p dist
	tar -czf dist/post-incident-proofs-source.tar.gz src lakefile.lean lean-toolchain README.md
	@echo "Release artifact created at dist/post-incident-proofs-source.tar.gz"
