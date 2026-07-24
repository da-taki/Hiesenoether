# Lean Mechanization Status

Lean 4 was not usable in the local environment for this work.

## Local Probe

- `lean` resolves to `<home>\.elan\bin\lean.exe`.
- `lake` resolves to `<home>\.elan\bin\lake.exe`.
- `lean --version` timed out locally.
- `lake --version` timed out locally.

Because the version and build commands did not complete, no compiled Lean file is included and no machine-checked theorem is claimed.

## Compiled Files

None.

## Compiled Theorem Names

None.

## Paper Meaning

The formal support for this branch is proof-auditable text plus exact symbolic scripts:

- `docs/formal_proof_appendix.md` gives full paper-level proofs for the deterministic and zero-divergence propositions under stated assumptions.
- `results/proof_support/claim_manifest.md` classifies each major claim by evidence level.
- `results/proof_support/running_example_derivation.md` gives an exact derivation of the central running example.

## Limitations

No statement in this branch should be described as machine-checked unless Lean is installed and a compiled proof file is added later. The paper can still state the proved propositions as paper proofs, but it should not claim Lean mechanization for them from this branch.

## Omitted or Weakened Theorems

All Lean theorem statements were omitted because the local Lean toolchain did not complete version checks. The corresponding paper propositions remain in the proof appendix, with explicit assumptions and claim boundaries.
