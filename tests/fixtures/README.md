# Portable regression fixtures

- `spec48-ticket60-contract-M/` contains only the 17 public resource/license files
  used by the retirement contract, plus reviewed counterpart bytes where an
  allowed control adaptation changed them. The tests compare exact bytes and
  retain their mutation/reversion counterexamples without requiring historical
  Git objects. Partial Markdown resources use `.fixture` extensions so the
  repository-wide Markdown link checker does not treat them as complete docs.
- `spec48-archive-history.tsv` pins only the eight public archive names and
  SHA-256 identities used by the README contract. It does not contain archive
  payloads or claim that those payloads are available or authenticated.
- `spec48-ticket60-c01-baseline/` contains two public product files for the
  opt-in pre-fix installation counterexample. It makes that negative run
  portable without reading an arbitrary local commit; the files likewise use a
  neutral `.fixture` extension.

No `.agents` notes, private working notes, or local evidence are fixtures.
