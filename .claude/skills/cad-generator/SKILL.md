---
name: cad-generator
description: Generates or updates Build123d model code from a validated specification, preserving parametricity and determinism. Use only after spec-reader confirms the spec is READY.
---

# cad-generator

## Zakres odpowiedzialności

Generowanie i aktualizacja kodu Build123d w `src/cad_project/model.py` (i,
jeśli konieczne, akcesorów w `src/cad_project/parameters.py`) na podstawie
specyfikacji już potwierdzonej jako kompletnej przez `spec-reader`. Ten
skill **nie zmienia wymagań** — tłumaczy istniejącą, zwalidowaną
specyfikację na kod.

## Dane wejściowe

* Wynik `spec-reader` (status `READY`, mapowanie parametr → id).
* `specs/spec.md` sekcja "Geometria" (kolejność operacji).
* `specs/parameters.yaml` (wartości, poprzez `src/cad_project/parameters.py`
  — nigdy wpisywane bezpośrednio w kodzie).
* Istniejący `src/cad_project/model.py`, jeśli to aktualizacja, nie nowy
  model.

## Wynik

Zmieniony/nowy `src/cad_project/model.py` (i ewentualnie nowe stałe w
`parameters.py`), który:

* importuje wszystkie wymiary z `cad_project.parameters` — zero
  zahardkodowanych liczb,
* buduje model deterministycznie (ten sam wynik przy każdym wywołaniu),
* nie eksportuje ani nie renderuje niczego przy imporcie modułu,
* zwraca `ModelResult(part: Part, features: ModelFeatures)` z jawnymi,
  zweryfikowalnymi metadanymi cech (liczba otworów, średnica, pozycje itd.),
* jest podzielony na czytelne kroki (komentarze/nazwy zmiennych), ale **bez**
  wydzielania zagnieżdżonych builderów (`BuildSketch`, `BuildLine`, ...) do
  osobnych funkcji przyjmujących builder jako argument — Build123d wymaga,
  by dziecko i rodzic (`BuildPart`) były otwarte w tej samej ramce Pythona
  (patrz komentarz w `model.py::build_model` i `specs/decisions.md`).

## Kroki działania

1. Potwierdź, że masz aktualne wartości parametrów (`from cad_project import
   parameters as p`).
2. Zaplanuj kolejność operacji dokładnie tak, jak opisano w
   `specs/spec.md` ("Geometria") — nie zmieniaj kolejności bez uzasadnienia
   (kolejność wpływa na to, względem czego liczone są pozycje otworów).
3. Zaimplementuj geometrię z użyciem Build123d (`BuildPart`, `Box`,
   `fillet`, `BuildSketch`, `Locations`, `Circle`, `extrude`), inline w
   jednej funkcji `build_model()`.
4. Zbuduj `ModelFeatures` z wartościami faktycznie użytymi do konstrukcji
   (nie przepisuj ślepo stałych z `parameters.py` — użyj tych samych
   zmiennych, które poszły do wywołań Build123d).
5. Uruchom `pytest tests/ -v` i napraw implementację, jeśli coś nie
   przechodzi.

## Ograniczenia

* Nie ma dostępu do informacji o tym, czy specyfikacja jest kompletna —
  zakłada, że `spec-reader` już to potwierdził. Jeśli podczas
  implementacji odkryje sprzeczność, której `spec-reader` nie wyłapał,
  zatrzymuje się i zgłasza problem zamiast zgadywać.
* Nie generuje eksportu STEP/STL/PNG — to `cad-validator` i
  `src/cad_project/exports.py`/`rendering.py`.

## Zabronione zachowania

* Nie zmienia `specs/parameters.yaml` ani `specs/spec.md`.
* Nie dodaje drugiego miejsca z zahardkodowaną wartością wymiaru.
* Nie wprowadza niedeterminizmu (losowości, zależności od czasu, kolejności
  iteracji zbiorów bez sortowania) do geometrii.
* Nie "naprawia" nieprzechodzących testów przez rozluźnienie asercji.

## Kryteria ukończenia

`build_model()` uruchamia się bez błędu, zwraca dokładnie jedną bryłę
zgodną z bounding boxem ze specyfikacji, `pytest tests/` przechodzi, a
żadna wartość liczbowa nie została wpisana bezpośrednio w `model.py` poza
przez import z `parameters.py`.
