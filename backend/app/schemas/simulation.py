from typing import Any, Literal

from pydantic import BaseModel, Field

TravelType = Literal["family", "solo", "duo", "couple", "friends", "group"]
TravelDistance = Literal["more", "less"]
HotelLocation = Literal["panjim", "margao", "mapusa", "canacona"]
Region = Literal["north", "central", "south"]


class Module1Request(BaseModel):
    user_preference: str
    min_rating: float = 3.0
    use_llm_interests: bool = False


class Module2Request(BaseModel):
    num_days: int = Field(ge=1, le=10)
    min_reviews: int = 1
    random_state: int = 42
    travel_distance: TravelDistance = "more"
    hotel_location: HotelLocation | None = None
    hotel_address: str | None = None
    hotel_lat: float | None = None
    hotel_lon: float | None = None
    region: Region | None = None
    user_preference: str | None = None


class Module4Request(BaseModel):
    num_days: int = Field(ge=1, le=10)
    user_preference: str
    travel_type: TravelType = "solo"
    travel_distance: TravelDistance = "more"
    hotel_location: HotelLocation | None = None
    hotel_address: str | None = None
    hotel_lat: float | None = None
    hotel_lon: float | None = None
    region: Region | None = None
    min_rating: float = 3.0
    min_reviews: int = 1
    population_size: int = 150
    max_generations: int = 100
    mutation_rate: float = 0.3
    crossover_rate: float = 0.7
    early_stopping_patience: int = Field(default=50, ge=5, le=200)
    random_state: int = 42
    use_osrm: bool = True
    use_llm_fitness_profile: bool = True
    use_llm_interests: bool = True
    include_ga_history: bool = True
    use_llm_itinerary_qa: bool = True
    use_llm_itinerary_retry: bool = True
    use_llm_secondary_itinerary_qa: bool = False
    mobile_only: bool = False


class Module4NarrationRequest(BaseModel):
    day: int = Field(ge=1, le=10)
    rank: int = Field(ge=1, le=10)
    user_preference: str = ""
    route: list[dict[str, Any]]


class SimulationResponse(BaseModel):
    data: dict[str, Any]
