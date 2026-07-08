# AGENTS.md

## Cursor Cloud specific instructions

This repository is the **Sphinx documentation source** for the "Razor Enhanced" Python
scripting API. There is no backend/frontend/database — the only "application" is the
generated HTML docs site.

### Build / lint the docs
- Sphinx CLI scripts install to `~/.local/bin`, which is not on `PATH`. Invoke Sphinx as a
  module instead: `python3 -m sphinx -b html . _build/html` (run from the repo root, where
  `conf.py` lives).
- The build currently emits ~180 warnings. These come from formatting issues in the `.rst`
  source (e.g. inline markup / indentation), not from the environment or missing deps — the
  build still succeeds. Treat a non-zero build exit (not warnings) as a real failure.
- For lint-style feedback, add `-W --keep-going` to turn warnings into errors while still
  building; do not use bare `-W` since the first warning would abort the build.

### Run / preview the docs
- After building, serve the output for browser preview:
  `cd _build/html && python3 -m http.server 8000` then open `http://localhost:8000/index.html`.
- For live-reload during editing: `python3 -m sphinx_autobuild . _build/html` (serves on
  port 8000 and rebuilds on file changes).

### Notes
- There is no dependency manifest committed (no `requirements.txt`/`pyproject.toml`). The
  only dependencies are `sphinx` and `sphinx_rtd_theme` (see the update script).
- `index.rst` contains `.. automodule::AutoComplete` / `.. autoclass::Player` lines with no
  space after `::`; these are parsed as comments (autodoc is not enabled in `conf.py`), so
  the ~6,800-line `AutoComplete.py` stub is not imported at build time.
