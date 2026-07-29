---
description: Run validation, read the JSON report, and summarize discrepancies without touching the spec.
---

Uruchom walidację i przedstaw wynik — **nie poprawiaj automatycznie
specyfikacji**, nawet jeśli walidacja nie przechodzi.

1. Uruchom:
   ```bash
   python -m cad_project.cli validate
   ```
   (uwaga: ta komenda sprawdza *istnienie* wcześniej wygenerowanych plików
   STEP/STL/PNG, nie generuje ich na nowo — jeśli chcesz pełny przebieg,
   użyj `/build-model` albo `python -m cad_project.cli all`).

2. Odczytaj `output/reports/validation-report.json`.

3. Podsumuj:
   - ogólny `status`,
   - dla każdego checku ze `status: "failed"`: `id`, `description`,
     `expected` vs `actual`, `tolerance`, `message`,
   - sekcję `topology_cross_check` — jasno zaznacz, że to wynik
     informacyjny, nie rozstrzygający (patrz `specs/constraints.md`),
   - sekcję `exports` (step/stl/preview) i ewentualne `warnings`.

4. Jeśli walidacja nie przechodzi:
   - Zdiagnozuj, czy problem jest w **kodzie** (`src/cad_project/model.py`
     nie realizuje specyfikacji poprawnie) czy w **specyfikacji**
     (wymaganie jest niejasne/sprzeczne).
   - Jeśli to kod: zaproponuj konkretną poprawkę w `src/`, nie w `specs/`.
   - Jeśli to specyfikacja: opisz sprzeczność użytkownikowi i zapytaj, jak
     ją rozwiązać. Nie zmieniaj `specs/parameters.yaml` ani `specs/spec.md`
     samodzielnie.
   - Nigdy nie podnoś tolerancji ani nie zmieniaj oczekiwanych wartości
     tylko po to, żeby raport pokazał `"passed"`.

5. Nie edytuj `output/reports/validation-report.json` ręcznie — to plik
   generowany automatycznie.
