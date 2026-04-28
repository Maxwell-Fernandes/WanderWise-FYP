# Module 4 GA, Fitness Preferences, and GA Config

## Overview
Module 4 is the route optimization stage. It runs a genetic algorithm (GA) per day, builds one primary itinerary plus alternatives, and emits JSON and map outputs. It also supports travel-type defaults and optional LLM-based fitness profile tuning.

## Key Files
- Module 4 engine: ../../backend/app/services/module4_service.py
- LLM fitness profile resolver: ../../backend/app/services/preference_fitness_llm.py
- GA defaults: ../../backend/app/services/ga_config.py
- Tests for LLM profile: ../../backend/tests/test_preference_fitness_llm.py

## End-to-End Flow
1. `run_module4_simulation()` seeds RNGs and loads GA defaults.
2. Payload overrides GA parameters (population, generations, rates, early stop) if provided.
3. `run_module1_simulation()` extracts interests and preferences.
4. `resolve_fitness_profile()` merges travel-type defaults with optional Groq LLM deltas and tag preferences.
5. `run_module2_simulation()` produces day clusters and POI pools.
6. For each day:
   - `prepare_day_matrices()` builds distance and duration matrices using OSRM, with a haversine fallback.
   - `optimize_route_ga()` evolves candidate routes and returns top alternatives.
   - Optional itinerary QA can trigger a retry with stricter weights or penalized POIs.
   - `build_day_json()` emits the route, fitness breakdown, and nearby suggestions.
7. Results are written to `exports/` and maps to `maps/`.

## GA Configuration (ga_config)
Default parameters live in ../../backend/app/services/ga_config.py and are pulled into Module 4 constants at import time.

Key defaults:
- Population: 120
- Generations: 90
- Crossover rate: 0.7
- Mutation rate: 0.2
- Tournament size: 2
- Elite count: 3
- Early stop threshold: 40
- Min/max POIs per route: 4 to 15
- Tour window: 09:00 to 18:00, lunch 12:00 to 13:30
- Average speed: 30 km/h

The payload can override `population_size`, `max_generations`, `mutation_rate`, `crossover_rate`, and `early_stopping_patience`.

## Fitness Model
Module 4 computes a fitness score as:

$$
fitness = \frac{reward}{1 + delta}
$$

Where `delta` is a weighted sum of penalties and `reward` is a weighted sum of bonuses. Weights come from `FitnessWeights` and travel-type profiles.

Key pieces:
- `FitnessWeights` defines per-penalty multipliers (distance, overtime, wrong_time, waterfall, fatigue, type_coverage, beach_dominance).
- `get_fitness_weights(travel_type)` returns the baseline multipliers per travel type.
- `get_default_tag_adjustments(travel_type)` applies tag-level rewards/penalties per travel type (e.g., family discourages strenuous waterfalls).
- `evaluate_fitness()` handles penalties and rewards including:
  - distance penalties with a quadratic term
  - lunch invasion and closed POI penalties
  - overtime and undertime penalties
  - waterfall and strenuous fatigue penalties
  - time-of-day penalties (beach scorch window, park time window)
  - type coverage bonus and missing-type penalty
  - beach dominance penalty
  - tag preference rewards/penalties
  - must-see and neighbor rewards

## Preference Fitness (LLM)
The optional Groq pass adjusts fitness weights and tag preferences once per run.

- `resolve_fitness_profile()`:
  - Uses `get_fitness_weights()` + `get_default_tag_adjustments()` as the baseline.
  - When `use_llm` is false or no API key, returns baseline.
  - When enabled, it prompts Groq for JSON with `weight_deltas` and `tag_preference`.
- `merge_fitness_weights()` clamps deltas to [-0.5, 0.5] and final weights to [0.25, 4.0].
- `tag_preference` is merged on top of travel-type defaults; keys not present keep the server default.

## Distance and Duration Matrices
- `prepare_day_matrices()` builds a per-day distance and duration matrix.
- OSRM Table API is used first; if it fails, a haversine fallback is used.

## Alternatives and QA Retry
- `optimize_route_ga()` keeps the top N diverse candidates by route difference.
- `select_exclusive_must_visit_alternatives()` prefers alternatives with unique must-visit POIs.
- Optional itinerary QA can trigger a retry that either excludes flagged POIs or applies penalties.

## Extension Points
- Add new travel types in `TRAVEL_TYPES` and update `get_fitness_weights()` and `get_default_tag_adjustments()`.
- Adjust penalty constants and time windows in `module4_service.py`.
- Update GA defaults in `ga_config.py`.
- Extend LLM tag keys in `preference_fitness_llm.py` to support new POI tags.
