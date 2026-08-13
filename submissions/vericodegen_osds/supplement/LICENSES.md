# License and Asset Provenance

This anonymized supplement contains original benchmark prompts, frozen replay metadata, analysis tables, reproduction scripts, and paper-support artifacts for review. Original supplement code and new benchmark artifacts are supplied under the repository's MIT license. The author-identifying copyright notice from the repository root license is not repeated in this anonymous review package.

Frozen Codex task-model responses are included as research artifacts to reproduce the reported replay classifications. No license is asserted over model-provider output beyond inclusion for review and reproducibility. No model weights, proprietary APIs, credentials, virtual environments, package caches, scraped datasets, or human-subject data are redistributed.

The official VeriCodeGen workshop submission template is included only as the unmodified style file required for source compilation. It is not relicensed by this supplement.

## Third-Party Assets

| Asset | Version or source | License or terms recorded | Use in supplement |
| --- | --- | --- | --- |
| httpcore | 1.0.9, PyPI and project source | BSD License classifier | Witness metadata, prompt context, replay imports; no full package source redistributed |
| PyYAML | 6.0.3, PyPI | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| pytest | 8.3.5, PyPI | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| Python-Markdown | 3.10.2 source distribution | BSD 3-Clause License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| more-itertools | 11.0.2 source distribution | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| docutils | 0.22.4, PyPI classifiers | Public Domain, BSD License, GPL classifiers | Witness metadata, prompt context, replay imports; no full package source redistributed |
| beautifulsoup4 | 4.14.3, PyPI | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| boltons | 25.0.0, PyPI | BSD License classifier | Witness metadata, prompt context, replay imports; no full package source redistributed |
| Cerberus | 1.3.8, PyPI | ISC License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| dnspython | 2.8.0, PyPI | ISC License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| h11 | 0.16.0, PyPI | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| anyio | 4.13.0 source distribution | MIT License | Witness metadata, prompt context, replay imports; no full package source redistributed |
| Codex task-model responses | frozen raw JSONL outputs | Generated research artifacts; no model code or weights redistributed | Replay-only behavioral evidence |
| VeriCodeGen workshop style | public Overleaf template linked from workshop CFP | Official submission-template terms; unmodified style file | Source-package compilation |

All package rows above are used for behavioral witness descriptions and local replay of small package-shaped code paths. The supplement does not redistribute complete third-party package source trees.
