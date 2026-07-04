from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from fizmo.config import LoggingConfig
from fizmo.models import ToolResult


class DataLogger:
    def __init__(self, config: LoggingConfig) -> None:
        self.config = config
        self.directory = Path(config.directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = self.directory / f"{timestamp}_behavior.jsonl"
        self.prune()

    def log_tool_result(self, command: str, result: ToolResult) -> None:
        if not self.config.enabled:
            return
        record = {
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "command": command,
            "result": _to_jsonable(result),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        self.prune()

    def list_logs(self) -> list[Path]:
        return _list_log_files(self.directory)

    def prune(self) -> dict[str, list[Path]]:
        result = {"deleted": [], "skipped": []}
        count_result = _prune_by_count(self.directory, self.config.max_files)
        size_result = _prune_by_size(self.directory, self.config.max_total_mb)
        result["deleted"].extend(count_result["deleted"])
        result["deleted"].extend(size_result["deleted"])
        result["skipped"].extend(count_result["skipped"])
        result["skipped"].extend(size_result["skipped"])
        return result

    def clear(self) -> dict[str, list[Path]]:
        result = {"deleted": [], "skipped": []}
        for path in self.list_logs():
            if _safe_unlink(path):
                result["deleted"].append(path)
            else:
                result["skipped"].append(path)
        return result


def summarize_logs(config: LoggingConfig) -> dict[str, Any]:
    directory = Path(config.directory)
    files = _list_log_files(directory)
    total_bytes = sum(path.stat().st_size for path in files)
    return {
        "directory": str(directory),
        "count": len(files),
        "total_mb": round(total_bytes / (1024 * 1024), 3),
        "files": [
            {"path": str(path), "size_bytes": path.stat().st_size}
            for path in files
        ],
    }


def prune_logs(config: LoggingConfig) -> dict[str, list[Path]]:
    return DataLogger(config).prune()


def clear_logs(config: LoggingConfig) -> dict[str, list[Path]]:
    logger = DataLogger(config)
    return logger.clear()


def _list_log_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*.jsonl"), key=lambda path: path.stat().st_mtime)


def _prune_by_count(directory: Path, max_files: int) -> dict[str, list[Path]]:
    result = {"deleted": [], "skipped": []}
    if max_files <= 0:
        return result
    files = _list_log_files(directory)
    while len(files) > max_files:
        victim = files.pop(0)
        if _safe_unlink(victim):
            result["deleted"].append(victim)
        else:
            result["skipped"].append(victim)
    return result


def _prune_by_size(directory: Path, max_total_mb: float) -> dict[str, list[Path]]:
    result = {"deleted": [], "skipped": []}
    max_bytes = max_total_mb * 1024 * 1024
    files = _list_log_files(directory)
    total = sum(path.stat().st_size for path in files)
    while files and total > max_bytes:
        victim = files.pop(0)
        size = victim.stat().st_size
        if _safe_unlink(victim):
            result["deleted"].append(victim)
            total -= size
        else:
            result["skipped"].append(victim)
            total -= size
    return result


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


def _safe_unlink(path: Path) -> bool:
    try:
        path.unlink()
        return True
    except PermissionError:
        return False
