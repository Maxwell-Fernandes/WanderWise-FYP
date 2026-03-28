# NLC Dataset Augmentation Plan

## Objective
Improve the NLC model accuracy from 90.7% to 92%+ by adding authentic, human-like training data that handles:
- Real-world use cases
- Edge cases
- Underrepresented categories (adventure, nature)
- Conversational inputs
- Mixed-language inputs (Hinglish)

---

## Current Performance Gaps

| Category | Current F1 | Target F1 | Gap |
|----------|------------|-----------|-----|
| adventure | 86.7% | 92%+ | -5.3% |
| nature | 86.7% | 92%+ | -5.3% |
| food | 90.2% | 93%+ | -2.8% |
| nightlife | 89.7% | 93%+ | -3.3% |

---

## Augmentation Strategy

### 1. Adventure Category Enhancement (100 samples)

#### Missing Activities Vocabulary
Current gaps in adventure vocabulary:
- Zip lining / Zipline
- Rock climbing
- Cliff diving
- Bungee jumping
- ATV rides
- Dirt biking
- Paragliding
- Microlight flying
- Kayaking (limited)
- Windsurfing (limited)

#### Sample Data to Add

```csv
# Extreme Sports
"want to try zip lining in goa",0,0,1,0,0,0,0
"zip lining adventure",0,0,1,0,0,0,0
"zipline near goa",0,0,1,0,0,0,0
"rock climbing spots in goa",0,0,1,0,0,0,0
"indoor rock climbing goa",0,0,1,0,0,0,0
"cliff diving near goa",0,0,1,0,0,0,0
"cliff jumping goa",0,0,1,0,0,0,0
"bungee jumping in goa",0,0,1,0,0,0,0
"bungee jumping adventure",0,0,1,0,0,0,0
"ATV rides in goa",0,0,1,0,0,0,0
"ATV tour goa",0,0,1,0,0,0,0
"all terrain vehicle goa",0,0,1,0,0,0,0
"dirt biking goa",0,0,1,0,0,0,0
"dirt bike rental goa",0,0,1,0,0,0,0
"paragliding in goa",0,0,1,0,0,0,0
"paragliding adventure",0,0,1,0,0,0,0
"microlight flying goa",0,0,1,0,0,0,0
"microlight flight goa",0,0,1,0,0,0,0

# Water Sports Expansion
"kayaking tours goa",0,0,1,0,0,0,0
"kayak rental goa",0,0,1,0,0,0,0
"windsurfing lessons goa",0,0,1,0,0,0,0
"windsurfing spots goa",0,0,1,0,0,0,0
"kitesurfing in goa",0,0,1,0,0,0,0
"kitesurfing lessons",0,0,1,0,0,0,0
"jet ski rental goa",0,0,1,0,0,0,0
"jet skiing experience",0,0,1,0,0,0,0
"water skiing goa",0,0,1,0,0,0,0
"wakeboarding goa",0,0,1,0,0,0,0
"flyboarding in goa",0,0,1,0,0,0,0
"flyboarding experience",0,0,1,0,0,0,0
"banana boat ride goa",0,0,1,0,0,0,0
"banana boat experience",0,0,1,0,0,0,0

# Diving & Snorkeling
"scuba diving packages goa",0,0,1,0,0,0,0
"scuba diving for beginners",0,0,1,0,0,0,0
"scuba certification goa",0,0,1,0,0,0,0
"snorkeling spots goa",0,0,1,0,0,0,0
"snorkeling tour goa",0,0,1,0,0,0,0
"deep sea diving goa",0,0,1,0,0,0,0
"underwater diving goa",0,0,1,0,0,0,0

# Adventure Tours
"adventure tour packages goa",0,0,1,0,0,0,0
"adventure sports goa",0,0,1,0,0,0,0
"extreme sports goa",0,0,1,0,0,0,0
"adventure activities near me",0,0,1,0,0,0,0
"thrill activities goa",0,0,1,0,0,0,0
"adrenaline activities goa",0,0,1,0,0,0,0
"action packed day goa",0,0,1,0,0,0,0

# Trekking & Hiking
"trekking in goa",0,0,1,0,0,0,0
"trekking trails goa",0,0,1,0,0,0,0
"hiking trails goa",0,0,1,0,0,0,0
"jungle trek goa",0,0,1,0,0,0,0
"forest trekking goa",0,0,1,0,0,0,0
"hill trekking goa",0,0,1,0,0,0,0

# Dolphin & Boat Tours
"dolphin spotting goa",0,0,1,0,0,0,0
"dolphin safari goa",0,0,1,0,0,0,0
"dolphin watching tour",0,0,1,0,0,0,0
"boat safari goa",0,0,1,0,0,0,0
"speed boat ride goa",0,0,1,0,0,0,0
"catamaran cruise goa",0,0,1,0,0,0,0

# Multi-label Adventure
"adventure and beach day",1,0,1,0,0,0,0
"trekking and wildlife",0,0,1,1,0,0,0
"scuba and beach relaxation",1,0,1,0,0,0,0
"adventure sports and nightlife",0,0,1,0,0,1,0
"kayaking and nature trails",0,0,1,1,0,0,0
```

### 2. Nature Category Enhancement (100 samples)

#### Missing Vocabulary
Current gaps in nature vocabulary:
- Mangrove tours
- Biodiversity
- Endemic species
- Eco-tourism
- Bird watching (limited)
- Butterfly watching
- Spice plantations (limited)
- Waterfalls (limited)

#### Sample Data to Add

```csv
# Mangrove & Wetlands
"mangrove tour goa",0,0,0,1,0,0,0
"mangrove safari goa",0,0,0,1,0,0,0
"mangrove ecosystem goa",0,0,0,1,0,0,0
"backwater cruise goa",0,0,0,1,0,0,0
"wetland tour goa",0,0,0,1,0,0,0

# Biodiversity & Wildlife
"biodiversity hotspot goa",0,0,0,1,0,0,0
"endemic species goa",0,0,0,1,0,0,0
"wildlife photography goa",0,0,0,1,0,0,0
"wildlife sanctuary goa",0,0,0,1,0,0,0
"animal spotting goa",0,0,0,1,0,0,0
"fauna of goa",0,0,0,1,0,0,0
"flora of goa",0,0,0,1,0,0,0

# Bird Watching
"bird watching goa",0,0,0,1,0,0,0
"bird watching tour goa",0,0,0,1,0,0,0
"bird sanctuary goa",0,0,0,1,0,0,0
"migratory birds goa",0,0,0,1,0,0,0
"bird photography goa",0,0,0,1,0,0,0
"salim ali bird sanctuary",0,0,0,1,0,0,0

# Butterfly & Insects
"butterfly watching goa",0,0,0,1,0,0,0
"butterfly conservatory goa",0,0,0,1,0,0,0
"insect photography goa",0,0,0,1,0,0,0

# Spice Plantations
"spice plantation tour goa",0,0,0,1,0,0,0
"spice farm visit goa",0,0,0,1,0,0,0
"spice garden goa",0,0,0,1,0,0,0
"organic farm tour goa",0,0,0,1,0,0,0
"plantation walk goa",0,0,0,1,0,0,0
"sahakari spice farm",0,0,0,1,0,0,0
"savoi spice plantation",0,0,0,1,0,0,0

# Waterfalls
"waterfall trek goa",0,0,0,1,0,0,0
"waterfall visit goa",0,0,0,1,0,0,0
"dudhsagar falls trek",0,0,0,1,0,0,0
"dudhsagar waterfall",0,0,0,1,0,0,0
"harvalem waterfall",0,0,0,1,0,0,0
"netravali waterfall",0,0,0,1,0,0,0
"kuskem waterfall",0,0,0,1,0,0,0

# Nature Trails & Walks
"nature trail goa",0,0,0,1,0,0,0
"nature walk goa",0,0,0,1,0,0,0
"eco trail goa",0,0,0,1,0,0,0
"forest walk goa",0,0,0,1,0,0,0
"jungle walk goa",0,0,0,1,0,0,0
"nature photography goa",0,0,0,1,0,0,0

# Eco-Tourism
"eco tourism goa",0,0,0,1,0,0,0
"eco tour goa",0,0,0,1,0,0,0
"sustainable tourism goa",0,0,0,1,0,0,0
"green tourism goa",0,0,0,1,0,0,0
"eco friendly activities goa",0,0,0,1,0,0,0

# Scenic Viewpoints
"scenic viewpoint goa",0,0,0,1,0,0,0
"panoramic view goa",0,0,0,1,0,0,0
"sunset point goa",0,0,0,1,0,0,0
"sunrise point goa",0,0,0,1,0,0,0
"viewpoint trek goa",0,0,0,1,0,0,0

# Nature + Food Multi-label
"spice plantation and lunch",0,0,0,1,1,0,0
"nature walk and local food",0,0,0,1,1,0,0
"waterfall trek and picnic",0,0,0,1,1,0,0
"bird watching and breakfast",0,0,0,1,1,0,0

# Nature + Adventure Multi-label
"trekking and wildlife safari",0,0,1,1,0,0,0
"kayaking and bird watching",0,0,1,1,0,0,0
"jungle trek and waterfall",0,0,1,1,0,0,0
```

### 3. Edge Cases (80 samples)

#### Negative Queries
```csv
"no beaches please just food",0,0,0,0,1,0,0
"i dont want beaches",0,0,0,0,0,0,0
"not interested in nightlife",0,0,0,0,0,0,0
"no adventure activities",0,0,0,0,0,0,0
"skip the beaches",0,0,0,0,0,0,0
"avoid crowded beaches",0,0,0,0,0,0,0
"no water sports please",0,0,0,0,0,0,0
"not into partying",0,0,0,0,0,0,0
"no shopping for me",0,0,0,0,0,0,0
"skip historical sites",0,0,0,0,0,0,0
"definitely no beaches",0,0,0,0,0,0,0
"rather not do adventure",0,0,0,0,0,0,0
```

#### Abbreviations & Slang
```csv
"bch day",1,0,0,0,0,0,0
"bches in goa",1,0,0,0,0,0,0
"nlyt spots",0,0,0,0,0,1,0
"nlyfe goa",0,0,0,0,0,1,0
"fd places",0,0,0,0,1,0,0
"shppg in goa",0,0,0,0,0,0,1
"adv activities",0,0,1,0,0,0,0
"hist places",0,1,0,0,0,0,0
"nat trails",0,0,0,1,0,0,0
"beach vibes only",1,0,0,0,0,0,0
"foodie life",0,0,0,0,1,0,0
"party hard",0,0,0,0,0,1,0
"shop till drop",0,0,0,0,0,0,1
"adventure time",0,0,1,0,0,0,0
"nature calls",0,0,0,1,0,0,0
"history buff",0,1,0,0,0,0,0
```

#### Typos & Misspellings
```csv
"beches in goa",1,0,0,0,0,0,0
"bech activites",1,0,0,0,0,0,0
"resturant goa",0,0,0,0,1,0,0
"resturants in goa",0,0,0,0,1,0,0
"nighlife goa",0,0,0,0,0,1,0
"nightlie spots",0,0,0,0,0,1,0
"shoping goa",0,0,0,0,0,0,1
"advenure sports",0,0,1,0,0,0,0
"adventur activities",0,0,1,0,0,0,0
"histroy places",0,1,0,0,0,0,0
"historical sited",0,1,0,0,0,0,0
"natur trails",0,0,0,1,0,0,0
"wildlfe sanctuary",0,0,0,1,0,0,0
"scubba diving",0,0,1,0,0,0,0
"snorkelling goa",0,0,1,0,0,0,0
"watrfall goa",0,0,0,1,0,0,0
```

#### Incomplete Sentences
```csv
"beach...",1,0,0,0,0,0,0
"food??",0,0,0,0,1,0,0
"nightlife??",0,0,0,0,0,1,0
"shopping...",0,0,0,0,0,0,1
"adventure??",0,0,1,0,0,0,0
"nature...",0,0,0,1,0,0,0
"historical??",0,1,0,0,0,0,0
"just beach",1,0,0,0,0,0,0
"want food",0,0,0,0,1,0,0
"need party",0,0,0,0,0,1,0
"looking shops",0,0,0,0,0,0,1
"seeking adventure",0,0,1,0,0,0,0
"craving nature",0,0,0,1,0,0,0
"want history",0,1,0,0,0,0,0
```

#### Vague Queries
```csv
"something fun",0,0,0,0,0,0,0
"anything interesting",0,0,0,0,0,0,0
"what to do",0,0,0,0,0,0,0
"recommend something",0,0,0,0,0,0,0
"suggest places",0,0,0,0,0,0,0
"best of goa",0,0,0,0,0,0,0
"must visit",0,0,0,0,0,0,0
"top attractions",0,0,0,0,0,0,0
"popular spots",0,0,0,0,0,0,0
"famous places",0,0,0,0,0,0,0
```

### 4. Real-World Conversational Inputs (100 samples)

#### Casual/Informal Style
```csv
"wanna hit the beach",1,0,0,0,0,0,0
"gonna check out beaches",1,0,0,0,0,0,0
"thinking of beach today",1,0,0,0,0,0,0
"lets go beach",1,0,0,0,0,0,0
"beach sounds good",1,0,0,0,0,0,0
"up for some beach time",1,0,0,0,0,0,0
"feeling like beach vibes",1,0,0,0,0,0,0
"could go for beach",1,0,0,0,0,0,0
"beach would be nice",1,0,0,0,0,0,0
"in the mood for beach",1,0,0,0,0,0,0

"need some food asap",0,0,0,0,1,0,0
"craving goan food",0,0,0,0,1,0,0
"hungry for seafood",0,0,0,0,1,0,0
"want to eat something good",0,0,0,0,1,0,0
"looking for tasty food",0,0,0,0,1,0,0
"food sounds amazing",0,0,0,0,1,0,0
"down for some food",0,0,0,0,1,0,0
"lets grab some food",0,0,0,0,1,0,0
"food hunting",0,0,0,0,1,0,0
"food trip goa",0,0,0,0,1,0,0

"party tonight anyone",0,0,0,0,0,1,0
"clubbing tonight",0,0,0,0,0,1,0
"night out goa",0,0,0,0,0,1,0
"party scene goa",0,0,0,0,0,1,0
"lets party",0,0,0,0,0,1,0
"nightlife calling",0,0,0,0,0,1,0
"up for partying",0,0,0,0,0,1,0
"club hopping tonight",0,0,0,0,0,1,0
"party time goa",0,0,0,0,0,1,0
"night vibes goa",0,0,0,0,0,1,0

"shopping spree anyone",0,0,0,0,0,0,1
"lets go shopping",0,0,0,0,0,0,1
"market hopping goa",0,0,0,0,0,0,1
"shopping therapy",0,0,0,0,0,0,1
"retail therapy goa",0,0,0,0,0,0,1
"bargain hunting time",0,0,0,0,0,0,1
"market exploration",0,0,0,0,0,0,1
"shopping day goa",0,0,0,0,0,0,1
"buy souvenirs",0,0,0,0,0,0,1
"gift shopping goa",0,0,0,0,0,0,1

"adventure anyone",0,0,1,0,0,0,0
"up for adventure",0,0,1,0,0,0,0
"thrill seeking goa",0,0,1,0,0,0,0
"adventure day goa",0,0,1,0,0,0,0
"action day goa",0,0,1,0,0,0,0
"extreme sports anyone",0,0,1,0,0,0,0
"adrenaline rush goa",0,0,1,0,0,0,0
"lets do something adventurous",0,0,1,0,0,0,0
"adventure calling",0,0,1,0,0,0,0
"thrill time goa",0,0,1,0,0,0,0

"nature walk anyone",0,0,0,1,0,0,0
"peaceful nature day",0,0,0,1,0,0,0
"nature vibes goa",0,0,0,1,0,0,0
"greenery therapy",0,0,0,1,0,0,0
"nature escape goa",0,0,0,1,0,0,0
"wildlife day goa",0,0,0,1,0,0,0
"nature lover here",0,0,0,1,0,0,0
"outdoor day goa",0,0,0,1,0,0,0
"nature time goa",0,0,0,1,0,0,0
"peaceful day in nature",0,0,0,1,0,0,0

"history buff here",0,1,0,0,0,0,0
"heritage day goa",0,1,0,0,0,0,0
"historical exploration",0,1,0,0,0,0,0
"culture day goa",0,1,0,0,0,0,0
"heritage walk goa",0,1,0,0,0,0,0
"history tour goa",0,1,0,0,0,0,0
"old goa exploration",0,1,0,0,0,0,0
"heritage vibes goa",0,1,0,0,0,0,0
"cultural tour goa",0,1,0,0,0,0,0
"historical sites anyone",0,1,0,0,0,0,0
```

### 5. Mixed-Language Inputs - Hinglish (60 samples)

#### Common Hinglish Phrases
```csv
"beach aur food chahiye",1,0,0,0,1,0,0
"kahan beach hai",1,0,0,0,0,0,0
"acchi restaurant batao",0,0,0,0,1,0,0
"nightlife kaisa hai goa mein",0,0,0,0,0,1,0
"shopping ke liye kahan jaoon",0,0,0,0,0,0,1
"adventure activities batao",0,0,1,0,0,0,0
"nature spots dikao",0,0,0,1,0,0,0
"historical places kahan hain",0,1,0,0,0,0,0
"beach pe kya karein",1,0,0,0,0,0,0
"food kahan milega",0,0,0,0,1,0,0
"party karni hai aaj",0,0,0,0,0,1,0
"market kahan hai",0,0,0,0,0,0,1
"thrill activities chahiye",0,0,1,0,0,0,0
"wildlife sanctuary kahan hai",0,0,0,1,0,0,0
"purani jagah dekhni hai",0,1,0,0,0,0,0
"beach ka maza lena hai",1,0,0,0,0,0,0
"khaana khaana hai",0,0,0,0,1,0,0
"club mein jana hai",0,0,0,0,0,1,0
"shopping karni hai",0,0,0,0,0,0,1
"adventure karni hai",0,0,1,0,0,0,0
"nature dekhni hai",0,0,0,1,0,0,0
"history dekhni hai",0,1,0,0,0,0,0
"best beach batao",1,0,0,0,0,0,0
"achha restaurant batao",0,0,0,0,1,0,0
"nightlife enjoy karni hai",0,0,0,0,0,1,0
"shopping karne jana hai",0,0,0,0,0,0,1
"adventure sports karni hai",0,0,1,0,0,0,0
"nature walk karni hai",0,0,0,1,0,0,0
"heritage tour karna hai",0,1,0,0,0,0,0
"beach pe jana hai",1,0,0,0,0,0,0
"khaane ka shauk hai",0,0,0,0,1,0,0
"party sharty karni hai",0,0,0,0,0,1,0
"market ghumna hai",0,0,0,0,0,0,1
"thrill chahiye",0,0,1,0,0,0,0
"greenery dekhni hai",0,0,0,1,0,0,0
"old goa jana hai",0,1,0,0,0,0,0
"beach vibes chahiye",1,0,0,0,0,0,0
"goan food try karna hai",0,0,0,0,1,0,0
"clubbing karni hai",0,0,0,0,0,1,0
"souvenirs kharidne hain",0,0,0,0,0,0,1
"water sports karni hai",0,0,1,0,0,0,0
"waterfall dekhna hai",0,0,0,1,0,0,0
"fort dekhna hai",0,1,0,0,0,0,0
"beach pe relax karna hai",1,0,0,0,0,0,0
"seafood khana hai",0,0,0,0,1,0,0
"casino jana hai",0,0,0,0,0,1,0
"flea market jana hai",0,0,0,0,0,0,1
"scuba diving karni hai",0,0,1,0,0,0,0
"bird watching karni hai",0,0,0,1,0,0,0
"church dekhni hai",0,1,0,0,0,0,0
"sunset beach pe dekhna hai",1,0,0,0,0,0,0
"local cuisine try karni hai",0,0,0,0,1,0,0
"pub crawl karni hai",0,0,0,0,0,1,0
"handicrafts kharidne hain",0,0,0,0,0,0,1
"parasailing karni hai",0,0,1,0,0,0,0
"spice plantation jana hai",0,0,0,1,0,0,0
"temple visit karni hai",0,1,0,0,0,0,0
"beach aur party dono chahiye",1,0,0,0,0,1,0
"food aur shopping dono",0,0,0,0,1,0,1
"adventure aur nature dono",0,0,1,1,0,0,0
"history aur food dono",0,1,0,0,1,0,0
```

---

## Implementation Plan

### Step 1: Create Augmented Dataset
1. Load existing `nlc_training_data_augmented.csv`
2. Add all new samples from this plan
3. Remove duplicates
4. Shuffle the dataset

### Step 2: Retrain Model
1. Run the existing notebook with new dataset
2. Compare metrics with baseline

### Step 3: Evaluate Improvement
Target metrics:
- Adventure F1: 86.7% → 92%+
- Nature F1: 86.7% → 92%+
- Overall Macro F1: 90.7% → 92%+

---

## Summary Statistics

| Category | Current Samples | New Samples | Total |
|----------|-----------------|-------------|-------|
| Adventure | ~400 | 100 | ~500 |
| Nature | ~400 | 100 | ~500 |
| Edge Cases | ~50 | 80 | ~130 |
| Conversational | ~200 | 100 | ~300 |
| Hinglish | ~30 | 60 | ~90 |
| **Total** | **3,427** | **440** | **~3,867** |

---

## Expected Outcomes

1. **Improved Recall**: Adventure and nature categories should see 5-10% improvement in recall
2. **Better Edge Case Handling**: Model will handle negative queries, abbreviations, and typos
3. **Real-World Performance**: Conversational and Hinglish inputs will improve user experience
4. **Robust Multi-label**: More diverse multi-label combinations for complex queries
