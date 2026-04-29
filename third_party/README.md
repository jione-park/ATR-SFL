# Third-Party References

This directory stores external codebases used as read-only references during Hermes research and implementation.

Current references:

- `FeSViBS/`
  - upstream: `https://github.com/faresmalik/FeSViBS`
  - inspected commit: `dc66070770c44dc9362201f6869f1b621e3c013b`

Rules:

- Do not treat code under `third_party/` as Hermes-owned implementation.
- Prefer re-implementing Hermes logic under `src/` instead of editing third-party code directly.
- If a file from a third-party reference is ported or adapted, record that in the relevant plan or implementation note.
