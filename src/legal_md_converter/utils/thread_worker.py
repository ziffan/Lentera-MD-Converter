"""
Thread worker utilities for Legal-MD-Converter.

Provides thread-safe worker classes for background processing
to keep the UI responsive during long operations.
"""

import logging
from typing import Any, Optional, Callable

from PySide6.QtCore import QObject, QThread, Signal, QMutex


logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int, int)  # current, total
    cancelled = Signal()


class Worker(QThread):
    """
    Generic worker thread for background processing.

    Features:
    - Progress reporting via Signal
    - Error handling with exception propagation
    - Cancel support via QMutex

    Usage:
        worker = Worker(fn, *args, **kwargs)
        worker.signals.result.connect(handle_result)
        worker.signals.error.connect(handle_error)
        worker.signals.finished.connect(cleanup)
        worker.start()
        
        # To cancel:
        worker.cancel()
    """

    def __init__(
        self,
        fn: Callable,
        *args,
        **kwargs
    ) -> None:
        super().__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Cancellation support
        self._cancelled = False
        self._cancel_mutex = QMutex()

        # Store result for retrieval
        self._result: Optional[Any] = None
        self._error: Optional[Exception] = None

    def cancel(self) -> None:
        """
        Request cancellation of the worker.
        Thread-safe via QMutex.
        """
        self._cancel_mutex.lock()
        try:
            self._cancelled = True
            logger.debug(f'Cancel requested for {self.fn.__name__}')
        finally:
            self._cancel_mutex.unlock()

    def is_cancelled(self) -> bool:
        """
        Check if cancellation was requested.
        Thread-safe via QMutex.
        """
        self._cancel_mutex.lock()
        try:
            return self._cancelled
        finally:
            self._cancel_mutex.unlock()

    def run(self) -> None:
        """Execute the worker function."""
        try:
            logger.debug(f'Worker starting: {self.fn.__name__}')
            
            # Check cancellation before starting
            if self.is_cancelled():
                self.signals.cancelled.emit()
                return
            
            self._result = self.fn(*self.args, **self.kwargs)
            
            # Check cancellation after completion
            if self.is_cancelled():
                self.signals.cancelled.emit()
                return
            
            self.signals.result.emit(self._result)

        except Exception as e:
            logger.error(f'Worker error: {e}', exc_info=True)
            self._error = e
            self.signals.error.emit((e,))

        finally:
            self.signals.finished.emit()
            logger.debug(f'Worker finished: {self.fn.__name__}')

    def get_result(self) -> Optional[Any]:
        """Get the result from the worker."""
        return self._result

    def has_error(self) -> bool:
        """Check if the worker encountered an error."""
        return self._error is not None

    def get_error(self) -> Optional[Exception]:
        """Get the error from the worker."""
        return self._error


class BatchWorker(Worker):
    """
    Worker for batch processing operations.

    Provides progress tracking for operations on multiple items.
    """

    def __init__(
        self,
        fn: Callable,
        items: list,
        *args,
        **kwargs
    ) -> None:
        kwargs['items'] = items
        super().__init__(fn, *args, **kwargs)
        self.items = items

    def run(self) -> None:
        """Execute the batch worker function with progress tracking."""
        try:
            total = len(self.items)
            logger.debug(f'Batch worker starting: {self.fn.__name__} ({total} items)')

            # Check cancellation before starting
            if self.is_cancelled():
                self.signals.cancelled.emit()
                return

            self._result = self.fn(*self.args, **self.kwargs)
            
            # Check cancellation after completion
            if self.is_cancelled():
                self.signals.cancelled.emit()
                return
            
            self.signals.result.emit(self._result)

        except Exception as e:
            logger.error(f'Batch worker error: {e}', exc_info=True)
            self._error = e
            self.signals.error.emit((e,))

        finally:
            self.signals.finished.emit()
            logger.debug('Batch worker finished')


class ThreadPool:
    """
    Simple thread pool manager for concurrent operations.
    
    Usage:
        pool = ThreadPool()
        pool.add_task(fn1, *args1)
        pool.add_task(fn2, *args2)
        pool.start_all()
        pool.wait_for_completion()
    """
    
    def __init__(self, max_threads: int = 4) -> None:
        """
        Initialize the thread pool.
        
        Args:
            max_threads: Maximum number of concurrent threads
        """
        self.max_threads = max_threads
        self.workers: list[Worker] = []
        self._running = False
    
    def add_task(self, fn: Callable, *args, **kwargs) -> Worker:
        """
        Add a task to the pool.
        
        Args:
            fn: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Worker: The worker instance for this task
        """
        worker = Worker(fn, *args, **kwargs)
        self.workers.append(worker)
        return worker
    
    def start_all(self) -> None:
        """Start all workers in the pool."""
        self._running = True
        
        for worker in self.workers:
            worker.start()
        
        logger.info(f'Started {len(self.workers)} workers')
    
    def wait_for_completion(self) -> None:
        """Wait for all workers to complete."""
        for worker in self.workers:
            worker.wait()
        
        self._running = False
        logger.info('All workers completed')
    
    def get_results(self) -> list[Any]:
        """Get results from all workers."""
        return [worker.get_result() for worker in self.workers]
    
    def has_errors(self) -> bool:
        """Check if any workers encountered errors."""
        return any(worker.has_error() for worker in self.workers)
    
    def clear(self) -> None:
        """Clear all workers from the pool."""
        self.workers.clear()
        self._running = False
    
    def is_running(self) -> bool:
        """Check if the pool is currently running."""
        return self._running
