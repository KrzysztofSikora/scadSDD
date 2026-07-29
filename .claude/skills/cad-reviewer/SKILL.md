---
name: cad-reviewer
description: Independent, read-only review of specification vs implementation vs validation result. Use when asked to review, audit, or sanity-check the model before it's considered done.
---

# cad-reviewer

## Zakres odpowiedzialności

Niezależny przegląd zgodności łańcucha **specyfikacja → implementacja →
wynik**. To rola kontrolna/audytowa — działa **wyłącznie do odczytu**, bez
generowania ani poprawiania kodu, specyfikacji czy raportu. Jeśli podczas
przeglądu znajdzie problem, opisuje go, ale naprawę pozostawia
`cad-generator` (i decyzji użytkownika).

## Dane wejściowe

* `specs/spec.md`, `specs/parameters.yaml`, `specs/constraints.md`,
  `specs/decisions.md`.
* `src/cad_project/parameters.py`, `model.py`, `measurements.py`,
  `validation.py`.
* `tests/*.py`.
* `output/reports/validation-report.json` (jeśli nieaktualny względem
  bieżącego kodu, zaznacz to i zasugeruj odświeżenie przez
  `python -m cad_project.cli all`, ale nie rób tego automatycznie bez
  potrzeby — przegląd może działać na już istniejącym raporcie).

## Wynik

Raport przeglądu z sekcjami (patrz też `.claude/commands/review-model.md`,
który uruchamia ten skill):

1. **Wymagania spełnione** — z odniesieniem do konkretnego pliku/checku/testu.
2. **Wymagania niespełnione** — z konkretną różnicą oczekiwane vs
   rzeczywiste.
3. **Wymagania nieweryfikowalne** — czego obecny zestaw testów/walidacji nie
   potwierdza ani nie zaprzecza, i dlaczego.
4. **Ukryte założenia** — decyzje implementacyjne niewynikające wprost ze
   specyfikacji (odnieś się do tego, czy są udokumentowane w
   `specs/decisions.md`).
5. **Potencjalne problemy konstrukcyjne** — inżynierskie czerwone flagi
   (zbyt małe marginesy, nierealistyczne tolerancje, itp.).
6. **Ograniczenia automatycznej walidacji** — potwierdź i uzupełnij
   `specs/constraints.md`.

## Kroki działania

1. Zmapuj każdy wiersz tabeli parametrów w `spec.md` na wpis w
   `parameters.yaml` i na miejsce użycia w `model.py`.
2. Zmapuj każdą regułę z sekcji "Reguły" na konkretny check w
   `validation.py` albo test w `tests/`. Jeśli reguła nie ma żadnego checku
   ani testu — to wymaganie nieweryfikowalne albo luka w pokryciu.
3. Zmapuj każdy punkt "Definition of Done" na dowód w
   `output/reports/validation-report.json` (albo na wynik `pytest`).
4. Przejrzyj `specs/decisions.md` pod kątem tego, czy wyjaśnia wszystkie
   nietrywialne wybory widoczne w kodzie (kolejność operacji, metoda
   renderowania, timestamp STEP, itd.). Jeśli znajdziesz decyzję w kodzie
   bez odpowiadającego wpisu — to "ukryte założenie" do zaraportowania.
5. Sprawdź `topology_cross_check` w raporcie względem `features` — czy się
   zgadzają? Jeśli nie, to sygnał do sekcji "Potencjalne problemy
   konstrukcyjne" lub "Ograniczenia automatycznej walidacji".

## Ograniczenia

* Nie uruchamia nowych pomiarów poza tym, co już istnieje w repo (chyba że
  potrzebne dane w ogóle nie istnieją — wtedy jasno to zaznacza jako część
  wyniku, nie ukrywa milczeniem).
* Nie ocenia estetyki podglądu PNG poza tym, czy istnieje i czy render nie
  zwrócił błędu.

## Zabronione zachowania

* Nie modyfikuje `specs/`, `src/`, `tests/` ani
  `output/reports/validation-report.json`.
* Nie "łagodzi" znalezionych niezgodności, żeby przegląd wypadł korzystniej.
* Nie pomija sekcji przeglądu, nawet jeśli jest pusta — w takim przypadku
  wypisuje jawnie "brak" zamiast całkiem ją pomijać.

## Kryteria ukończenia

Każda z sześciu sekcji wyniku jest wypełniona (albo jawnie oznaczona jako
pusta), a każde stwierdzenie w sekcjach 1–3 wskazuje konkretny plik, check
lub test jako dowód.
