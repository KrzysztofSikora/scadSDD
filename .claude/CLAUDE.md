# CLAUDE.md — instrukcje pracy dla Claude Code w tym repozytorium

Ten projekt implementuje **Spec-Driven Development dla CAD**: parametryczne
modele Build123d generowane i walidowane na podstawie specyfikacji w
`specs/`. Przeczytaj to w całości przed jakąkolwiek zmianą kodu.

## Modele w tym repozytorium

To repozytorium hostuje **więcej niż jeden niezależny model**, każdy ze
swoją własną specyfikacją, kodem, testami i CLI — żaden nie modyfikuje
plików drugiego:

| Model | Specyfikacja | Kod | CLI |
|---|---|---|---|
| Uchwyt montażowy (`bracket-001`) | `specs/spec.md`, `specs/parameters.yaml` | `src/cad_project/{parameters,model}.py` | `python -m cad_project.cli` |
| Magnetyczny uchwyt na lufę (`magnetic-rifle-mount-001`) | `specs/rifle-mount/spec.md`, `specs/rifle-mount/parameters.yaml` | `src/cad_project/rifle_mount/{parameters,model}.py` | `python -m cad_project.rifle_mount.cli` |
| Doniczka premium z samonawadnianiem (`self-watering-planter-001`) | `specs/planter/spec.md`, `specs/planter/parameters.yaml` | `src/cad_project/planter/{parameters,model}.py` | `python -m cad_project.planter.cli` |

Moduły `measurements.py`, `exports.py`, `rendering.py` w
`src/cad_project/` są **generyczne** (biorą dowolny Build123d `Part`) i są
reużywane przez oba modele — nie duplikuj ich przy dodawaniu kolejnego
modelu.

Gdy pracujesz nad jednym modelem, zawsze najpierw ustal, którego dotyczy
zadanie, i czytaj **tylko jego** `specs/` — nie mieszaj wymagań między
modelami.

## Źródło prawdy

Dla każdego modelu z osobna:

* **`spec.md`** — czytelna dla ludzi specyfikacja: metadane, tabela
  parametrów, geometria, reguły, oczekiwane wyniki, Definition of Done.
* **`parameters.yaml`** — jedyne maszynowe źródło wartości liczbowych.
  Odpowiedni `parameters.py` wczytuje ten plik bezpośrednio; nic innego
  w kodzie nie powinno powtarzać tych liczb.
* **`constraints.md`** — ograniczenia inżynieryjne i procesowe, w tym
  znane ograniczenia automatycznej walidacji.
* **`decisions.md`** — log decyzji technicznych z uzasadnieniami.

Te pliki są źródłem prawdy dla wymagań, wymiarów i tolerancji.
**Nie zmieniaj ich wartości, aby "przepchnąć" testy lub walidację.**

## Tryb pracy (obowiązkowy proces)

1. Przeczytaj `specs/spec.md`.
2. Przeczytaj `specs/constraints.md` i `specs/decisions.md`.
3. Sprawdź spójność wymagań (czy parametry się nie wykluczają, czy
   `specs/parameters.yaml` i tabela w `specs/spec.md` są zgodne — patrz
   `tests/test_spec_compliance.py`).
4. Przed zmianą kodu przedstaw krótki plan (co i dlaczego zamierzasz
   zmienić).
5. Zmieniaj wyłącznie pliki potrzebne do zadania.
6. Nie zmieniaj plików w `specs/` bez wyraźnego polecenia użytkownika.
7. Uruchom testy i walidację (`make test`, `make all` albo
   `python -m cad_project.cli validate` / `all`).
8. Przeanalizuj raport JSON (`output/reports/validation-report.json`) —
   pole `status`, listę `checks`, sekcję `exports`.
9. Jeśli wynik nie spełnia specyfikacji, popraw **kod** (`src/`), nie
   specyfikację ani tolerancje.
10. Nie wykonuj `git commit` (ani `git tag`, `git push`) bez wyraźnego
    polecenia użytkownika.
11. Nie usuwaj istniejących funkcji bez uzasadnienia — jeśli coś wydaje się
    zbędne, zapytaj albo wyjaśnij dlaczego w opisie zmiany.
12. Nie ukrywaj błędów ani nie osłabiaj testów, żeby "przeszły na zielono".
13. Nie zwiększaj tolerancji w `specs/parameters.yaml` tylko po to, żeby
    walidacja przeszła.
14. Nie wpisuj oczekiwanych wartości jako rzekomo zmierzonych — wartości w
    `output/reports/validation-report.json` muszą pochodzić z rzeczywistego
    pomiaru (`src/cad_project/measurements.py`), nigdy z ręcznej edycji.
15. Nie modyfikuj raportu walidacji ręcznie — jest on generowany wyłącznie
    przez `src/cad_project/validation.py` i CLI.

## Gdy specyfikacja jest niepełna lub sprzeczna

Zatrzymaj się. Nie zgaduj wartości inżynieryjnych. Zamiast tego:

1. Zatrzymaj generowanie geometrii (nie twórz "tymczasowego" kodu z
   wymyśloną wartością).
2. Opisz problem użytkownikowi wprost.
3. Wskaż dokładnie, którego parametru/reguły brakuje albo która para
   wymagań się wyklucza (np. konkretne pola w `specs/parameters.yaml` albo
   konkretny punkt w `specs/spec.md`).
4. Zaproponuj pytanie do użytkownika zamiast domyślnej wartości.

Przykład wzorca w kodzie: `cad_project.parameters.SpecificationError` i
`check_engineering_preconditions()` w `src/cad_project/parameters.py` —
mechanizm, który celowo przerywa budowę modelu zamiast "naprawiać" sprzeczne
parametry.

## Architektura (gdzie co jest)

| Warstwa                  | Uchwyt montażowy                        | Uchwyt na lufę (rifle_mount)                     | Doniczka (planter)                              |
|---------------------------|-------------------------------------------|----------------------------------------------------|---------------------------------------------------|
| Parametry (jedno źródło)  | `src/cad_project/parameters.py`            | `src/cad_project/rifle_mount/parameters.py`         | `src/cad_project/planter/parameters.py`            |
| Geometria (Build123d)     | `src/cad_project/model.py`                 | `src/cad_project/rifle_mount/model.py`              | `src/cad_project/planter/model.py`                 |
| Walidacja                 | `src/cad_project/validation.py`            | `src/cad_project/rifle_mount/validation.py`         | `src/cad_project/planter/validation.py`            |
| CLI                       | `src/cad_project/cli.py`                   | `src/cad_project/rifle_mount/cli.py`                | `src/cad_project/planter/cli.py`                   |
| Pomiary/Eksport/Podgląd   | `measurements.py`/`exports.py`/`rendering.py` (generyczne, **współdzielone** przez wszystkie modele) |||

`build_model()` w każdym `model.py` **nigdy** nie eksportuje ani nie
renderuje — zwraca wyłącznie metadane cech (`ModelResult`/`RifleMountResult`/
`PlanterResult` + `*Features`). Eksport/render są zawsze jawne (CLI albo
skrypt), nigdy efektem ubocznym importu modułu.

Model uchwytu na lufę ma **dwie fizycznie osobne części** (base + arm) —
`build_model()` zwraca oba `Part`y razem z osobnymi metadanymi cech; patrz
`specs/rifle-mount/constraints.md`. Model doniczki też ma **dwie fizycznie
osobne części** (insert + reservoir) — patrz `specs/planter/constraints.md`.
W doniczce tylko jeden fragment geometrii (`_carve_wall_pattern()` w
`model.py`, parametry `pattern_*`) jest przeznaczony do wymiany między
przyszłymi wariantami serii — reszta wymiarów ma pozostać identyczna, patrz
`specs/planter/decisions.md` ("Architektura wymiennego wzoru").

## Uruchamianie

Uchwyt montażowy:
```bash
source .venv/bin/activate
python -m cad_project.cli build      # zbuduj model, brak eksportu
python -m cad_project.cli export     # zbuduj + eksportuj STEP/STL
python -m cad_project.cli render     # zbuduj + wyrenderuj podgląd PNG
python -m cad_project.cli validate   # zbuduj + zmierz + zwaliduj + zapisz raport
python -m cad_project.cli all        # pełny pipeline
```

Uchwyt na lufę (te same komendy, osobny CLI, wolniejszy build — patrz niżej):
```bash
python -m cad_project.rifle_mount.cli all
```

Doniczka (te same komendy, osobny CLI, szybki build jak uchwyt montażowy):
```bash
python -m cad_project.planter.cli all
```

```bash
pytest tests/ -v
ruff check src tests
mypy src
```

Albo równoważnie `make build|validate|test|lint|typecheck|render|all|clean`
oraz `make rifle-build|rifle-validate|rifle-render|rifle-all|rifle-clean`
oraz `make planter-build|planter-validate|planter-render|planter-all|planter-clean`.

**Uwaga o wydajności**: model uchwytu na lufę używa prawdziwego,
drukowalnego gwintu (`bd_warehouse`, sweep helikalny w OCCT) — pełne
budowanie obu części zajmuje ~20-30s (zamiast <1s dla uchwytu
montażowego). Testy w `tests/rifle_mount/` używają współdzielonej,
sesyjnej fixture (`conftest.py`), żeby nie odbudowywać modelu bez
potrzeby — nie dodawaj kolejnych pełnych buildów w nowych testach bez
wyraźnej potrzeby.

## Zasady jakości kodu

* Typuj funkcje publiczne, używaj `@dataclass(frozen=True)` dla struktur
  danych (patrz `ModelFeatures`, `ModelResult`, `Measurements`,
  `ValidationCheck`).
* Build123d: pamiętaj, że zagnieżdżone buildery (`BuildPart`, `BuildSketch`,
  ...) muszą być otwierane w tej samej ramce Pythona co ich rodzic — nie
  wydzielaj `with BuildSketch(...):` do osobnej funkcji przyjmującej builder
  jako argument (patrz komentarz w `model.py::build_model`).
* Błąd renderowania PNG nigdy nie blokuje eksportu STEP/STL — musi być
  przechwycony i zaraportowany osobno (patrz `RenderOutcome` w
  `rendering.py`).
* Nie porównuj binarnej zawartości STEP w testach (metadane mogą się różnić
  mimo identycznej geometrii) — porównuj bounding box, objętość, powierzchnię,
  liczbę brył i `ModelFeatures`.
* Liczba otworów w raporcie pochodzi z jawnych metadanych `ModelFeatures`
  zwracanych przez `build_model()`, nie z domysłu topologicznego — patrz
  `specs/constraints.md`.
