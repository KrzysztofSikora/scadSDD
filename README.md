# Spec-Driven CAD (Build123d)

Lokalnie działający system Spec-Driven Development dla CAD: specyfikacja w
`specs/` jest źródłem prawdy, kod w `src/cad_project/` generuje geometrię w
[Build123d](https://build123d.readthedocs.io/), a automatyczna walidacja
porównuje wynikowy model z wymaganiami i zapisuje raport JSON.

To repozytorium hostuje **dwa niezależne modele**, każdy ze swoją
specyfikacją, kodem, testami i CLI:

1. **Uchwyt montażowy** (`bracket-001`) — prosta płyta z czterema otworami
   montażowymi i zaokrągleniem krawędzi. Opisany w reszcie tego README.
2. **Magnetyczny uchwyt na lufę karabinu do sejfu**
   (`magnetic-rifle-mount-001`) — dwuczęściowy, regulowany uchwyt z
   prawdziwym, drukowalnym gwintem. Zobacz
   [„Drugi model: magnetyczny uchwyt na lufę"](#drugi-model-magnetyczny-uchwyt-na-lufę-karabinu) niżej.

## Dlaczego specyfikacja jest źródłem prawdy

Ten projekt istnieje po to, żeby modelowanie CAD wspomagane przez Claude
Code było **odtwarzalne i kontrolowalne**: człowiek opisuje wymagania w
`specs/spec.md` (czytelnie) i `specs/parameters.yaml` (maszynowo), a Claude
(albo dowolny inny agent/deweloper) generuje kod, który te wymagania
realizuje. Kod nigdy nie zmienia wymagań, żeby "przejść" walidację — jeśli
walidacja nie przechodzi, poprawia się **implementację**, a jeśli
specyfikacja jest niejasna albo sprzeczna, generowanie się zatrzymuje i
problem jest zgłaszany człowiekowi zamiast być zgadywanym. Pełne zasady
pracy z Claude Code są w [`.claude/CLAUDE.md`](.claude/CLAUDE.md).

`specs/parameters.yaml` jest **jedynym maszynowym źródłem** wartości
liczbowych (długość, szerokość, średnice, tolerancje...).
`src/cad_project/parameters.py` wczytuje ten plik bezpośrednio — żadna
wartość nie jest wpisana na stałe gdzie indziej w kodzie. `specs/spec.md`
zawiera tę samą tabelę w formie czytelnej dla człowieka plus dosłowną kopię
YAML w bloku ```` ```yaml ````; `tests/test_spec_compliance.py` automatycznie
sprawdza, że oba pliki się zgadzają (parserem YAML, nie wyrażeniami
regularnymi po Markdownie).

## Wymagania systemowe

* Linux (testowane na Ubuntu; skrypty zakładają bash).
* Python 3.12+.
* `libcairo` (zwykle już obecna w systemie) — niepotrzebna bezpośrednio, ale
  część zależności graficznych jej używa.
* Brak wymogu GPU/GUI — cały pipeline, łącznie z podglądem PNG, działa w
  pełni headless.
* **FreeCAD (opcjonalnie)** — nie jest zależnością pipeline'u (build/export/
  validate/render działają bez niego), ale jeśli chcesz interaktywnie
  obejrzeć/obrócić wygenerowany model STEP, a nie tylko statyczny podgląd
  PNG, zainstaluj go osobno:
  ```bash
  sudo apt update && sudo apt install freecad     # Debian/Ubuntu/Mint
  # albo: flatpak install --user -y flathub org.freecad.FreeCAD
  # albo: AppImage bez sudo — https://www.freecad.org/downloads.php
  ```
  Zobacz sekcję "Podgląd modelu w FreeCAD" niżej.

## Instalacja krok po kroku

```bash
git clone <adres-repozytorium> spec-driven-cad
cd spec-driven-cad

# Utworzenie i wypełnienie .venv (build123d, matplotlib, pytest, ruff, ...)
bash scripts/setup.sh
# albo: make setup
```

`scripts/setup.sh` tworzy `.venv/` w katalogu repozytorium (jeśli nie
istnieje) i instaluje projekt w trybie edytowalnym wraz z zależnościami
deweloperskimi (`pip install -e ".[dev]"`).

## Aktywacja środowiska

```bash
source .venv/bin/activate
```

Od tego momentu komendy `python -m cad_project.cli ...`, `pytest`, `ruff`
działają bezpośrednio. Bez aktywacji można też wywoływać binaria wprost:
`.venv/bin/python -m cad_project.cli ...`.

## Uruchomienie przykładowego modelu

Przykładowy model to parametryczny uchwyt montażowy: podstawa 100×40×5 mm,
cztery otwory montażowe Ø5 mm (środek 8 mm od krawędzi), zaokrąglenie
krawędzi zewnętrznych R3 mm — pełny opis w
[`specs/spec.md`](specs/spec.md).

```bash
python -m cad_project.cli build
```

To tylko buduje model w pamięci i wypisuje podstawowe fakty geometryczne
(liczba brył, bounding box, objętość) — nic nie zapisuje na dysk.

## Generowanie STEP/STL/PNG

```bash
python -m cad_project.cli export   # output/step/model.step, output/stl/model.stl
python -m cad_project.cli render   # output/previews/model.png
```

Albo wszystko naraz (build → measure → validate → export STEP → export STL
→ render PNG → zapis raportu):

```bash
python -m cad_project.cli all
# albo: make all / bash scripts/build.sh
```

Kod wyjścia `all` to `0`, jeśli walidacja przeszła (`status: "passed"` w
raporcie), a różny od zera w przeciwnym razie — nadaje się do CI.

**Renderowanie PNG jest odseparowane od eksportu STEP/STL**: jeśli
renderer zawiedzie, STEP i STL i tak powstają, a błąd renderera trafia
osobno do pola `exports.preview` (i `warnings`) w raporcie — nie blokuje
reszty pipeline'u.

## Podgląd modelu w FreeCAD (opcjonalnie)

`output/previews/model.png` daje szybki, statyczny podgląd izometryczny bez
żadnych dodatkowych narzędzi. Jeśli chcesz **interaktywnie** obejrzeć,
obrócić albo zmierzyć wygenerowany model STEP, możesz otworzyć go w
[FreeCAD](https://www.freecad.org/) — to opcjonalny viewer, nie zależność
pipeline'u (build/export/validate/render działają bez FreeCAD).

Instalacja (jednorazowo, wymaga sudo albo Flatpak/AppImage bez sudo — patrz
"Wymagania systemowe" wyżej), a potem:

```bash
make all    # upewnij się, że output/step/model.step istnieje
make view   # albo: bash scripts/view.sh
```

`scripts/view.sh` wykrywa binarkę `freecad`/`FreeCAD` na `PATH` i otwiera w
niej `output/step/model.step`. Jeśli FreeCAD nie jest zainstalowany, skrypt
kończy się czytelnym błędem i podpowiedzią instalacji zamiast cichej
porażki.

## Uruchamianie walidacji

```bash
python -m cad_project.cli validate
```

Buduje model, mierzy go, uruchamia zestaw jawnych reguł walidacyjnych
(patrz [`src/cad_project/validation.py`](src/cad_project/validation.py)) i
zapisuje `output/reports/validation-report.json`. W przeciwieństwie do
`all`, `validate` **nie generuje na nowo** plików eksportu — sprawdza tylko,
czy już istnieją (uruchom `export`/`render`/`all` wcześniej).

Przykładowa (skrócona) struktura raportu:

```json
{
  "status": "passed",
  "model": {
    "solid_count": 1,
    "is_valid": true,
    "volume_mm3": 19568.67,
    "surface_area_mm2": 9515.88,
    "bounding_box_mm": { "x": 100.0, "y": 40.0, "z": 5.0 },
    "mass_kg": 0.0528
  },
  "features": {
    "hole_count": 4,
    "hole_diameter_mm": 5.0,
    "hole_positions_mm": [[42.0, 12.0], [42.0, -12.0], [-42.0, 12.0], [-42.0, -12.0]]
  },
  "topology_cross_check": { "note": "informational only, see specs/constraints.md" },
  "checks": [
    { "id": "bounding_box_length", "expected": 100.0, "actual": 100.0, "tolerance": 0.05, "status": "passed" }
  ],
  "exports": {
    "step": { "status": "passed", "path": "output/step/model.step" },
    "stl": { "status": "passed", "path": "output/stl/model.stl" },
    "preview": { "status": "passed", "path": "output/previews/model.png" }
  }
}
```

## Uruchamianie testów

```bash
pytest tests/ -v
# albo: make test
```

34 testy w czterech plikach:

* `tests/test_dimensions.py` — bounding box, pozycje/średnice otworów vs
  `specs/parameters.yaml`.
* `tests/test_geometry.py` — jedna bryła, poprawność bryły, objętość
  dodatnia, determinizm (dwa niezależne buildy dają identyczny wynik),
  czytelne błędy dla niepoprawnych parametrów.
* `tests/test_exports.py` — eksport STEP/STL do plików tymczasowych,
  determinizm STEP, render PNG, obsługa brakujących plików.
* `tests/test_spec_compliance.py` — zgodność `spec.md` ↔ `parameters.yaml`,
  zgodność stałych w `parameters.py` z YAML, struktura raportu JSON.

Lint:

```bash
ruff check src tests
# albo: make lint
```

Sprawdzanie typów (opcjonalne, `mypy` jest w zależnościach `dev`):

```bash
mypy src
# albo: make typecheck
```

## Drugi model: magnetyczny uchwyt na lufę karabinu

Pełna specyfikacja: [`specs/rifle-mount/spec.md`](specs/rifle-mount/spec.md)
(+ `parameters.yaml`, `constraints.md`, `decisions.md` w tym samym
katalogu). Uchwyt mocowany magnetycznie do metalowej ścianki sejfu,
przytrzymujący lufę karabinu w regulowanym zakresie 80–140 mm od ścianki.
Składa się z **dwóch fizycznie osobnych części** skręcanych ze sobą:

* **`base`** — kwadratowa płyta (60×60×4mm) z czterema magnesami
  neodymowymi Ø12×3mm i tuleją z gwintem wewnętrznym,
* **`arm`** — gwintowany trzpień + kołnierz oporowy + chwyt w kształcie
  litery U na lufę (prześwit 30mm, z rowkiem na wkładkę ochronną).

Gwint (skok 4mm, Ø25mm, kąt 29° jak ACME) jest **prawdziwą, drukowalną
geometrią** wygenerowaną biblioteką
[`bd_warehouse`](https://github.com/gumyr/bd_warehouse) — nie uproszczoną
reprezentacją. To sprawia, że budowanie tego modelu jest zauważalnie
wolniejsze niż uchwytu montażowego: **ok. 20–30 sekund** na pełny build
obu części (helikalny sweep w OCCT), zamiast <1s. Test suite dla tego
modelu (`tests/rifle_mount/`) używa współdzielonej, sesyjnej fixture
(`conftest.py`), żeby nie odbudowywać modelu bez potrzeby.

Komendy (własny CLI, ta sama składnia co uchwyt montażowy):

```bash
python -m cad_project.rifle_mount.cli build      # zbuduj obie części, brak eksportu
python -m cad_project.rifle_mount.cli export     # eksportuj STEP/STL obu części
python -m cad_project.rifle_mount.cli render     # podgląd PNG obu części
python -m cad_project.rifle_mount.cli validate   # zmierz + zwaliduj + raport
python -m cad_project.rifle_mount.cli all        # pełny pipeline
# albo: make rifle-build|rifle-validate|rifle-render|rifle-all|rifle-clean
```

Wyniki trafiają do osobnego drzewa `output/rifle-mount/` (nie kolidują z
plikami uchwytu montażowego):

```text
output/rifle-mount/step/base.step       output/rifle-mount/step/arm.step
output/rifle-mount/stl/base.stl         output/rifle-mount/stl/arm.stl
output/rifle-mount/previews/base.png    output/rifle-mount/previews/arm.png
output/rifle-mount/reports/validation-report.json
output/rifle-mount/logs/build.log
```

Podgląd w FreeCAD (opcjonalnie, patrz sekcja wyżej):

```bash
make rifle-view
# albo: bash scripts/view.sh output/rifle-mount/step/base.step output/rifle-mount/step/arm.step
```

Testy tylko dla tego modelu:

```bash
pytest tests/rifle_mount/ -v
```

**Ważne ograniczenia inżynieryjne tego modelu** (patrz
`specs/rifle-mount/constraints.md` po pełny opis):
* Walidacja geometrii **nie sprawdza** wytrzymałości mechanicznej (siły
  magnesów, naprężeń przy maksymalnym wysięgu 140mm) — to świadome
  ograniczenie zakresu v1, nie błąd.
* Chwyt U jest zamodelowany jako prosty prostokątny rowek (nie zaokrąglony
  łuk dopasowany do lufy) — decyzja opisana w `decisions.md`, nie zmienia
  wyprowadzenia zakresu regulacji.

## Struktura katalogów

```text
.
├── .claude/                # Konfiguracja i workflow Claude Code
│   ├── CLAUDE.md            #   zasady pracy (obowiązkowe kroki, zakazy)
│   ├── commands/            #   /generate-model /build-model /validate-model /review-model
│   └── skills/               #   spec-reader, cad-generator, cad-validator, cad-reviewer
├── specs/                  # ŹRÓDŁO PRAWDY dla wymagań (uchwyt montażowy)
│   ├── spec.md               #   specyfikacja czytelna dla człowieka + kopia YAML
│   ├── parameters.yaml       #   maszynowe źródło wartości (jedyne)
│   ├── constraints.md        #   ograniczenia inżynieryjne/procesowe
│   ├── decisions.md          #   log decyzji technicznych
│   └── rifle-mount/          #   ŹRÓDŁO PRAWDY dla uchwytu na lufę (ten sam wzorzec 4 plików)
├── src/cad_project/        # Kod
│   ├── parameters.py          #   wczytuje parameters.yaml, jedno źródło stałych
│   ├── model.py               #   geometria Build123d, build_model() -> ModelResult
│   ├── measurements.py        #   pomiary czystej geometrii (generyczne, współdzielone)
│   ├── validation.py          #   reguły walidacji + raport JSON
│   ├── exports.py             #   eksport STEP/STL (generyczne, współdzielone)
│   ├── rendering.py           #   podgląd PNG, headless matplotlib (generyczne, współdzielone)
│   ├── cli.py                 #   build/export/render/validate/all/clean
│   └── rifle_mount/           #   drugi model: parameters.py, model.py, validation.py, cli.py
├── tests/                  # pytest (+ tests/rifle_mount/ dla drugiego modelu)
├── scripts/                # setup.sh, build.sh, validate.sh, render.sh, view.sh, clean.sh
├── output/                 # Wyniki generowane automatycznie (ignorowane przez git poza .gitkeep)
│   ├── step/ stl/ previews/ reports/ logs/       (uchwyt montażowy)
│   └── rifle-mount/{step,stl,previews,reports,logs}/  (uchwyt na lufę)
├── docs/mcp-roadmap.md      # Plan na przyszłość dla serwera MCP
├── pyproject.toml, Makefile, .gitignore
└── README.md, CHANGELOG.md
```

## Workflow z Claude Code

1. Claude czyta `specs/spec.md`, `specs/parameters.yaml`,
   `specs/constraints.md`, `specs/decisions.md` (patrz `.claude/CLAUDE.md`).
2. Sprawdza kompletność/spójność specyfikacji (skill `spec-reader`) —
   jeśli coś jest niejasne albo sprzeczne, **zatrzymuje się i pyta**, zamiast
   zgadywać wartości inżynieryjne.
3. Generuje/aktualizuje `src/cad_project/model.py` (skill `cad-generator`),
   zachowując parametryczność i determinizm, bez dotykania `specs/`.
4. Uruchamia `pytest` i `python -m cad_project.cli validate`/`all` (skill
   `cad-validator`), analizuje `output/reports/validation-report.json`.
5. Jeśli walidacja nie przechodzi, poprawia **kod**, nie tolerancje ani
   oczekiwane wartości.
6. Na żądanie: niezależny przegląd zgodności specyfikacja → implementacja →
   wynik (skill `cad-reviewer`, polecenie `/review-model`).
7. Claude **nie wykonuje** `git commit`/`git tag`/`git push` samodzielnie —
   tylko na wyraźne polecenie użytkownika.

Sugerowany workflow Git (wykonywany przez człowieka, nie automatycznie):

```bash
git checkout -b feature/initial-bracket
git add specs src tests
git commit -m "feat: add parametric mounting bracket"
git tag v0.1.0
```

## Ograniczenia

* **Detekcja liczby/rozmiaru otworów** opiera się na jawnych metadanych
  (`ModelFeatures`) zwracanych przez `build_model()`, nie na w pełni
  niezawodnej analizie topologicznej — patrz
  [`specs/constraints.md`](specs/constraints.md). Dodatkowy, best-effort
  przegląd topologiczny (`topology_cross_check` w raporcie) jest jawnie
  oznaczony jako informacyjny, nie rozstrzygający.
* **Podgląd PNG** jest generowany bez VTK/GUI (tessellacja per-ściana +
  ręczne cieniowanie w matplotlib, headless backend `Agg`) — to nie jest
  fotorealistyczny render, tylko czytelny podgląd izometryczny na jasnym
  tle. Zobacz `specs/decisions.md` po uzasadnienie tego wyboru.
* **Parser `spec.md`** celowo nie używa wyrażeń regularnych po prozie
  Markdown — czyta wyłącznie jawnie odgraniczony blok ```` ```yaml ````.
  Jeśli ten blok zniknie albo się rozsynchronizuje z prozą tabeli,
  automatyczna kontrola zgodności to wykryje, ale **nie naprawi prozy
  automatycznie** (to celowe — naprawa treści czytelnej dla człowieka
  wymaga człowieka).
* Model referencyjny (uchwyt montażowy) zakłada dokładnie 4 otwory
  narożne — zmiana tej liczby wymaga świadomej zmiany
  `src/cad_project/model.py`, nie jest w pełni generyczna dla dowolnej
  liczby otworów (patrz `check_engineering_preconditions`).
* Brak własnego serwera MCP na tym etapie — patrz
  [`docs/mcp-roadmap.md`](docs/mcp-roadmap.md) po uzasadnienie i plan na
  przyszłość.
* **Uchwyt na lufę** (drugi model) buduje się ~20-30x wolniej niż uchwyt
  montażowy (prawdziwy gwint helikalny) i nie ma zweryfikowanej analizy
  wytrzymałościowej (siła magnesów, naprężenia przy max. wysięgu) — patrz
  [`specs/rifle-mount/constraints.md`](specs/rifle-mount/constraints.md).

## Troubleshooting

**`ModuleNotFoundError: No module named 'cad_project'`**
Środowisko nie jest aktywowane albo pakiet nie jest zainstalowany. Uruchom
`bash scripts/setup.sh` albo `pip install -e .` w `.venv`.

**`SpecificationError: Inconsistent specification: ...`**
To zamierzone zachowanie, nie bug — `parameters.py` wykrył sprzeczność w
`specs/parameters.yaml` (np. otwór nachodzący na zaokrąglenie) i celowo
zatrzymał generowanie geometrii zamiast zgadywać. Popraw wartości w
`specs/parameters.yaml` po konsultacji z osobą odpowiedzialną za
wymagania — nie w kodzie.

**Render PNG kończy się błędem, ale STEP/STL powstały**
To zgodne z projektem (błąd renderera jest odseparowany). Sprawdź
`exports.preview.error` w `output/reports/validation-report.json` oraz
`output/logs/build.log`. Częsta przyczyna: brak pakietu `matplotlib` w
środowisku — uruchom ponownie `scripts/setup.sh`.

**`ruff`/`pytest`: command not found**
Nie aktywowałeś `.venv`, albo zależności dev nie zostały zainstalowane —
`bash scripts/setup.sh` instaluje `.[dev]`, które zawiera oba narzędzia.

**Chcę zmienić wymiary modelu**
Edytuj **tylko** `specs/parameters.yaml` (i zaktualizuj czytelną tabelę
oraz blok ```` ```yaml ```` w `specs/spec.md`, żeby były zgodne — sprawdzi
to `tests/test_spec_compliance.py`). Nie edytuj wartości bezpośrednio w
`src/cad_project/parameters.py` ani `model.py`.

**Testy `pytest` są wolne / render trwa długo**
Renderowanie PNG (tessellacja + matplotlib) jest najwolniejszym krokiem
(rzędu ułamka sekundy dla tego modelu). Przy większych/złożonych modelach
rozważ zwiększenie `_TESSELLATION_TOLERANCE_MM` w
`src/cad_project/rendering.py` (kosztem dokładności podglądu — nie wpływa
to na eksport STEP/STL).
