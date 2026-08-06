"""Regression tests for stripe partitioning under resume.

Copy these into any project that stripes pyramid work across workers. The bug they
guard against loses data while every worker reports success, so it will not show up
in exit codes, logs, or a random-sample verification.

Run: pytest test_striping.py
"""

import pytest

from manifest import drop_existing, stripe

NSTRIPES = 6


def make_tasks(n=240):
    """(lead, ((y0, y1), (x0, x1))) tasks, like a real output-shard work list."""
    return [((t,), ((y, y + 10), (x, x + 10)))
            for t in range(2) for y in range(0, 60, 10) for x in range(0, 200, 10)][:n]


def key_of(task):
    lead, wins = task
    return lead + tuple(s // 10 for s, _ in wins)


def stripe_then_filter(tasks, i, n, done):
    """Correct order: partition the stable list, then drop finished work."""
    return drop_existing(stripe(tasks, i, n), done, key_of)


def filter_then_stripe(tasks, i, n, done):
    """The buggy order, kept so the guard itself is tested."""
    return stripe(drop_existing(tasks, done, key_of), i, n)


def done_after(tasks, frac):
    """A contiguous done-set, e.g. a clean resume after a killed single worker."""
    return {key_of(t) for t in tasks[: int(len(tasks) * frac)]}


def observed_done(tasks, worker, nstripes, frac=0.5):
    """What worker `worker` sees when it lists, mid-run, in a concurrent build.

    Realistic and *scattered*, which matters: each already-running worker has
    written a prefix of its own stripe, and those tasks are interleaved throughout
    the global list rather than forming a contiguous block. A contiguous done-set
    makes the buggy ordering look harmless, because the tasks it drops happen to be
    the ones already written.
    """
    done = set()
    for j in range(worker):                      # workers that started earlier
        mine = stripe(tasks, j, nstripes)
        done |= {key_of(t) for t in mine[: int(len(mine) * frac)]}
    return done


def test_partition_is_exact_with_no_prior_work():
    tasks = make_tasks()
    claimed = [t for i in range(NSTRIPES) for t in stripe_then_filter(tasks, i, NSTRIPES, set())]
    assert sorted(map(key_of, claimed)) == sorted(map(key_of, tasks))
    assert len(claimed) == len(set(map(key_of, claimed))), "no task claimed twice"


def test_partition_holds_when_workers_see_different_done_sets():
    """The real race: each worker lists 'already done' at a different moment."""
    tasks = make_tasks()
    claimed, observed = [], set()
    for i in range(NSTRIPES):
        done = observed_done(tasks, i, NSTRIPES)   # scattered, as in a real run
        observed |= done
        claimed += stripe_then_filter(tasks, i, NSTRIPES, done)

    keys = set(map(key_of, claimed))
    missing = [key_of(t) for t in tasks if key_of(t) not in keys and key_of(t) not in observed]
    assert missing == [], f"{len(missing)} tasks would never be written"
    assert len(claimed) == len(keys), "no task claimed twice"


def test_buggy_order_really_loses_tasks():
    """Anti-rot: if this ever passes, the test above has stopped proving anything."""
    tasks = make_tasks()
    claimed, observed = [], set()
    for i in range(NSTRIPES):
        done = observed_done(tasks, i, NSTRIPES)
        observed |= done
        claimed += filter_then_stripe(tasks, i, NSTRIPES, done)

    keys = set(map(key_of, claimed))
    missing = [key_of(t) for t in tasks if key_of(t) not in keys and key_of(t) not in observed]
    assert missing, "expected the filter-then-stripe order to drop tasks"


def test_single_worker_unaffected():
    tasks = make_tasks()
    assert stripe_then_filter(tasks, 0, 1, set()) == tasks


def test_every_stripe_gets_work():
    tasks = make_tasks()
    for i in range(NSTRIPES):
        assert stripe(tasks, i, NSTRIPES), f"stripe {i} empty — reduce nstripes"


def test_resume_writes_each_remaining_task_exactly_once():
    """After a partial run, the union of stripes must equal exactly the gap."""
    tasks = make_tasks()
    done = done_after(tasks, 0.5)
    claimed = [t for i in range(NSTRIPES) for t in stripe_then_filter(tasks, i, NSTRIPES, done)]
    keys = sorted(map(key_of, claimed))
    expect = sorted(key_of(t) for t in tasks if key_of(t) not in done)
    assert keys == expect
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("n", [1, 2, 3, 5, 6, 7, 13])
def test_partition_exact_for_various_worker_counts(n):
    tasks = make_tasks()
    claimed = [t for i in range(n) for t in stripe(tasks, i, n)]
    assert sorted(map(key_of, claimed)) == sorted(map(key_of, tasks))
