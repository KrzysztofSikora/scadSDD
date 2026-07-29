# Changelog

Format oparty na [Keep a Changelog](https://keepachangelog.com/), wersje wg
[Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-07-28

### Dodano

- Drugi, niezależny model: **magnetyczny uchwyt na lufę karabinu do sejfu**
  (`magnetic-rifle-mount-001`), dwuczęściowy (base + arm), regulowany w
  zakresie 80–140mm, z rzeczywistym, drukowalnym gwintem trapezowym
  (biblioteka `bd_warehouse`, nowa zależność).
  - Specyfikacja: `specs/rifle-mount/{spec.md,parameters.yaml,constraints.md,decisions.md}`.
  - Kod: `src/cad_project/rifle_mount/{parameters,model,validation,cli}.py`
    — reużywa generyczne `measurements.py`/`exports.py`/`rendering.py`.
  - Wyjście: osobne drzewo `output/rifle-mount/{step,stl,previews,reports,logs}/`.
  - Testy: `tests/rifle_mount/` (31 testów, fixture sesyjna w `conftest.py`
    ze względu na ~20-30s czas budowania per część).
  - Makefile: `rifle-build`, `rifle-validate`, `rifle-render`, `rifle-all`,
    `rifle-clean`, `rifle-view`.
- Opcjonalny viewer **FreeCAD**: `scripts/view.sh` (+ `make view` /
  `make rifle-view`), wykrywa instalację natywną lub Flatpak
  (`org.freecad.FreeCAD`); nie jest zależnością pipeline'u.
- `.claude/CLAUDE.md` zaktualizowany o tabelę wielu modeli w repozytorium.

### Zmieniono

- `pyproject.toml`: dodano zależność `bd_warehouse`, zaktualizowano opis
  projektu (wiele modeli), wersja pakietu 0.1.0 → 0.2.0.

## [0.1.0] — 2026-07-28

### Dodano

- Specyfikacja: `specs/spec.md`, `specs/parameters.yaml` (maszynowe źródło
  parametrów), `specs/constraints.md`, `specs/decisions.md`.
- Parametryczny model uchwytu montażowego (`src/cad_project/model.py`)
  zbudowany w Build123d: podstawa 100×40×5 mm, cztery otwory montażowe
  Ø5 mm (odsunięcie 8 mm od krawędzi), zaokrąglenie krawędzi zewnętrznych
  R3 mm.
- Pomiary geometrii (`measurements.py`): bounding box, objętość,
  powierzchnia, liczba brył, poprawność bryły, opcjonalna masa.
- Eksplicytna walidacja regułowa (`validation.py`) z raportem JSON
  (`output/reports/validation-report.json`).
- Eksport STEP/STL (`exports.py`), deterministyczny (stały znacznik czasu w
  STEP).
- Headless renderowanie podglądu PNG w rzucie izometrycznym
  (`rendering.py`) — matplotlib + ręczne cieniowanie, bez zależności od
  VTK/GUI; błędy renderera raportowane niezależnie od eksportu STEP/STL.
- CLI (`cli.py`): `build`, `export`, `render`, `validate`, `all`, `clean`.
- Skrypty powłoki (`scripts/*.sh`) i `Makefile`.
- Zestaw testów pytest (34 testy): wymiary, geometria/determinizm/błędy,
  eksporty/renderowanie, zgodność specyfikacji.
- Konfiguracja Claude Code: `.claude/CLAUDE.md`, polecenia
  (`/generate-model`, `/build-model`, `/validate-model`, `/review-model`),
  skille (`spec-reader`, `cad-generator`, `cad-validator`, `cad-reviewer`).
- `docs/mcp-roadmap.md` — plan na przyszłość dla serwera MCP.
