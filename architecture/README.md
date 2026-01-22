# WanderWise+ Architecture Documentation

This folder contains comprehensive architecture and data flow documentation for the WanderWise+ intelligent tourism recommendation system.

## Contents

| File | Description |
|------|-------------|
| `01_detailed_data_flow.md` | Complete system architecture and data flow diagrams |
| `02_module_integration.md` | Module integration guide with data contracts |

## Quick Links

- **[System Overview](01_detailed_data_flow.md#1-system-overview)**
- **[Module Architecture](01_detailed_data_flow.md#2-module-architecture)**
- **[Detailed Data Flow](01_detailed_data_flow.md#3-detailed-data-flow)**
- **[Database Schema](01_detailed_data_flow.md#4-database-schema)**
- **[API Endpoints](01_detailed_data_flow.md#5-api-endpoints)**
- **[Technology Stack](01_detailed_data_flow.md#6-technology-stack)**
- **[Deployment Architecture](01_detailed_data_flow.md#7-deployment-architecture)**

## Architecture Summary

```
User Input → NLC → Clustering → GA → Output
            ↓        ↓         ↓
         Reviews  K-Means   COX Crossover
         Social   Haversine Tournament Selection
         Temporal WPI       Fitness Evaluation
```

## Related Documentation

- `/AGENTS.md` - Development guide and coding standards
- `/TODO.md` - Project progress tracking
- `/ModuleResearch/` - Research papers and algorithms
