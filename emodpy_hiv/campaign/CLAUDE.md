# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this directory.

## Campaign Module Overview

This package implements HIV-specific EMOD campaign configuration. It provides interventions, event coordinators, and distribution strategies on top of the base `emodpy` framework.

## Module Roles

| Module | Role |
|--------|------|
| `common.py` | Defines `NChooserTargetedDistributionHIV` (who/when/how-many targeting); re-exports shared emodpy types |
| `individual_intervention.py` | 30+ HIV-specific individual-level interventions (ART, diagnostics, PMTCT, circumcision, etc.) |
| `node_intervention.py` | Re-exports node-level interventions from emodpy unchanged |
| `waning_config.py` | Re-exports waning config classes from emodpy unchanged |
| `event_coordinator.py` | `NChooserEventCoordinatorHIV` (exact-N targeting) and `ReferenceTrackingEventCoordinatorTrackingConfig` (coverage maintenance) |
| `distributor.py` | `add_intervention_nchooser_df()`, `add_intervention_reference_tracking()`; re-exports `add_intervention_scheduled` and `add_intervention_triggered` from emodpy |
| `cascade_of_care.py` | Complete HIV cascade of care — assembles testing, staging, linkage, and ART states using the other modules |

## Key Abstractions

### NChooser vs. Reference Tracking vs. Scheduled/Triggered

- **NChooser** (`add_intervention_nchooser_df`): Distribute to exactly N individuals. Takes a DataFrame with columns `year`, `min_age`, `max_age`, and either `num_targeted` or `num_targeted_female`/`num_targeted_male`. Wraps in `NChooserEventCoordinatorHIV`.
- **Reference Tracking** (`add_intervention_reference_tracking`): Automatically distributes to maintain a desired coverage level over time. Configured with a `time_value_map`, a `tracking_config` (what to count as numerator), and a `targeting_config` (denominator population).
- **Scheduled** / **Triggered**: Imported directly from emodpy via `distributor.py`.

### Cascade of Care Structure

`cascade_of_care.py` builds the HIV care cascade by composing discrete state functions. Key enums:
- `CustomEvent`: Named broadcast events that drive state transitions (e.g., `HCT_TESTING_LOOP_0`, `LINKING_TO_ART_0`)
- `CascadeState`: Individual property values representing cascade position (e.g., `ON_ART`, `LOST_FOREVER`)

The main entry points are:
- `add_ART_cascade()` — wires together staging, linkage, pre-ART, and ART states
- `add_health_care_testing()` / `add_state_HCTTestingLoop()` / `add_state_TestingOnANC()` etc. — testing touchpoints
- `add_pmtct()`, `add_vmmc_reference_tracking()`, `add_historical_vmmc_nchooser()` — prevention interventions
- `add_csw()` — commercial sex worker dynamics

State transitions rely on `HIVMuxer`, `HIVRandomChoice`, `HIVPiecewiseByYearAndSexDiagnostic`, and `HIVSigmoidByYearAndSexDiagnostic` to route individuals and broadcast events.

### Intervention Pattern

All individual interventions follow the same constructor signature:
```python
MyIntervention(campaign, common_intervention_params=CommonInterventionParameters(...), ...)
```
and call `super().add_to_campaign(campaign)` to register themselves.

### Sigmoid and Piecewise Helpers

`Sigmoid` (in `individual_intervention.py`) defines a sigmoidal probability curve with `min`, `max`, `mid`, `rate` parameters — used in `HIVSigmoidByYearAndSexDiagnostic` and similar classes for year-dependent behavior.

## Import Dependency Order

```
waning_config.py  ←  (no internal deps)
node_intervention.py  ←  (no internal deps)
common.py  ←  emodpy, utils/
individual_intervention.py  ←  common, waning_config, utils/
event_coordinator.py  ←  common, emodpy
distributor.py  ←  common, event_coordinator, individual_intervention, utils/
cascade_of_care.py  ←  individual_intervention, common, distributor, utils/
```