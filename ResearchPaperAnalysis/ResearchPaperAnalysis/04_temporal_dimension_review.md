# Temporal Dimension Review: Time Windows and Opening Hours

## Table of Contents

1. [Introduction](#introduction)
2. [Time Window Modeling](#time-window-modeling)
3. [Opening Hours Integration](#opening-hours-integration)
4. [Constraint Handling Approaches](#constraint-handling-approaches)
5. [WanderWise+ Temporal Integration](#wanderwise-temporal-integration)
6. [Implementation Considerations](#implementation-considerations)
7. [Summary](#summary)
8. [References](#references)

---

## 1. Introduction

Temporal dimension modeling represents a critical aspect of tourist itinerary optimization that addresses the time-dependent constraints and preferences affecting attraction visitation. This documentation file reviews the research literature on temporal constraints in tourism optimization, focusing on time window modeling, opening hours integration, and constraint handling approaches that inform the WanderWise+ system implementation.

The temporal dimension adds significant complexity to the TTDP formulation by introducing time-dependent feasibility and quality constraints. Unlike spatial constraints that remain constant regardless of when attractions are visited, temporal constraints vary with the scheduled visit time. An attraction may be highly valuable but infeasible to visit if the scheduled time falls outside operating hours. Similarly, the queuing time and crowd levels at an attraction vary substantially depending on the time of day and day of week.

The research literature on temporal dimension in tourism optimization spans multiple decades, with foundational work on time windows in vehicle routing and scheduling extending naturally to tourist itinerary planning. The key challenge is balancing the flexibility of soft time preferences against the hard constraints of operating hours and realistic scheduling requirements. This balance determines both the feasibility of generated itineraries and their practical utility for tourists.

---

## 2. Time Window Modeling

### 2.1 Time Window Types

The research literature identifies multiple types of time windows applicable to tourist itinerary optimization:

**Hard Time Windows:**
Fixed operating hours during which attractions must be visited. Visiting outside hard time windows renders the itinerary infeasible. Example: A museum open 9 AM to 5 PM requires all visits within this window.

**Soft Time Windows:**
Preferred visiting periods with flexibility for visits outside the preferred window. Soft time windows may reflect optimal visiting times (e.g., avoiding midday heat at beaches) or crowd avoidance preferences. Visiting outside soft time windows incurs fitness penalties but does not invalidate the solution.

**Elapsed Time Windows:**
Minimum or maximum time requirements between attraction visits. These windows may reflect minimum visit duration requirements or maximum allowable gaps in the itinerary.

**Sequential Time Windows:**
Time windows that depend on the sequence of visits. Visiting one attraction may open or close time windows for subsequent attractions due to travel time requirements.

### 2.2 Mathematical Representation

Time windows are mathematically represented as constraints on visit times:

**Hard Window Constraint:**
```
openᵢ ≤ arrival_timeᵢ ≤ closeᵢ
```

**Soft Window Penalty:**
```
penaltyᵢ = {
    0 if openᵢ ≤ arrival_timeᵢ ≤ closeᵢ
    w × distance_to_window if outside
}
```

**Elapsed Time Constraint:**
```
elapsed_timeᵢⱼ ≥ travel_timeᵢⱼ
elapsed_timeᵢⱼ ≥ min_visitᵢ
elapsed_timeᵢⱼ ≤ max_gap
```

### 2.3 Time Window Interaction

The research literature examines how time windows interact when multiple attractions are included in an itinerary:

**Window Intersection:**
The feasible window for an attraction depends on the cumulative time spent at previous attractions and the travel time to reach the attraction. The feasible window shrinks as the itinerary progresses:

```
feasible_startᵢ = max(openᵢ, arrival_timeᵢ₋₁ + visit_durationᵢ₋₁ + travel_timeᵢ₋₁,ᵢ)
feasible_endᵢ = min(closeᵢ, feasible_startᵢ + max_visitᵢ)
```

**Window Propagation:**
Late arrivals at early attractions propagate forward, reducing the feasible windows for all subsequent attractions. This propagation can render late-stage attractions infeasible, requiring itinerary restructuring.

**Window Reset:**
Some attractions (e.g., overnight stays, meal breaks) reset the time window calculation, establishing new baseline times for subsequent attractions.

---

## 3. Opening Hours Integration

### 3.1 Operating Hours Data

The integration of operating hours requires accurate data collection and representation:

**Data Sources:**
- Official attraction websites
- Tourism board databases
- Google Places API operating hours
- User-contributed data

**Data Representation:**
Operating hours are represented as time ranges associated with specific days:

```
hours = {
    "Monday": [("09:00", "17:00")],
    "Tuesday": [("09:00", "17:00")],
    "Friday": [("09:00", "21:00")],
    "Saturday": [("10:00", "18:00")]
}
```

**Special Schedules:**
Many attractions have special operating hours for holidays, events, or seasons. The data model must accommodate these variations:

```
special_hours = {
    "2024-12-25": None,  # Closed
    "2024-12-31": [("10:00", "16:00")],  # Special hours
}
```

### 3.2 Operating Hours Constraints

Operating hours are typically modeled as hard constraints that cannot be violated:

**Feasibility Check:**
An attraction is feasible for a given time slot if the scheduled visit time falls within the operating hours range. The visit duration must also fit within the remaining operating time:

```
feasible(poi, time, duration) =
    operating_hours[poi][day].contains(time) AND
    operating_hours[poi][day].remaining_time(time) >= duration
```

**Schedule Adjustment:**
When a scheduled visit becomes infeasible due to operating hours, the schedule must be adjusted. Options include:
- Rescheduling the visit to a different time
- Removing the attraction from the itinerary
- Adjusting previous visits to make time

### 3.3 Goa-Specific Operating Hours

The Goa tourism context has specific operating hours patterns:

**Beach Access:**
Beaches are generally accessible 24 hours, but beach shacks and water sports operators follow specific schedules:
- Water sports: 8 AM to 5 PM
- Beach shacks: 11 AM to 11 PM

**Heritage Sites:**
Heritage sites typically follow standard museum hours:
- 9 AM to 5:30 PM
- Some sites close on Mondays

**Spice Plantations:**
Spice plantations typically operate:
- 9 AM to 4 PM for tours
- Advance booking often required

**Markets:**
Local markets have variable hours:
- Anjuna Flea Market: Wednesday and Saturday
- Mapusa Market: Daily, peak 6 AM to 1 PM

---

## 4. Constraint Handling Approaches

### 4.1 Penalty Function Approaches

The research literature identifies multiple penalty function approaches for temporal constraint handling:

**Linear Penalties:**
```
penalty = w × violation_magnitude
```

Linear penalties apply constant penalty per unit of violation. Simple to implement but may not reflect true cost of constraint violation.

**Quadratic Penalties:**
```
penalty = w × violation_magnitude²
```

Quadratic penalties apply increasing penalties for larger violations, strongly discouraging severe constraint violations while allowing minor violations.

**Step Penalties:**
```
penalty = {
    0 if violation < threshold₁
    w₁ if threshold₁ ≤ violation < threshold₂
    w₂ if violation ≥ threshold₂
}
```

Step penalties apply graduated penalties with threshold crossings, providing clear zones of acceptable and unacceptable violation levels.

### 4.2 Repair Approaches

Repair approaches modify infeasible solutions to satisfy constraints:

**Local Search Repair:**
Identify the first constraint violation and apply local search to adjust nearby visits to resolve the violation. May require cascading adjustments for propagation effects.

**Removal and Reinsertion:**
Remove attractions causing constraint violations and reinsert them at feasible positions. Uses the optimization algorithm to find new feasible positions.

**Time Shift:**
Shift all subsequent visits to accommodate a constraint violation. Effective for minor violations but may cause cascading violations.

### 4.3 Constraint Ordering

The research literature examines constraint ordering effects on optimization:

**Hard Constraints First:**
Apply hard constraints first to establish feasible solution space, then optimize for soft constraints. Ensures feasibility but may limit exploration.

**Soft Constraints First:**
Optimize soft constraints first, then apply hard constraint repairs. May find better solutions but requires robust repair mechanisms.

**Integrated Optimization:**
Optimize all constraints simultaneously using weighted penalties. Most flexible approach but requires careful weight calibration.

---

## 5. WanderWise+ Temporal Integration

### 5.1 Fitness Function Integration

The WanderWise+ fitness function integrates temporal constraints through the constraint penalty component:

```python
def calculate_temporal_penalty(
    route: list[str],
    start_time: datetime,
    operating_hours: dict[str, dict[str, tuple[datetime, datetime]]],
    visit_durations: dict[str, int],
) -> float:
    """
    Calculate penalty for temporal constraint violations.
    
    Returns:
        Penalty value (0 if no violations)
    """
    penalty = 0.0
    current_time = start_time
    
    for poi in route:
        duration = visit_durations.get(poi, 60)
        day = current_time.strftime("%A")
        hours = operating_hours.get(poi, {}).get(day)
        
        if hours:
            open_time, close_time = hours
            visit_end = current_time + timedelta(minutes=duration)
            
            if current_time < open_time:
                penalty += 30.0
                current_time = open_time
            
            if visit_end > close_time:
                penalty += 50.0
        
        current_time += timedelta(minutes=duration)
    
    return penalty
```

### 5.2 Operating Hours Data Management

The WanderWise+ operating hours data management includes:

**Data Collection:**
- Daily sync with Google Places API
- Manual curation for attractions with missing API data
- Special schedule monitoring for holidays and events

**Data Storage:**
- PostgreSQL database with dedicated operating hours table
- Caching layer for frequent access
- Version control for schedule changes

**Data Validation:**
- Consistency checking for overlapping or missing hours
- Weekend/holiday pattern verification
- User feedback integration for data quality improvement

### 5.3 Real-Time Schedule Adjustment

The WanderWise+ system supports real-time schedule adjustment based on temporal factors:

**Operating Hours Updates:**
When operating hours change, affected itineraries are flagged for review. The GA can re-optimize affected itineraries with updated constraints.

**Crowd-Based Adjustment:**
High crowd levels may prompt schedule adjustment recommendations, suggesting alternative times or attractions.

**User Preferences:**
Users can specify preferred visiting times for attraction categories, which are integrated as soft constraints in the optimization.

---

## 6. Implementation Considerations

### 6.1 Time Representation

Time representation in WanderWise+ uses Python datetime objects with timezone awareness:

```python
from datetime import datetime, timedelta, timezone

# Use UTC for internal storage
start_time = datetime(2024, 12, 15, 9, 0, 0, tzinfo=timezone.utc)

# Convert to local time for scheduling
local_time = start_time.astimezone(timezone(timedelta(hours=5, minutes=30)))  # IST
```

### 6.2 Schedule Calculation

Schedule calculation follows a forward-pass algorithm:

```python
def calculate_schedule(
    route: list[str],
    start_time: datetime,
    visit_durations: dict[str, int],
    travel_times: dict[tuple[str, str], int],
) -> list[dict]:
    """
    Calculate arrival and departure times for each attraction.
    
    Returns:
        List of visit schedules with times
    """
    schedule = []
    current_time = start_time
    
    for i, poi in enumerate(route):
        if i > 0:
            prev_poi = route[i - 1]
            travel_time = travel_times.get((prev_poi, poi), 30)
            current_time += timedelta(minutes=travel_time)
        
        duration = visit_durations.get(poi, 60)
        
        schedule.append({
            "poi": poi,
            "arrival": current_time,
            "departure": current_time + timedelta(minutes=duration),
            "duration": duration,
        })
        
        current_time += timedelta(minutes=duration)
    
    return schedule
```

### 6.3 Validation and Testing

Temporal constraint validation includes:

**Unit Tests:**
- Operating hours boundary testing
- Schedule calculation edge cases
- Penalty calculation verification

**Integration Tests:**
- End-to-end itinerary generation with temporal constraints
- Real-time update handling
- Multi-day schedule coordination

**Performance Testing:**
- Operating hours lookup latency
- Schedule calculation performance
- Constraint evaluation throughput

---

## 7. Summary

This documentation has reviewed the temporal dimension modeling approaches in tourism optimization research, providing the foundation for temporal constraint handling in WanderWise+. The time window modeling, operating hours integration, and constraint handling approaches from the literature inform the system implementation.

Key findings include the distinction between hard and soft temporal constraints, the importance of accurate operating hours data, and the various penalty and repair approaches for constraint handling. The integration of temporal constraints in the fitness function enables generation of temporally feasible itineraries that respect attraction operating hours while optimizing for user preferences.

---

## 8. References

1. Vansteenwegen, P., & Van Oudheusden, D. (2007). The mobile tourist guide: An OR opportunity. OR Insight, 20(4), 220-232.

2. Cao, L., et al. (2022). The traveling tourist destination problem: Mathematical formulation and solution approaches. Transportation Research Part C, 138, 103628.

3. IEEE Access 2020. "Personalized Itinerary Recommendation with Queuing Time Awareness." IEEE Access, 2020.

4. Archetti, C., et al. (2007). The orienteering problem with time windows. European Journal of Operational Research, 178(3), 751-764.

5. Gunawan, A., et al. (2016). An iterated local search algorithm for the orienteering problem with time windows. European Journal of Operational Research, 247(3), 686-693.
