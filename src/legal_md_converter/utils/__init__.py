"""Utility modules for threading, logging, path handling, and cross-platform support."""

from legal_md_converter.utils.thread_worker import Worker, WorkerSignals, ThreadPool
from legal_md_converter.utils.path_utils import (
    get_home_directory,
    get_desktop_directory,
    validate_file_path,
    validate_directory_path,
    create_safe_filename,
    get_unique_filepath,
    is_supported_file,
)
from legal_md_converter.utils.dependency_checker import DependencyChecker

__all__ = [
    'Worker', 'WorkerSignals', 'ThreadPool',
    'get_home_directory', 'get_desktop_directory',
    'validate_file_path', 'validate_directory_path',
    'create_safe_filename', 'get_unique_filepath',
    'is_supported_file',
    'DependencyChecker',
]
