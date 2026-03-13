import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################

# EC1: capacity = 0
def test_edge_case_capacity_zero():
    er = EventRegistration(capacity=0)

    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    assert er.snapshot()["registered"] == []


# EC2: duplicate registration
def test_edge_case_duplicate_registration():
    er = EventRegistration(capacity=2)

    er.register("u1")

    with pytest.raises(DuplicateRequest):
        er.register("u1")


# EC3: registered user cancels with waitlist
def test_edge_case_promotion_after_cancel():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")

    er.cancel("u1")

    assert er.status("u2") == UserStatus("registered")


# EC4: waitlisted user cancels
def test_edge_case_waitlist_cancel():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")

    er.cancel("u2")

    assert er.status("u2") == UserStatus("none")

def test_reregister_after_cancel():
    er = EventRegistration(capacity=1)

    # user registers
    er.register("u1")

    # user cancels
    er.cancel("u1")

    # user should be able to register again
    status = er.register("u1")

    assert status == UserStatus("registered")

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == []


    ######################################################################
    ##Lab9 
    ###############################
    # C2: deterministic system behavior
# AC1, AC2
def test_deterministic_behavior_same_sequence():
    er1 = EventRegistration(capacity=2)
    er2 = EventRegistration(capacity=2)

    sequence = ["u1", "u2", "u3", "u4"]

    for u in sequence:
        er1.register(u)

    for u in sequence:
        er2.register(u)

    # same operations must produce identical system state
    assert er1.snapshot() == er2.snapshot()

# C3: system must explain invalid actions
# AC5
def test_cancel_unknown_user_raises_notfound():
    er = EventRegistration(capacity=2)

    with pytest.raises(NotFound):
        er.cancel("unknown_user")

# C1: consistent behavior during repeated operations
# AC3
def test_multiple_cancellations_sequential_promotion():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")  # promotes u2
    er.cancel("u2")  # promotes u3

    assert er.status("u3") == UserStatus("registered")

# EC: querying user not in system
# C3
def test_status_for_unknown_user():
    er = EventRegistration(capacity=2)

    status = er.status("ghost")

    assert status == UserStatus("none")

# EC6: multiple users registering when one slot remains
# C1, C5
def test_multiple_users_one_remaining_slot():
    er = EventRegistration(capacity=1)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("waitlisted", 1)
    assert s3 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
