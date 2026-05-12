"""GA configuration aligned with module4_genetic_algorithm.ipynb."""

# GA Parameters (Based on TPOS paper - ga_parameter_tuning_TPOS.md)
# Defaults tuned for deeper search / slower early stop (more exploration).
POPULATION_SIZE = 150
MAX_GENERATIONS = 100
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.3
TOURNAMENT_SIZE = 2
ELITE_COUNT = 3
EARLY_STOPPING_THRESHOLD = 50

# Chromosome Configuration (TPOS approach)
INITIAL_CHROMOSOME_LENGTH = 6
MIN_POIS_PER_ROUTE = 4
MAX_POIS_PER_ROUTE = 15

# TPOS Penalty Values (ADJUSTED FOR GOA DATA SCALE)
HARD_VIOLATION_PENALTY = 1000
USER_PREFERENCE_PENALTY_MULTIPLIER = 1.0
DISTANCE_PENALTY_MULTIPLIER = 1.0
MUST_SEE_PENALTY_MULTIPLIER = 100
RESTAURANT_PENALTY = 100

# Time Configuration (TPOS spec)
TOUR_START_TIME = "09:00"
TOUR_END_TIME = "18:00"
LUNCH_START_TIME = "12:00"
LUNCH_END_TIME = "13:30"
DAILY_TIME_BUDGET_HOURS = 9

# POI Default Values
DEFAULT_VISIT_DURATION_MIN = 60
DEFAULT_OPENING_TIME = "09:00"
DEFAULT_CLOSING_TIME = "18:00"

# Visit Duration by Location Type (TPOS Section 7)
VISIT_DURATIONS = {
    "museum": 90,
    "park": 60,
    "shopping_mall": 120,
    "zoo": 120,
    "waterfall": 120,
    "default": 60,
}

# Travel Speed (Goa road conditions)
AVERAGE_SPEED_KM_H = 30

# Preference enforcement (module4 per-day and global targets)
PREFERRED_TAG_MIN_OVERALL = 2
PREFERRED_TAG_OVERALL_FRACTION = 0.6
MAX_DAILY_PREFERENCE_TAGS = 3
PREFERRED_TAG_DAILY_PENALTY = 4.0
PREFERRED_TAG_GLOBAL_MISSING_PENALTY = 2.0
PREFERRED_TAG_GLOBAL_REWARD = 0.6
PREFERRED_TAG_MAX_PER_DAY_CREDIT = 2
