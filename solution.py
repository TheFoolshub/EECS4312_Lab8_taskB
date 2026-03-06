## Student Name: Ali Ashraf
## Student ID: 218990184

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    pass


class NotFound(Exception):
    pass


@dataclass(frozen=True)
class UserStatus:
    state: str
    position: Optional[int] = None


class EventRegistration:

    def __init__(self, capacity: int) -> None:
        # Constraint C6: capacity must be non-negative
        if capacity < 0:
            raise ValueError("capacity must be non-negative")

        self.capacity = capacity
        self.registered: List[str] = []
        self.waitlist: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        # Constraint C2: prevent duplicate users
        if user_id in self.registered or user_id in self.waitlist:
            raise DuplicateRequest()

        # AC1: register if capacity available
        if len(self.registered) < self.capacity:
            self.registered.append(user_id)
            return UserStatus("registered")

        # AC2: otherwise waitlist (FIFO)
        self.waitlist.append(user_id)
        return UserStatus("waitlisted", len(self.waitlist))

    def cancel(self, user_id: str) -> None:

        # If registered → remove and promote waitlisted user
        if user_id in self.registered:
            self.registered.remove(user_id)

            # AC3: promote earliest waitlisted user
            if self.waitlist and self.capacity > 0:
                promoted_user = self.waitlist.pop(0)
                self.registered.append(promoted_user)

            return

        # If waitlisted → remove from waitlist
        if user_id in self.waitlist:
            self.waitlist.remove(user_id)
            return

        # Edge case: cancel unknown user
        raise NotFound()

    def status(self, user_id: str) -> UserStatus:

        if user_id in self.registered:
            return UserStatus("registered")

        if user_id in self.waitlist:
            position = self.waitlist.index(user_id) + 1
            return UserStatus("waitlisted", position)

        return UserStatus("none")

    def snapshot(self) -> dict:
        return {
            "registered": list(self.registered),
            "waitlist": list(self.waitlist),
        }
