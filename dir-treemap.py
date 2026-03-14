from dataclasses import dataclass

@dataclass(frozen=True)
class DirectoryEntry:
    name: str
    size_bytes: int


import os
import sys
from typing import List, Dict, Optional


def create_result_object(dir_name: str, size: int) -> DirectoryEntry:
    return DirectoryEntry(name=dir_name, size_bytes=size)


def get_file_size(file_path: str) -> Optional[int]:
    """
    Safely retrieve the size of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        Optional[int]: File size in bytes, or None if an error occurred.
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        print(f"Error reading file size of '{file_path}': {e}")
        return None


def accumulate_sizes_to_ancestors(directory: str, size: int, root_dir: str, dir_sizes: Dict[str, int]):
    """
    Accumulate a given `size` to all ancestor directories up to the `root_dir`.

    Args:
        directory (str): The current directory path.
        size (int): File size in bytes to be propagated upwards.
        root_dir (str): The original root directory. Propagation stops at this level.
    """
    current = directory
    while True:
        if current not in dir_sizes:
            dir_sizes[current] = 0

        dir_sizes[current] += size
        parent = os.path.dirname(current)
        if parent == current or current == root_dir:
            break
        current = parent


def build_directory_entries(sizes_dict: Dict[str, int]) -> List[DirectoryEntry]:
    """
    Convert a dictionary of directory sizes into a list of `DirectoryEntry` objects.

    Args:
        sizes_dict (Dict[str, int]): A mapping from full directory paths to their total size in bytes.

    Returns:
        List[DirectoryEntry]: A list of structured data entries.
    """
    return [create_result_object(dir_name, size) for dir_name, size in sizes_dict.items()]


def collect_all_directory_info(root_dir: str, include_subdirectories: bool = True) -> List[DirectoryEntry]:
    """
    Main function that orchestrates all steps to compute directory sizes.

    Args:
        root_dir (str): The starting point of the file system traversal.

    Returns:
        List[DirectoryEntry]: A list of structured data entries with directory names and their total size.
    """
    dir_sizes: Dict[str, int] = {}

    dirs = [root for root, _, _ in os.walk(root_dir)]
    for root in dirs:
        if root not in dir_sizes:
            dir_sizes[root] = 0

        for file in os.listdir(root):
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                size = get_file_size(file_path)
                if size is not None:
                    accumulate_sizes_to_ancestors(root, size, root_dir, dir_sizes)

    if include_subdirectories:
        return build_directory_entries(dir_sizes)
    else:
        first_level_dirs = [os.path.join(root_dir, name)
                            for name in os.listdir(root_dir)
                            if os.path.isdir(os.path.join(root_dir, name))]
        result_entries = [
            create_result_object(dir_name, dir_sizes.get(dir_name, 0))
            for dir_name in first_level_dirs
        ]
        return result_entries


import plotly.express as px
import pandas as pd


def bytes_to_mb(b: int) -> float:
    return b / (1024 ** 2)


def list_to_treemap(root_dir: str, results: List[DirectoryEntry]):
    results = results[1:]
    
    x = [ r.name for r in results]
    y = [ bytes_to_mb(r.size_bytes) for r in results]
    
    data = {
        "path": x,
        "MB": y
    }

    df = pd.DataFrame(data)
    fig = px.treemap(df,
                     path=[px.Constant(root_dir), 'path'],
                     values='MB',
                     color='MB',
                     color_continuous_scale="Viridis")
    fig.show()


if __name__ == "__main__":
    input_directory = "C:\\"
    results: List[DirectoryEntry] = collect_all_directory_info(input_directory)
    list_to_treemap(input_directory, results)
