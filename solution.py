## Student Name: Ali Ashraf
## Student ID: 218990184

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised when a user attempts to register more than once."""
    pass


class NotFound(Exception):
    """Raised when a user cancellation is attempted for a non-existent user."""
    pass


@dataclass(frozen=True)
class UserStatus:
    state: str
    position: Optional[int] = None


class EventRegistration:

    def __init__(self, capacity: int) -> None:
        # Constraint C6: capacity must be non-negative
        if capacity < 0:
            raise ValueError("Event capacity must be a non-negative value.")

        self.capacity = capacity
        self.registered: List[str] = []
        self.waitlist: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        # C2: prevent duplicate registrations
        if user_id in self.registered or user_id in self.waitlist:
            raise DuplicateRequest(
                f"User '{user_id}' is already registered or waitlisted."
            )

        # AC6: capacity = 0 → everyone waitlisted
        if self.capacity == 0:
            self.waitlist.append(user_id)
            return UserStatus("waitlisted", len(self.waitlist))

        # AC1: register if capacity available
        if len(self.registered) < self.capacity:
            self.registered.append(user_id)
            return UserStatus("registered")

        # AC2: otherwise waitlist (FIFO)
        self.waitlist.append(user_id)
        return UserStatus("waitlisted", len(self.waitlist))

    def cancel(self, user_id: str) -> None:

        # Registered user cancellation
        if user_id in self.registered:
            self.registered.remove(user_id)

            # AC3: promote earliest waitlisted user
            if self.waitlist and self.capacity > 0:
                promoted_user = self.waitlist.pop(0)
                self.registered.append(promoted_user)

            return

        # Waitlisted user cancellation
        if user_id in self.waitlist:
            self.waitlist.remove(user_id)
            return

        # C3 + AC5: explicit failure explanation
        raise NotFound(f"User '{user_id}' does not exist in the system.")

    def status(self, user_id: str) -> UserStatus:

        if user_id in self.registered:
            return UserStatus("registered")

        if user_id in self.waitlist:
            position = self.waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)

        # explicit status
        return UserStatus("none")

    def snapshot(self) -> dict:
        return {
            "registered": list(self.registered),
            "waitlist": list(self.waitlist),
        }
