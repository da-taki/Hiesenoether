# Limitations

This is a small benchmark run over 13 base tasks and 26 normal/warned prompt variants derived from validated package witnesses. Several tasks share packages, transformation families, or witness structure, so results should not be interpreted as prevalence estimates.

Sol, Terra, and Luna are Codex task-model configurations. They should not be described as independent providers or as OpenAI API runs. The run records the actual Codex model identifiers and exposed settings where available, but temperature and seed were not exposed.

The completed frozen primary study found five verified OSDS divergences across Terra and Luna and none for Sol. All five occurred in hidden-observation cases and were silent under ordinary tests. Ordinary programming bugs and invalid patches were counted separately and should not be used as OSDS evidence.

The study does not make a real-world prevalence claim. It evaluates behavior preservation on a curated benchmark built from pre-existing real-package witnesses.
