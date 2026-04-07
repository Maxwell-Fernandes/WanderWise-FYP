#!/usr/bin/env python3
import json
import sys

# Load existing notebook
with open('wanderwise_complete_test.ipynb', 'r') as f:
    nb = json.load(f)

# Track cell count
start_cells = len(nb['cells'])

# Module 3: Clustering
module3_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Module 3: Geographic Clustering (K-Means)\n\n"
            "Group POIs into days using K-Means clustering (K = number of days)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Check if we have enough POIs\nif len(filtered_df) < NUM_DAYS:\n"
            "    raise ValueError(f\"Not enough POIs ({len(filtered_df)}) for {NUM_DAYS} days\")\n\n"
            "# Prepare coordinates\ncoords = filtered_df[['latitude', 'longitude']].values\n\n"
            "# K-Means clustering\nkmeans = KMeans(n_clusters=NUM_DAYS, random_state=42, n_init=10)\n"
            "filtered_df['cluster'] = kmeans.fit_predict(coords)\n"
            "filtered_df['day'] = filtered_df['cluster'] + 1\n\n"
            "print(f\"🗺️  K-Means Clustering Results (K={NUM_DAYS}):\")\n"
            "for day in range(1, NUM_DAYS + 1):\n"
            "    day_pois = filtered_df[filtered_df['day'] == day]\n"
            "    print(f\"   Day {day}: {len(day_pois)} POIs\")\n\n"
            "print(f\"\\n✅ Module 3 complete\")"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Normalize popularity within each cluster\n"
            "for day in range(1, NUM_DAYS + 1):\n"
            "    day_mask = filtered_df['day'] == day\n"
            "    day_data = filtered_df[day_mask]\n"
            "    max_pop = day_data['popularity_score'].max()\n"
            "    if max_pop > 0:\n"
            "        filtered_df.loc[day_mask, 'normalized_popularity'] = (\n"
            "            filtered_df.loc[day_mask, 'popularity_score'] / max_pop\n"
            "        )\n"
            "    else:\n"
            "        filtered_df.loc[day_mask, 'normalized_popularity'] = 0.5\n\n"
            "print('✅ Popularity normalized within clusters')"
        ]
    }
]

nb['cells'].extend(module3_cells)
print(f"Added Module 3 ({len(module3_cells)} cells)", file=sys.stderr)

# Save incremental progress
with open('wanderwise_complete_test.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Total cells: {start_cells} -> {len(nb['cells'])}", file=sys.stderr)
print("Notebook build successful!")
