import os
import csv
from pathlib import Path
from typing import Iterator, Dict


class CSVPostWriter:
    def __init__(
        self,
        folder_name: str,
        root_dir: str = "data",
        max_lines_per_file: int = 5000,
        with_original=False,
    ):
        self.max_lines = max_lines_per_file

        self.output_dir = Path(root_dir) / folder_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_file_index = 1
        self.current_line_count = 0
        self.current_file = None
        self.writer = None

        self.fields_order = [
            "date",
            "id",
            "from_id",
            "owner_id",
            "reposts",
            "likes",
            "views",
            "comments",
            "text",
        ]

        if with_original:
            self.fields_order.append("original_text")

    def _open_new_file(self):
        if self.current_file:
            self.current_file.close()

        file_path = self.output_dir / f"posts_part_{self.current_file_index}.csv"
        self.current_file = open(file_path, mode="w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.current_file, fieldnames=self.fields_order)
        self.writer.writeheader()
        self.current_line_count = 0
        self.current_file_index += 1

    def write_posts(self, posts: Iterator[Dict]):
        for post in posts:
            if self.writer is None or self.current_line_count >= self.max_lines:
                self._open_new_file()
            self.writer.writerow({k: post.get(k, "") for k in self.fields_order})
            self.current_line_count += 1

    def close(self):
        if self.current_file:
            self.current_file.close()
            self.current_file = None
