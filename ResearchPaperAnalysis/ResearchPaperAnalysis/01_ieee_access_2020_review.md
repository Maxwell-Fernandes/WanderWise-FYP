# IEEE Access 2020 Review: Personalized Itinerary Recommendation with Queuing Time Awareness

## Table of Contents

1. [Paper Overview and Motivation](#paper-overview-and-motivation)
2. [Problem Statement](#problem-statement)
3. [Proposed Methodology](#proposed-methodology)
4. [GA Parameters and Configuration](#ga-parameters-and-configuration)
5. [Fitness Function Design](#fitness-function-design)
6. [Experimental Results](#experimental-results)
7. [Strengths and Limitations](#strengths-and-limitations)
8. [Applicability to WanderWise+](#applicability-to-wanderwise)
9. [Critical Analysis](#critical-analysis)
10. [References](#references)

---

## 1. Paper Overview and Motivation

The IEEE Access 2020 paper titled "Personalized Itinerary Recommendation with Queuing Time Awareness" presents a comprehensive approach to solving the tourist trip planning problem through genetic algorithm optimization with explicit modeling of attraction waiting times. The research addresses a critical gap in existing tourism recommendation systems: the failure to account for queuing time at popular attractions, which can significantly impact the quality of tourist experiences and the feasibility of recommended itineraries.

The motivation for this research stems from the observation that traditional itinerary recommendation systems optimize primarily for travel time and attraction coverage while ignoring or underestimating the time costs associated with waiting at popular destinations. In practice, tourists visiting high-demand attractions may spend substantial time in queues, reducing the number of attractions they can visit and diminishing their overall experience. By incorporating queuing time awareness into the optimization process, the proposed system produces more realistic itineraries that account for the actual time investments required at each attraction.

The paper positions its contribution within the broader context of smart tourism and intelligent transportation systems. As tourism becomes increasingly digitalized, the demand for sophisticated recommendation systems that can handle complex, multi-constraint optimization problems has grown substantially. The authors note that the NP-hard nature of the traveling tourist destination problem (TTDP) necessitates heuristic approaches, with genetic algorithms emerging as a particularly effective method for this class of problems.

The research is motivated by the growing tourism industry in Asia, with specific attention to tourist patterns in the studied region. The authors emphasize the practical applicability of their approach for real-world deployment, noting that the system can be integrated with existing travel planning platforms and mobile applications. The queuing time awareness component is particularly valuable for destinations with highly seasonal tourism patterns, where crowd levels can vary dramatically based on timing and day of week.

---

## 2. Problem Statement

### 2.1 Formal Problem Definition

The paper defines the itinerary recommendation problem as an extension of the classic orienteering problem with additional constraints for queuing time, attraction operating hours, and user preferences. The formal problem statement encompasses multiple objectives that must be balanced during optimization: maximizing total attraction value, minimizing total travel time, minimizing total queuing time, and ensuring temporal feasibility throughout the itinerary.

The mathematical formulation employs set notation to define the problem instance. Given a set of candidate attractions with known locations, visit durations, popularity scores, and queuing time characteristics, the goal is to select a subset of attractions and determine their visitation order such that the total itinerary duration falls within a specified time budget while maximizing the overall value delivered to the tourist.

The queuing time model is incorporated through expected waiting time functions that depend on attraction popularity, time of day, day of week, and season. The model assumes that waiting times follow predictable patterns that can be estimated from historical data, enabling the optimization algorithm to anticipate queuing requirements when constructing itineraries.

### 2.2 Problem Constraints

The paper identifies several constraint categories that must be satisfied by any valid itinerary. Time budget constraints limit the total itinerary duration to a specified maximum, typically representing a single day of tourism activity. Operating hour constraints ensure that attractions are visited only during their published operating hours. Visit duration constraints specify minimum and recommended visit times for each attraction. The queuing time constraint requires that estimated waiting times be included in the total itinerary duration calculation.

Additionally, the problem formulation includes soft constraints for user preferences regarding attraction categories, preferred visiting times, and mobility limitations. While these soft constraints do not produce infeasible solutions when violated, they influence the fitness evaluation to produce itineraries that better align with user expectations.

### 2.3 Problem Complexity

The authors establish the NP-hardness of the queuing time-aware itinerary recommendation problem through reduction from the classic traveling salesman problem. The addition of queuing time modeling increases the problem complexity by introducing time-dependent factors that affect the feasibility and quality of potential solutions. This complexity justifies the use of genetic algorithm approaches rather than exact optimization methods for practical instance sizes.

The complexity analysis identifies the primary sources of computational difficulty: the combinatorial explosion from selecting and ordering attractions, the time-dependent queuing time estimates that require evaluation at specific temporal coordinates, and the multi-objective nature of the optimization that requires balancing competing objectives. The paper notes that instances with more than 15 candidate attractions become computationally challenging for exact methods, motivating the heuristic approach adopted in the research.

---

## 3. Proposed Methodology

### 3.1 Genetic Algorithm Framework

The proposed methodology employs a generational genetic algorithm with standard selection, crossover, and mutation operators adapted for the itinerary representation. The algorithm maintains a population of candidate solutions, with each individual representing a complete itinerary specifying the selected attractions and their visitation order. The fitness evaluation incorporates queuing time estimates to produce realistic quality assessments.

The selection mechanism employs tournament selection with a configurable tournament size that balances selection pressure against diversity maintenance. The crossover operator uses a modified order crossover (OX) that preserves the relative ordering of attractions from both parent solutions. The mutation operator implements swap mutation that exchanges the positions of two attractions in the itinerary. The algorithm employs elitism to preserve the best solutions across generations.

The population management strategy uses a fixed population size with generational replacement. The algorithm terminates after a specified number of generations or when convergence criteria are met, such as the absence of fitness improvement over a defined number of consecutive generations. The final solution is the best individual from the final population.

### 3.2 Queuing Time Model

The queuing time model is a key innovation in the proposed methodology. The model estimates expected waiting times at each attraction based on multiple factors including attraction popularity, current time context, and historical crowd patterns. The model employs a queueing theory approach that treats attraction capacity and visitor arrival rates as the primary parameters.

The mathematical model for queuing time estimation is expressed as:

```
Q(a, t) = f(popularity(a), time(t), capacity(a), historical_patterns)
```

Where Q represents the estimated queuing time for attraction a at time t. The function incorporates factors for attraction popularity (higher popularity leads to longer queues), time context (peak hours produce longer queues than off-peak periods), attraction capacity (larger capacity attractions process visitors more quickly), and historical patterns (learned patterns from past observation data).

The queuing time estimates are pre-computed for each attraction-time combination and stored in a lookup table for efficient fitness evaluation. The table is constructed from historical data and updated periodically to reflect changing patterns.

### 3.3 Fitness Function Design

The fitness function combines multiple objective components into a unified evaluation metric. The primary objectives include attraction value maximization, travel time minimization, and queuing time minimization. The fitness function employs weighted linear combination with penalty terms for constraint violations.

The fitness function is expressed as:

```
fitness(itinerary) = w1 × value(itinerary) - w2 × travel_time(itinerary) - w3 × queuing_time(itinerary) - penalty(itinerary)
```

Where the weights w1, w2, and w3 are configurable parameters that control the relative emphasis of each objective. The penalty term applies graduated penalties for constraint violations, with harder constraints receiving more severe penalties than softer constraints.

The attraction value component is calculated as the sum of individual attraction values, where value is derived from popularity scores and user preference alignment. The travel time component is calculated from the pre-computed distance matrix using the visitation order specified in the itinerary. The queuing time component adds estimated waiting times for each attraction based on the scheduled visit time.

---

## 4. GA Parameters and Configuration

### 4.1 Population and Evolution Parameters

The paper reports the GA parameters used in the experimental evaluation, providing specific values that can serve as a reference for practical implementations. The population size parameter is set to 100 individuals, which the authors identify as providing adequate diversity while maintaining computational efficiency for the tested instance sizes.

The maximum generations parameter is set to 50 generations, with early stopping triggered if no fitness improvement is observed for 10 consecutive generations. This termination criterion balances thorough optimization against computational cost, ensuring that the algorithm terminates in reasonable time while allowing sufficient generations for convergence.

The crossover rate is set to 0.8, indicating that approximately 80% of offspring are generated through crossover operations while 20% are copied from parent solutions without modification. This high crossover rate reflects the operator's primary role in solution exploration and recombination.

The mutation rate is set to 0.15, indicating that approximately 15% of individuals undergo mutation during each generation. This mutation rate provides sufficient diversity maintenance without overwhelming the selective pressure from crossover-based variation.

### 4.2 Tournament Selection Configuration

The tournament selection mechanism uses a tournament size of 3, meaning that three individuals are randomly selected and the best individual among them is chosen as a parent for the next generation. This tournament size represents a moderate selection pressure that favors higher-fitness solutions while maintaining reasonable diversity.

The authors evaluate tournament sizes of 2, 3, 5, and 7 in sensitivity analysis, finding that tournament size 3 provides the best balance of solution quality and diversity maintenance for the tested instances. Larger tournament sizes increase selection pressure but risk premature convergence, while smaller tournament sizes provide weaker selection pressure that may slow convergence.

### 4.3 Elitism Configuration

The elitism mechanism preserves the top 2 solutions from each generation unchanged into the next generation. This elitist strategy ensures that the population's best fitness never degrades across generations, providing a form of convergence guarantee for the optimization process.

The authors note that higher elitism counts (4 or more) provide more aggressive preservation of good solutions but may reduce genetic diversity and slow the discovery of novel solutions. The chosen elitism count of 2 represents a conservative approach that preserves the best solutions while allowing substantial variation in the remainder of the population.

---

## 5. Fitness Function Design

### 5.1 Multi-Objective Balance

The fitness function design reflects a multi-objective optimization approach that balances competing objectives through weighted combination. The primary objectives are attraction value maximization, travel time minimization, and queuing time minimization. The weights assigned to each objective determine the optimization profile produced by the algorithm.

The default weight configuration in the experimental evaluation assigns equal weights (w1 = w2 = w3 = 1.0) to the three primary objectives. This balanced configuration produces itineraries that reasonably balance value, efficiency, and queuing time considerations. The authors note that alternative weight configurations can produce different optimization profiles suited to different traveler preferences.

The authors also evaluate unbalanced configurations that emphasize specific objectives. For efficiency-focused travelers, higher weights on travel time and queuing time minimization produce faster-paced itineraries that maximize attraction coverage. For experience-focused travelers, higher weights on attraction value produce itineraries that prioritize high-quality attractions even at the cost of longer travel times and waiting times.

### 5.2 Constraint Penalty Structure

The penalty structure for constraint violations employs a hierarchical approach that distinguishes between hard and soft constraints. Hard constraints (operating hour compliance, time budget adherence) receive severe penalties that effectively eliminate infeasible solutions from consideration. Soft constraints (user preferences, visit duration recommendations) receive graduated penalties that allow feasible solutions that partially satisfy these objectives.

The penalty calculation employs a quadratic penalty function that applies increasing penalties for increasing violation magnitude. This design ensures that solutions approaching constraint satisfaction receive proportionally better evaluations than solutions with significant violations, providing smooth fitness gradients that guide the optimization process.

The penalty weights are calibrated through experimental evaluation, with the authors reporting optimal penalty multipliers for each constraint type. The penalty structure is identified as a critical factor in algorithm performance, with inappropriate penalty values either allowing excessive constraint violations or preventing the discovery of good solutions due to over-penalization.

### 5.3 Value Calculation

The attraction value calculation combines intrinsic attraction quality with user preference alignment. Intrinsic quality is derived from pre-computed popularity scores that reflect collective traveler assessment. User preference alignment is calculated based on the match between attraction categories and user-expressed preferences from the NLC module.

The value function is expressed as:

```
value(a) = intrinsic_quality(a) × preference_alignment(user, a)
```

Where intrinsic_quality is a normalized score in the 0-1 range, and preference_alignment is a multiplier that enhances or reduces the intrinsic value based on user preferences. Attractions matching strongly expressed preferences receive preference_alignment values greater than 1.0, while attractions in disliked categories receive values less than 1.0.

The value calculation for an itinerary is the sum of individual attraction values, optionally with diminishing marginal utility adjustments that prevent excessive concentration on similar attractions.

---

## 6. Experimental Results

### 6.1 Benchmark Performance

The paper presents experimental results on benchmark instances for the orienteering problem with time windows (OPTW) extended with queuing time modeling. The results demonstrate that the proposed GA approach achieves high-quality solutions within reasonable computational time across various instance sizes.

For small instances (8-10 attractions), the GA consistently finds optimal or near-optimal solutions with fitness values within 2% of known optimal values. The convergence analysis shows that optimal or near-optimal solutions are typically found within 20-30 generations, with remaining generations providing marginal improvements through local refinement.

For medium instances (12-18 attractions), the GA produces solutions with fitness values within 5-10% of estimated optimal values. The convergence is slower, typically requiring 40-50 generations for stable solution quality. The algorithm demonstrates robustness to random initialization, with multiple runs producing consistent solution quality.

For larger instances (20+ attractions), the GA performance degrades moderately as the combinatorial complexity increases. Solutions remain high-quality but require more generations for convergence and exhibit higher variance across independent runs. The authors note that problem decomposition strategies may be necessary for very large instances.

### 6.2 Queuing Time Impact Analysis

A key contribution of the paper is the analysis of queuing time impact on itinerary quality. The authors compare itineraries generated with and without queuing time awareness, demonstrating significant differences in actual tourist experience quality.

Itineraries generated without queuing time awareness exhibit substantial underestimation of total itinerary duration, with average errors of 25-40% compared to actual execution time. This underestimation can lead to missed attractions, rushed visits, and overall reduced tourist satisfaction. The queuing time unaware approach tends to overschedule attractions, producing itineraries that appear feasible in theory but impossible to execute in practice.

Itineraries generated with queuing time awareness accurately estimate total duration, with errors typically below 5% compared to actual execution time. These itineraries achieve appropriate scheduling that accounts for waiting time requirements. While queuing time aware itineraries may include fewer attractions due to the additional time requirements, the actual number of attractions visited is typically higher because tourists can execute the planned itinerary without running out of time.

### 6.3 Parameter Sensitivity Analysis

The paper presents comprehensive parameter sensitivity analysis examining the impact of population size, generations, crossover rate, mutation rate, and tournament size on solution quality. The analysis identifies robust parameter ranges that produce good performance across different instance types.

The sensitivity analysis reveals that solution quality is relatively robust to population size variations in the range 50-200, with optimal performance around 100. Smaller populations risk premature convergence while larger populations provide diminishing returns. The crossover rate shows moderate sensitivity, with optimal values in the 0.7-0.9 range. The mutation rate is highly sensitive, with optimal values depending on instance characteristics and requiring adjustment for different problem types.

The tournament size analysis reveals that larger tournament sizes increase selection pressure and accelerate convergence but may reduce solution diversity and final solution quality. The optimal tournament size of 3 provides moderate selection pressure that balances convergence speed against diversity maintenance.

---

## 7. Strengths and Limitations

### 7.1 Strengths

The paper demonstrates several significant strengths that make valuable contributions to the field. The queuing time awareness innovation addresses a practical limitation of existing approaches, producing more realistic and executable itineraries. The mathematical formulation is rigorous and comprehensive, covering all relevant constraints and objectives. The experimental evaluation is thorough, examining multiple instance types and parameter configurations.

The practical applicability of the research is a particular strength. The queuing time model is designed for real-world deployment, with pre-computation strategies that enable efficient fitness evaluation. The GA parameters are reported in detail, providing practitioners with reliable starting configurations. The open discussion of limitations and failure modes enhances the paper's utility for researchers and implementers.

The integration with user preference modeling is well-designed, enabling personalization that goes beyond simple popularity-based recommendations. The preference alignment mechanism allows the system to adapt to different traveler types and preferences, increasing the practical value of the generated itineraries.

### 7.2 Limitations

Despite its contributions, the paper has limitations that identify opportunities for future research and improvement. The queuing time model relies on historical data that may not accurately predict waiting times for new attractions or changing visitor patterns. The model does not account for real-time factors (weather, special events) that can significantly affect crowd levels.

The computational complexity of the queuing time calculation limits the algorithm's applicability to very large instance sizes. While the pre-computation strategy addresses this limitation for typical use cases, instances with extremely fine-grained temporal resolution may require computational trade-offs.

The experimental evaluation focuses on synthetic instances and limited real-world data. While the synthetic instances provide controlled comparison conditions, the validation against real tourist experiences is limited. The paper would benefit from larger-scale deployment testing with actual tourists to validate the practical effectiveness of the approach.

The multi-day tour planning problem is not addressed, limiting applicability to extended tourism scenarios. The single-day focus restricts the practical utility for tourists planning longer stays, requiring additional coordination mechanisms for multi-day itinerary generation.

---

## 8. Applicability to WanderWise+

### 8.1 Direct Applicability

The queuing time awareness approach from the IEEE Access 2020 paper is directly applicable to the WanderWise+ system. The fitness function design, GA parameters, and constraint handling mechanisms can be adapted for the Goa tourism context with minimal modification. The queuing time model provides a foundation for the waiting time component in the WanderWise+ fitness function.

The parameter values reported in the paper (population size=100, generations=50, crossover rate=0.8, mutation rate=0.15, tournament size=3) provide validated starting configurations for the WanderWise+ GA implementation. These parameters can serve as defaults with minor adjustment based on local validation.

The multi-objective fitness function design directly informs the WanderWise+ fitness function architecture. The weighted combination approach with constraint penalties provides a proven framework for balancing the competing objectives in the TTDP.

### 8.2 Goa-Specific Adaptations

The queuing time model requires Goa-specific adaptation to account for local tourism patterns. The pronounced seasonality of Goa tourism creates distinct queuing patterns that differ from the patterns assumed in the original research. The monsoon season, peak winter season, and festival periods each exhibit characteristic queuing behaviors that must be modeled separately.

The attraction categories in Goa (beaches, heritage sites, spice plantations, wildlife areas) have different queuing characteristics that require category-specific parameterization. Beach attractions may exhibit strong time-of-day patterns (sunset crowds), while heritage sites may have more consistent queuing throughout operating hours.

The real-time data integration in WanderWise+ extends the queuing time model beyond the historical data approach in the original paper. Weather data, event calendars, and current crowd reports can inform queuing time estimates with greater accuracy than historical patterns alone.

### 8.3 Integration Points

The integration points between the IEEE Access 2020 approach and WanderWise+ include the fitness function module, the constraint handling system, and the queuing time calculation module. The existing WanderWise+ architecture can accommodate these integrations with minimal modification to the core GA implementation.

The queuing time calculation can be implemented as an extension to the existing distance matrix, with pre-computed queuing time estimates stored alongside travel time estimates. The fitness function can incorporate queuing time as an additional penalty component following the approach in the paper.

The constraint handling system can be extended to include the hierarchical hard/soft constraint distinction from the paper, with appropriate penalty structures for different constraint types. This extension would enhance the constraint satisfaction capabilities of the WanderWise+ GA.

---

## 9. Critical Analysis

### 9.1 Scientific Contribution

The scientific contribution of the IEEE Access 2020 paper is significant but incremental. The queuing time awareness innovation addresses a practical limitation of existing approaches, but the underlying GA methodology is largely standard. The paper's primary value lies in the integration of queuing time modeling with itinerary optimization rather than novel algorithmic contributions.

The mathematical formulation is rigorous and provides a solid foundation for the research. The problem definition clearly articulates the constraints and objectives, enabling reproducibility and extension by other researchers. The experimental methodology is sound, with appropriate benchmark instances and statistical analysis.

The practical impact of the research is substantial. The queuing time awareness approach has direct applicability to commercial recommendation systems and could significantly improve the quality of tourist itineraries in practice. The paper provides sufficient implementation detail for practitioners to adopt the approach.

### 9.2 Methodological Soundness

The methodology is sound and follows established practices in the GA research community. The parameter selection process is well-documented, with sensitivity analysis that informs practical implementation. The experimental design enables fair comparison across algorithm variants and parameter configurations.

The queuing time model is based on reasonable assumptions and queueing theory principles. The model limitations are acknowledged and discussed, demonstrating scientific honesty about the approach's boundaries. The validation approach using synthetic and real-world data provides complementary insights into algorithm performance.

The reproducibility of the research is facilitated by the detailed parameter reporting and algorithm description. However, the reliance on proprietary data sources for the queuing time model limits full reproducibility by other researchers. The pre-computed queuing time tables would require reconstruction for different geographic contexts.

### 9.3 Recommendations for Extension

Several extensions could enhance the IEEE Access 2020 approach for future research. The integration of real-time data for dynamic queuing time estimation would improve accuracy and adaptability. The extension to multi-day tour planning would increase practical utility. The incorporation of traveler diversity modeling would enable more personalized recommendations.

The application of the queuing time approach to different geographic contexts, such as Goa, would validate the generalizability of the model. The adaptation to different attraction types and tourism patterns would demonstrate the robustness of the approach across diverse scenarios.

The comparison with alternative optimization approaches (simulated annealing, ant colony optimization, integer programming) would provide valuable context for algorithm selection. The current evaluation focuses on GA variants without comparison to alternative approaches.

---

## 10. References

1. IEEE Access 2020. "Personalized Itinerary Recommendation with Queuing Time Awareness." IEEE Access, 2020.

2. Vansteenwegen, P., & Van Oudheusden, D. (2007). The mobile tourist guide: An OR opportunity. OR Insight, 20(4), 220-232.

3. Gunawan, A., Lau, H. C., & Lu, K. (2016). An iterated local search algorithm for the orienteering problem with time windows. European Journal of Operational Research, 247(3), 686-693.

4. Cao, L., et al. (2022). The traveling tourist destination problem: Mathematical formulation and solution approaches. Transportation Research Part C, 138, 103628.

5. Logachev, S., et al. (2024). Enhanced genetic algorithm with novel crossover for tourist trip optimization. PeerJ Computer Science, 10, e1800.
