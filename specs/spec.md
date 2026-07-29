# Specyfikacja modelu CAD: Uchwyt montażowy (Mounting Bracket)

> **Ten plik jest źródłem prawdy dla wymagań.** Claude (ani żaden automat) nie
> może zmieniać wartości, tolerancji ani reguł w tym pliku bez wyraźnego
> polecenia człowieka. Zobacz `.claude/CLAUDE.md` oraz `specs/constraints.md`.

## Metadane

| Pole                  | Wartość            |
|-----------------------|---------------------|
| Nazwa projektu        | Mounting Bracket    |
| Identyfikator modelu  | `bracket-001`       |
| Wersja specyfikacji   | `1.0.0`             |
| Jednostki             | milimetry (mm)      |

## Parametry

Poniższa tabela jest zapisem **czytelnym dla człowieka**. Ostatecznym,
maszynowym źródłem prawdy dla wszystkich wartości liczbowych jest plik
[`specs/parameters.yaml`](parameters.yaml). Fragment YAML poniżej jest
dosłowną kopią tamtego pliku i służy do automatycznej weryfikacji zgodności
(`tests/test_spec_compliance.py` parsuje oba pliki przez `yaml.safe_load` i
porównuje strukturalnie — bez żadnych wyrażeń regularnych na tekście
Markdown).

| Nazwa parametru                              | ID techniczne        | Wartość   | Jednostka | Tolerancja | Opis |
|-----------------------------------------------|----------------------|-----------|-----------|------------|------|
| Długość podstawy                              | `length`             | 100.0     | mm        | ±0.05      | Całkowita długość podstawy wzdłuż osi X |
| Szerokość podstawy                            | `width`              | 40.0      | mm        | ±0.05      | Całkowita szerokość podstawy wzdłuż osi Y |
| Grubość podstawy                              | `base_thickness`     | 5.0       | mm        | ±0.05      | Grubość płyty bazowej wzdłuż osi Z |
| Liczba otworów montażowych                    | `hole_count`         | 4         | szt.      | 0          | Po jednym otworze w każdym rogu |
| Średnica otworów montażowych                  | `hole_diameter`      | 5.0       | mm        | ±0.02      | Średnica każdego otworu |
| Odsunięcie środka otworu od krawędzi          | `hole_edge_offset`   | 8.0       | mm        | ±0.05      | Liczone niezależnie wzdłuż X i Y |
| Promień zaokrąglenia krawędzi zewnętrznych    | `fillet_radius`      | 3.0       | mm        | ±0.05      | Cztery pionowe krawędzie narożników |
| Gęstość materiału (opcjonalna)                | `material_density`   | 2.70e-6   | kg/mm³    | —          | Aluminium 6061, tylko do obliczenia masy |

### Fragment maszynowy (kopia `specs/parameters.yaml`)

```yaml
project:
  name: "Mounting Bracket"
  model_id: "bracket-001"
  spec_version: "1.0.0"
  units: "mm"

parameters:
  - id: length
    name: "Długość podstawy"
    value: 100.0
    unit: mm
    tolerance: 0.05
    description: >
      Całkowita długość podstawy uchwytu wzdłuż osi X (przed zaokrągleniem
      krawędzi zewnętrznych).

  - id: width
    name: "Szerokość podstawy"
    value: 40.0
    unit: mm
    tolerance: 0.05
    description: >
      Całkowita szerokość podstawy uchwytu wzdłuż osi Y (przed zaokrągleniem
      krawędzi zewnętrznych).

  - id: base_thickness
    name: "Grubość podstawy"
    value: 5.0
    unit: mm
    tolerance: 0.05
    description: Grubość płyty bazowej wzdłuż osi Z.

  - id: hole_count
    name: "Liczba otworów montażowych"
    value: 4
    unit: count
    tolerance: 0
    description: Liczba otworów montażowych, po jednym w każdym rogu podstawy.

  - id: hole_diameter
    name: "Średnica otworów montażowych"
    value: 5.0
    unit: mm
    tolerance: 0.02
    description: Średnica każdego z czterech otworów montażowych.

  - id: hole_edge_offset
    name: "Odsunięcie środka otworu od krawędzi"
    value: 8.0
    unit: mm
    tolerance: 0.05
    description: >
      Odległość od środka otworu montażowego do najbliższej krawędzi podstawy
      (mierzona niezależnie wzdłuż osi X i osi Y, przed zaokrągleniem
      krawędzi).

  - id: fillet_radius
    name: "Promień zaokrąglenia krawędzi zewnętrznych"
    value: 3.0
    unit: mm
    tolerance: 0.05
    description: >
      Promień zaokrąglenia czterech pionowych, zewnętrznych krawędzi
      podstawy (narożniki).

  - id: material_density
    name: "Gęstość materiału (opcjonalna, do obliczenia masy)"
    value: 2.70e-6
    unit: kg/mm3
    tolerance: 0
    description: >
      Domyślna gęstość materiału (aluminium 6061) używana wyłącznie do
      opcjonalnego obliczenia masy w raporcie pomiarowym. Nie jest wymiarem
      geometrycznym i nie podlega walidacji bounding-boxa.
```

## Geometria

Kolejność operacji (deterministyczna, patrz `src/cad_project/model.py`):

1. **Bryła bazowa**: prostopadłościan o wymiarach `length` × `width` ×
   `base_thickness`, wyśrodkowany w płaszczyźnie XY, symetryczny względem
   początku układu współrzędnych. Oś X = długość, oś Y = szerokość, oś Z =
   grubość.
2. **Zaokrąglenie krawędzi zewnętrznych**: fillet o promieniu `fillet_radius`
   nałożony na cztery pionowe krawędzie (równoległe do osi Z) w narożnikach
   podstawy. Zaokrąglenie nie zmienia bounding boxa modelu (jest styczne do
   obu ścian bocznych w każdym narożniku).
3. **Otwory montażowe**: cztery otwory przelotowe o średnicy `hole_diameter`,
   przechodzące przez całą grubość podstawy (wzdłuż osi Z), o środkach
   umieszczonych symetrycznie w narożnikach:
   - `(+(length/2 − hole_edge_offset), +(width/2 − hole_edge_offset))`
   - `(+(length/2 − hole_edge_offset), −(width/2 − hole_edge_offset))`
   - `(−(length/2 − hole_edge_offset), +(width/2 − hole_edge_offset))`
   - `(−(length/2 − hole_edge_offset), −(width/2 − hole_edge_offset))`

   Otwory są wycinane (boolean subtract) **po** zaokrągleniu krawędzi, aby
   ich pozycja była liczona względem oryginalnych krawędzi podstawy, a nie
   względem zaokrąglonego obrysu.

## Reguły

* Wszystkie otwory muszą przechodzić przez całą podstawę (na wylot, brak
  otworów ślepych).
* Otwory muszą być rozmieszczone symetrycznie względem obu osi (X i Y)
  środka podstawy.
* Model ma być pojedynczą bryłą (`solid_count == 1`).
* Model nie może zawierać ujemnej objętości ani pustej geometrii
  (`volume_mm3 > 0`, `is_valid == True`).
* Odsunięcie otworu od krawędzi musi być większe niż promień zaokrąglenia,
  tak aby otwory nie przecinały zaokrąglonych narożników
  (`hole_edge_offset − hole_diameter/2 > 0` i otwór musi pozostać w całości
  wewnątrz płaskiego obszaru podstawy, poza strefą zaokrąglenia).
* Zmiana dowolnego parametru w `specs/parameters.yaml` musi być odzwierciedlona
  w tabeli powyżej (patrz `tests/test_spec_compliance.py`).

## Oczekiwane wyniki

Po uruchomieniu pełnego pipeline'u (`python -m cad_project.cli all` albo
`make all`) muszą powstać:

* `output/step/model.step` — model STEP,
* `output/stl/model.stl` — model STL (tesselacja trójkątna),
* `output/previews/model.png` — podgląd PNG w rzucie izometrycznym,
* `output/reports/validation-report.json` — raport JSON z pomiarami i
  wynikiem walidacji,
* `output/logs/build.log` — log wykonania.

## Definition of Done

Model uznaje się za gotowy, gdy spełnione są **wszystkie** poniższe warunki:

- [ ] kod uruchamia się bez błędów (`python -m cad_project.cli build`),
- [ ] powstaje dokładnie jedna bryła (`solid_count == 1`),
- [ ] bounding box jest zgodny z wymiarami (`100.0 × 40.0 × 5.0` mm, w
      granicach tolerancji z tabeli parametrów),
- [ ] liczba otworów jest zgodna ze specyfikacją (4),
- [ ] średnice otworów są zgodne ze specyfikacją (5.0 mm ± 0.02 mm),
- [ ] eksport STEP działa (plik istnieje i jest niepusty),
- [ ] eksport STL działa (plik istnieje i jest niepusty),
- [ ] podgląd PNG istnieje (lub błąd renderera jest jawnie i osobno
      zaraportowany, bez blokowania eksportu STEP/STL),
- [ ] wszystkie testy `pytest` przechodzą,
- [ ] raport walidacji (`output/reports/validation-report.json`) ma status
      `"passed"`.
