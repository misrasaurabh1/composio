"""
File I/O tool for Composio.
"""

import os
import typing as t

from composio.tools.local.base import Action, Tool

from .actions import CreateIndex, IndexStatus, SearchCodebase


class CodeIndexTool(Tool):
    """Code index tool."""

    def actions(self) -> t.List[t.Type[Action]]:
        """Return the list of actions."""
        return [CreateIndex, IndexStatus, SearchCodebase]

    def triggers(self) -> t.List:
        """Return the list of triggers."""
        return []

    def _process_file(self, chroma_collection, file_path: str, repo_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            return

        windows = self._create_windows(content)
        file_extension = os.path.splitext(file_path)[1].lower()
        file_type = SUPPORTED_FILE_EXTENSIONS.get(file_extension, "Unknown")

        for start, end, window_content in windows:
            metadata = {
                "start_line": start,
                "end_line": end,
                "file_path": os.path.relpath(file_path, repo_path),
                "file_extension": file_extension,
                "file_type": file_type,
            }
            chroma_collection.add(
                documents=[window_content],
                metadatas=[metadata],
                ids=[f"{file_path}_{start}_{end}"],
            )
