"""Fetch modules for raw datasets, one module per source (``/ingest``).

Each module downloads into ``inbox/<dataset-slug>/`` with the provider's file names;
``scripts/intake.py`` files the download into ``data/raw/``. Provenance of every download
goes in ``data/sources.yaml``. Standard: ``docs/standards/data.md``.
"""
