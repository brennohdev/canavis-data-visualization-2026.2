from __future__ import annotations

from pathlib import Path

import pandas as pd

from canavis.config import load_settings


def dataset_path(directory: Path, name: str) -> Path:
    suffix = load_settings().storage.format
    return directory / f"{name}.{suffix}"


def write(frame: pd.DataFrame, directory: Path, name: str) -> Path:
    storage = load_settings().storage
    directory.mkdir(parents=True, exist_ok=True)
    destination = dataset_path(directory, name)
    if storage.format == "parquet":
        frame.to_parquet(destination, compression=storage.compression, index=False)
    elif storage.format == "csv":
        frame.to_csv(destination, index=False, encoding="utf-8")
    else:
        raise ValueError(f"Formato de storage não suportado: {storage.format}")
    return destination


def read(directory: Path, name: str) -> pd.DataFrame:
    storage = load_settings().storage
    source = dataset_path(directory, name)
    if storage.format == "parquet":
        return pd.read_parquet(source)
    if storage.format == "csv":
        return pd.read_csv(source)
    raise ValueError(f"Formato de storage não suportado: {storage.format}")


def exists(directory: Path, name: str) -> bool:
    return dataset_path(directory, name).exists()
