# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import threading
import time
from typing import Dict
from typing import List

MIN_TIME_BETWEEN_PROGRESS_UPDATE_SECONDS = 5


class ProgressPresenterFactory:
    def create(self, position: int) -> "ProgressPresenter":
        pass


class ProgressTracker:
    """
    A class for tracking the progress of a task and its sub-tasks.
    """

    def __init__(
        self, title: str, parent: "ProgressTracker", presenter: "ProgressPresenter"
    ):
        """
        :param title: The title of the task being tracked.
        :param parent: The parent task tracker. None if this is the root task.
        :param presenter: The presenter to use for tracking progress.
        """
        self._title = title
        self._parent = parent
        self._children: List["ProgressTracker"] = []
        self._metrics: Dict[str, float] = {}
        self._progress = 0
        self._last_update_time = 0
        self._last_updated_progress = 0
        self._total_iterations = 0
        self._presenter = presenter
        self._lock = threading.Lock()

    def start(self):
        self._presenter.start()

    def end(self):
        self._presenter.end()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.end()

    def add_iterations(self, new_iterations: int):
        """
        Adds new iterations to the total count for this tracker.

        :param new_iterations: The number of new iterations to add.
        """
        self._total_iterations += new_iterations
        self._presenter.adjust_total_iteration(self._total_iterations)
        if self._parent:
            self._parent.add_iterations(new_iterations)

    def update_progress(self, iterations: int):
        # this is not really atomic and only works because of Python GIL
        self._progress += iterations
        current_time = time.time()
        if (
            current_time - self._last_update_time
            > MIN_TIME_BETWEEN_PROGRESS_UPDATE_SECONDS
        ):
            # we have no control over update. It might be expensive call (very least lock is expensive)
            # as update_progress can be called millions or billions of times
            # we need some optimization here so we buffer iterations before calling update.
            with self._lock:
                if (
                    current_time - self._last_update_time
                    > MIN_TIME_BETWEEN_PROGRESS_UPDATE_SECONDS
                ):
                    self._presenter.update(self._progress - self._last_updated_progress)
                    self._last_updated_progress = self._progress
                    self._last_update_time = time.time()

        if self._parent:
            # Propagate the child's updated progress to parent
            self._parent.update_progress(iterations)

    def create_sub_tracker(
        self, title: str, total_iterations: int = 0
    ) -> "ProgressTracker":
        child = ProgressTracker(title, self, self._presenter)
        self._children.append(child)
        child.add_iterations(total_iterations)
        return child

    def track_metric(self, key: str, value: float):
        """
        The tracked metric must be cumulative since it's aggregated in the parent.
        Non-cumulative metrics (like rate, latency, mean, median) will not provide result.
        Example of cumulative metrics are  records processed, errors, time spent, number of requests, successful requests, failed requests.
        """
        self._metrics[key] = self._metrics.get(key, 0) + value
        if self._parent:
            self._parent.track_metric(key, value)

    def get_metrics(self):
        return self._metrics.copy()


###
# Below are sample implmentation of plugins for presenting progress.
###


from abc import ABC, abstractmethod


class ProgressPresenter(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def end(self):
        pass

    @abstractmethod
    def update(self, iterations: int):
        pass

    @abstractmethod
    def adjust_total_iteration(self, total_iterations: int):
        pass


#
# now we can implement strategies for terminal (tqdm) , notebook, cloud :
#


class NotebookProgressPresenter(ProgressPresenter):
    pass


class CloudLoggingProgressPresenter(ProgressPresenter):
    pass


# For example:
#
#
from tqdm import tqdm


class TqdmProgressPresenter(ProgressPresenter):
    def __init__(self, total_iterations: int = 0):
        self._progress = tqdm(total=total_iterations)

    def start(self):
        pass

    def end(self):
        self._progress.close()

    def adjust_total_iterations(self, total_iterations: int):
        self._progress.total = total_iterations

    def update(self, new_iterations: int):
        self._progress.update_progress(new_iterations)


if __name__ == "__main__":
    # This is just an example actually we would use factory method and not pass TqdmProgressPresenter directly
    with ProgressTracker("Main", None, TqdmProgressPresenter()) as tracker:
        # because ingest is in background thread, even though items can be added in steps , its parent is main
        ingestion_tracker = tracker.create_sub_tracker("Ingestion Background Process")
        with tracker.create_sub_tracker("Step 1") as step1_tracker:
            # start ingesting 10 payloads
            ingestion_tracker.add_iterations(10)  # add 10 items to be tracked
            # start ingesting 10 more payloads in background thread
            ingestion_tracker.add_iterations(10)  # add 10 items to be tracked

            with step1_tracker.create_sub_tracker("DAG", 5) as dag_tracker:
                dag_tracker.update_progress(5)  # all 5 dag jobs finished

            with step1_tracker.create_sub_tracker("SQL", 1) as sql_tracker:
                sql_tracker.update_progress(1)  # query-finished
                sql_tracker.track_metric("sql-success", 1)  # if ok
                sql_tracker.track_metric("sql-failure", 1)  # if failed

    ingestion_tracker.update_progress(10)  # 10 payloads ingested
    ingestion_tracker.update_progress(10)  # 10 payloads ingested
    ingestion_tracker.track_metric("success", 20)  # async
    ingestion_tracker.track_metric("lost_payloads", 0)  # async


## If TQDM used, in order not to interfere with std out and normal logigng we may need to write logs using tqdm.write


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


logging.basicConfig(level=logging.INFO, handlers=[TqdmLoggingHandler()])
