# Logic layer where all my backend classes live

from dataclasses import dataclass, field


@dataclass
class Preferences:
    """Walking and feeding preferences, shared by Pet and User."""
    walking_amount: float
    walking_times: list[str] = field(default_factory=list)
    feeding_amount: float = 0.0
    feeding_times: list[str] = field(default_factory=list)

    def update_walking_amount(self, amount: float) -> None:
        pass

    def update_walking_times(self, times: list[str]) -> None:
        pass

    def update_feeding_amount(self, amount: float) -> None:
        pass

    def update_feeding_times(self, times: list[str]) -> None:
        pass


@dataclass
class Pet:
    """A single pet and its care preferences."""
    species: str
    ideal_weight: float
    weight: float
    preferences: Preferences

    def update_weight(self, weight: float) -> None:
        pass

    def update_preferences(self, preferences: Preferences) -> None:
        pass


@dataclass
class Activity:
    """A time-specific entry in the user's schedule."""
    name: str
    start_time: str
    end_time: str


class UserSchedule:
    """The user's own time-specific activities."""

    def __init__(self) -> None:
        self.activities: list[Activity] = []

    def add_activity(self, activity: Activity) -> None:
        pass

    def remove_activity(self, activity: Activity) -> None:
        pass


class PetCaringSchedule:
    """The optimized pet-caring schedule generated for a user."""

    def __init__(self, user: "User") -> None:
        self.user = user


class User:
    """The app user, owning pets, schedules, and preferences."""

    def __init__(
        self,
        user_schedule: UserSchedule,
        pet_caring_preferences: Preferences,
    ) -> None:
        self.pets: list[Pet] = []
        self.user_schedule = user_schedule
        self.pet_caring_preferences = pet_caring_preferences
        self.pet_caring_schedule: PetCaringSchedule | None = None

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def update_schedule(self, user_schedule: UserSchedule) -> None:
        pass

    def update_pet_caring_preferences(self, preferences: Preferences) -> None:
        pass
