# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`emodpy-hiv` is a Python package that extends `emodpy` with HIV-specific campaign, demographics, and reporting classes for the EMOD epidemiological simulator. It targets Python 3.11–3.14 and is published to PyPI.

## Common Commands

### Installation
```bash
pip install -e .[test]        # Install in editable mode with test dependencies
pip install -e .[docs]        # Install with documentation dependencies
pip install -e .[lint]        # Install with lint dependencies
```

### Running Tests
```bash
# All unit tests
cd tests && pytest unittests/ -m unit

# Single test file
cd tests && pytest unittests/test_campaign_common.py

# Single test by name
cd tests && pytest unittests/test_campaign_common.py::TestClassName::test_method_name

# Container tests (require EMOD container platform)
cd tests && pytest -m container

# Basic smoke test
cd tests && pytest unittests/test_emod_hiv_package.py
```

### Linting
```bash
flake8 emodpy_hiv/           # Ignores E501, E261, W503 per CI config
```

### Building
```bash
make package                  # Builds wheel to dist/
make install                  # Installs latest wheel from dist/
```

### Version Bumping
```bash
make bump_patch               # Bumps patch version in pyproject.toml
```

### Documentation
```bash
pip install -e .[docs]
python -m sphinx -T --keep-going -b html ./docs ./site
```

## Test Markers

Tests are organized by pytest markers (defined in `tests/pytest.ini`):
- `unit` — no EMOD runtime required, runs in CI on Linux and Windows
- `container` — requires the EMOD container platform (Linux CI only)
- `comps` — COMPS-based tests
- `country` — country model tests

## Architecture

### Package Layout (`emodpy_hiv/`)

- **`campaign/`** — HIV-specific EMOD campaign interventions (cascade of care, individual/node interventions, event coordinators, waning configs, distributors)
- **`demographics/`** — Population modeling: relationship types, society structure, concurrency, pair formation, assortivity, condom usage, risk groups, and UN world population data integration
- **`reporters/`** — HIV-specific EMOD reporters (`reporters.py` is the primary large module)
- **`plotting/`** — Visualization helpers for inset charts, age/gender breakdowns, relationship events
- **`countries/`** — Country-specific model implementations (currently Zambia) with CSV config data and data conversion utilities
- **`utils/`** — Shared utilities: config helpers, distributions, enums, targeting config
- **`country_model.py`** — Base `Country` class that country-specific implementations inherit from

### Key Design Patterns

- **Country model pattern**: `country_model.py` defines a base `Country` class. Country-specific subclasses (e.g., in `countries/zambia/`) override methods to configure demographics, campaigns, and reports for that country. Tutorials (`tutorials/`) demonstrate this pattern.
- **Cascade of Care (CoC)**: `campaign/cascade_of_care.py` implements the HIV testing/treatment cascade. Tutorial 4 shows how to override it.
- **Demographics pipeline**: Demographics is built using a hierarchy — `hiv_demographics.py` → `society.py` → `relationship_parameters.py` / `concurrency_parameters.py` / etc.
- **UN population data**: `demographics/un_world_pop.py` and `demographics/un_world_pop_data/` integrate UN demographic projections for mortality calibration.

### Dependency Notes

- `emodpy~=3.0` — the base EMOD Python framework
- `emod-hiv==2.30.0` — the pinned EMOD HIV binary/schema (exact version matters)
- `pandas~=3.0`, `scikit-learn~=1.8` — used in demographics calculations

### CI/CD

- Patch version is auto-bumped on every push to `main` that modifies `emodpy_hiv/` or `pyproject.toml`.
- PyPI publishing is manual (workflow dispatch on `publish_pypi.yml`).
- Docs are auto-deployed to GitHub Pages on push to `main`.