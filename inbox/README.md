# inbox/

The only place new files go. Drop anything here: docs, spreadsheets, data pulls, images.

Then run `/map-refresh`. The Librarian will:

1. Classify each file (methodology doc, other doc, dataset, competition/pitch material, junk).
2. Move it with `scripts/intake.py`: docs → `archive/`, datasets → `data/raw/`,
   macOS junk (`._*`, `.DS_Store`) deleted. Each file is copied and hash-checked before its source is deleted.
3. Write a text mirror (docs) or data card (datasets) in `knowledge/`.
4. Add a one-line entry to the right `INDEX.md` and refresh the inventory (`manifests/`).

`inbox/seagate/` holds the Seagate's Documents, Pitches, handout and old code, waiting for
Phase 1 intake. `legacy-code/` goes to `archive/legacy-code/`.

Nothing in this folder is committed to git except this README. A hook limits agents here:
they may add new files and edit `inbox/_plan.yaml`, but never sweep, delete or overwrite a
waiting file (`intake.py` does the moving).
