---
description: Run the full pipeline (build, measure, validate, export STEP/STL, render PNG, report) and summarize the outcome.
---

Uruchom pełny pipeline i zaraportuj wynik.

1. Upewnij się, że środowisko jest gotowe (`.venv` istnieje; jeśli nie,
   poinformuj użytkownika, że trzeba najpierw uruchomić
   `bash scripts/setup.sh` / `make setup`).

2. Uruchom pipeline:
   ```bash
   python -m cad_project.cli all
   ```
   (równoważnie `make all` albo `bash scripts/build.sh`).

3. Odczytaj `output/reports/validation-report.json` i przedstaw:
   - ogólny `status` (`passed`/`failed`),
   - ścieżki do wygenerowanych plików:
     `output/step/model.step`, `output/stl/model.stl`,
     `output/previews/model.png`, `output/reports/validation-report.json`,
     `output/logs/build.log`,
   - listę wszystkich `checks`, które mają `status != "passed"` (jeśli są),
   - status sekcji `exports` (step/stl/preview) — pamiętaj, że błąd
     renderowania PNG (`preview`) nie oznacza porażki całego pipeline'u, ale
     musi być jawnie wskazany.

4. Nie edytuj ręcznie raportu JSON. Jeśli pipeline zakończył się błędem,
   przeczytaj `output/logs/build.log` i konkretny komunikat błędu zanim
   zaproponujesz poprawkę kodu.

5. Zakończ krótkim podsumowaniem: status końcowy, ścieżki plików, kod
   wyjścia procesu (0 = sukces, != 0 = porażka walidacji lub eksportu).
