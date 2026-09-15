# Venue and format branch

Read when the user names a venue, track, year, submission stage or template. Adapted from Orchestra’s template-handling and checklist methods; historical venue tables and vendored templates are deliberately not shipped as current requirements.

## Official rules first

1. Identify the exact venue, year, track/article type and review/preprint/camera-ready stage from the request. Ask only for missing distinctions that change the requested output. With no venue, draft in the user’s format or Markdown and state that venue compliance was not checked.
2. Within the authorized read-only search budget, find that edition’s official author guide, CFP, style files and applicable checklist. Follow links from the official venue site; a search snippet, third-party template or past-year guide is not confirmation of the current rule.
3. In drafting notes record the official URLs, access date, edition/stage and specific rules that affect the requested draft: page/word limits and what counts; language; anonymous author/acknowledgment/repository treatment; required sections; ethics, AI-use and reproducibility disclosures; reference style; appendix/supplement policy. Read each applicable rule rather than assuming all conferences share it.
4. Compare the user’s template with those rules. Show each conflict and ask which path to take. Wait before changing affected formatting or producing a supposedly compliant full draft. The user may keep a conflicting template for an internal draft; record that decision and the remaining noncompliance, never call it officially compliant.
5. If official pages cannot be reached or the requested edition has no published rules, mark the check unresolved. Ask for official material or permission to proceed as a generic draft; do not silently substitute an older edition or install a browser/tool.

**Done**: each relevant constraint has an official source or a named unknown; every template conflict has an explicit user decision before affected work resumes.

## Existing LaTeX template

- Inspect the authorized local template’s main file, referenced style/bibliography files, examples, macros and include relationships. Preserve the complete set actually needed for the existing template rather than copying only `main.tex` and inventing missing `.sty` files.
- User-provided template assets keep their license/attribution. This Skill supplies no conference template and grants no license to external assets. Downloading or copying a new template into the project requires the appropriate write scope; check its included license first.
- Replace example content section by section in the approved destination. Read each example’s formatting and macros before using that pattern. Keep original examples in the source template, not as invented research content in the candidate draft.
- Reuse current notation and template commands; add paper-specific notation only in an authorized draft-local file and avoid duplicate definitions. Do not merge unrelated preambles, alter style files, margins or fonts to squeeze in content, or switch citation packages arbitrarily.
- Check that referenced sections, graphics, bibliography and macros exist; missing assets become visible gaps. Existing project structure is valid—one file per section is useful but not mandatory.
- Upstream’s compile-before-edit and compile-after-section methods belong to a separately authorized compilation check. Drafting does not run builds, install missing TeX packages or repair the user’s environment. Ask the user for an existing build report if relevant, otherwise mark compilation and page count untested.
- At handoff, identify unused example content or stale includes in the authorized candidate draft. Fix draft-local references when allowed; propose removal of other files instead of deleting them. Actual PDF layout, rendering and page counts remain unverified without a real build/inspection.

**Done**: draft-local source references are checked, preserved assets and unresolved dependencies are listed, and no source-only check is labeled a successful build.
