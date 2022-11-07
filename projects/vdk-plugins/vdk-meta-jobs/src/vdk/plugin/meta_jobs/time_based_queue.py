# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import time
from collections import deque
from dataclasses import dataclass
from random import randint
from typing import Any


@dataclass
class _QueueEntry:
    element: Any
    ready_time: float


class TimeBasedQueue:
    """
    Use it to enqueue elements until element is ready to be dequeued.
    """

    def __init__(
        self,
        min_ready_time_seconds=10,
        randomize_delay_seconds=10,
        dequeue_timeout_seconds=5,
    ):
        """

        :param min_ready_time_seconds: the minimum time in seconds for element to be ready
        :param randomize_delay_seconds: added delay in seconds randomly between [0 , random_delay_seconds]
        :param dequeue_timeout_seconds: dequeue method blocks maximum that many seconds before returning.
        """
        self._elements: deque[_QueueEntry] = deque()
        self._min_ready_time_seconds = min_ready_time_seconds
        self._randomize_delay_seconds = randomize_delay_seconds
        self._dequeue_timeout_seconds = dequeue_timeout_seconds

    def enqueue(self, element):
        ready_time = self._min_ready_time_seconds + randint(
            0, self._randomize_delay_seconds
        )
        self._elements.append(_QueueEntry(element, time.time() + ready_time))

    def dequeue(self):
        """
        Dequeues the next ready element. Element is ready if their ready time (duration) has passed.
        Otherwise it will wait up to dequeue_timeout_seconds and return None if no element is ready.
        If the queue is empty it returns immediately with None.
        """
        if len(self._elements) > 0:
            entry = self._elements[0]
            if entry.ready_time <= time.time():
                return self._elements.popleft().element
            else:
                self.__wait_for_entry_to_be_ready(entry.ready_time)
                if entry.ready_time <= time.time():
                    return self._elements.popleft().element
        return None

    def size(self):
        return len(self._elements)

    def __wait_for_entry_to_be_ready(self, ready_time: float):
        sleep_time_seconds = ready_time - time.time()
        sleep_time_seconds = min(sleep_time_seconds, self._dequeue_timeout_seconds)
        time.sleep(sleep_time_seconds)
