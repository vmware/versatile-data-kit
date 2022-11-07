# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import time

from vdk.plugin.meta_jobs.time_based_queue import TimeBasedQueue


def test_enqueue_dequeue_empty():
    queue = TimeBasedQueue(
        min_ready_time_seconds=2, randomize_delay_seconds=0, dequeue_timeout_seconds=0
    )
    assert queue.dequeue() is None


def test_enqueue_dequeue_not_wait_for_ready():
    queue = TimeBasedQueue(
        min_ready_time_seconds=4, randomize_delay_seconds=0, dequeue_timeout_seconds=0
    )
    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() is None


def test_enqueue_dequeue_wait():
    queue = TimeBasedQueue(
        min_ready_time_seconds=2, randomize_delay_seconds=0, dequeue_timeout_seconds=0
    )
    queue.enqueue(1)
    queue.enqueue(2)
    assert queue.dequeue() is None
    time.sleep(2)
    assert queue.dequeue() == 1
    assert queue.dequeue() == 2
