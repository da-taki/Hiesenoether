# Supplement Dependency Audit

Repository-local imports were parsed from every Python file in the reviewer supplement. External package imports are excluded from this local-file audit and are covered by REPRODUCE.md dependency checks.

| Script | Local import | Resolved file | Status |
| --- | --- | --- | --- |
| `experiments/agent_behavior_preservation/agent_bp/providers.py` | `cases` | `experiments/agent_behavior_preservation/agent_bp/cases.py` | `resolved` |
| `experiments/agent_behavior_preservation/agent_bp/providers.py` | `self_assessment` | `experiments/agent_behavior_preservation/agent_bp/self_assessment.py` | `resolved` |
| `experiments/agent_behavior_preservation/causal_controls/run_model_failure_causal_controls.py` | `agent_bp.execution` | `experiments/agent_behavior_preservation/agent_bp/execution.py` | `resolved` |
| `experiments/agent_behavior_preservation/causal_controls/run_model_failure_causal_controls.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `agent_bp.cases` | `experiments/agent_behavior_preservation/agent_bp/cases.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `agent_bp.execution` | `experiments/agent_behavior_preservation/agent_bp/execution.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `agent_bp.patching` | `experiments/agent_behavior_preservation/agent_bp/patching.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `agent_bp.providers` | `experiments/agent_behavior_preservation/agent_bp/providers.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `agent_bp.schema` | `experiments/agent_behavior_preservation/agent_bp/schema.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_baselines.py` | `agent_bp.execution` | `experiments/agent_behavior_preservation/agent_bp/execution.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_baselines.py` | `runners.run_benchmark` | `experiments/agent_behavior_preservation/runners/run_benchmark.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_baselines.py` | `runners.validate_existing_witnesses` | `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_baselines.py` | `metamorphic_candidates` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_candidates.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_baselines.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `metamorphic_candidates` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_candidates.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `run_branch_flip_cases` | `paper_artifacts/scp_realcode_metamorphic_oracle/run_branch_flip_cases.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `run_metamorphic_controls` | `paper_artifacts/scp_realcode_metamorphic_oracle/run_metamorphic_controls.py` | `resolved` |
| `experiments/agent_behavior_preservation/runners/validate_existing_witnesses.py` | `run_metamorphic_oracle` | `paper_artifacts/scp_realcode_metamorphic_oracle/run_metamorphic_oracle.py` | `resolved` |
| `paper_artifacts/scp_realcode_metamorphic_oracle/run_branch_flip_cases.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `paper_artifacts/scp_realcode_metamorphic_oracle/run_metamorphic_controls.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `paper_artifacts/scp_realcode_metamorphic_oracle/run_metamorphic_oracle.py` | `metamorphic_fixtures` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py` | `resolved` |
| `paper_artifacts/scp_realcode_metamorphic_oracle/run_metamorphic_oracle.py` | `metamorphic_candidates` | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_candidates.py` | `resolved` |

Python files audited: 23
Frozen candidate syntax parse failures recorded: 0
Unresolved repository-local imports for documented reproduction commands: 0
