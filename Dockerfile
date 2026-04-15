FROM leanprover/lean4:4.7.0 AS builder
WORKDIR /app
COPY . .
RUN lake build

FROM ubuntu:22.04 AS runtime
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/.lake /app/.lake
COPY --from=builder /app/lakefile.lean /app/lakefile.lean
COPY --from=builder /app/lean-toolchain /app/lean-toolchain
COPY --from=builder /app/src /app/src

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["lake", "exe", "validate"]
