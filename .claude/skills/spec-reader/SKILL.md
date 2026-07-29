---
name: spec-reader
description: Reads and analyzes the CAD specification (specs/), detects gaps and contradictions, and maps requirements to technical parameter ids. Use before generating or reviewing any model code.
---

# spec-reader

## Zakres odpowiedzialności

Analiza specyfikacji CAD w `specs/` — **wyłącznie odczyt i analiza**, bez
generowania geometrii czy modyfikowania jakiegokolwiek pliku. Ten skill
odpowiada na pytanie: "czy specyfikacja jest kompletna, spójna i gotowa do
implementacji?"

## Dane wejściowe

* `specs/spec.md` — metadane, tabela parametrów, geometria, reguły,
  oczekiwane wyniki, Definition of Done.
* `specs/parameters.yaml` — maszynowe źródło wartości parametrów.
* `specs/constraints.md` — ograniczenia inżynieryjne i procesowe.
* `specs/decisions.md` — historia decyzji (kontekst, nie wymagania same w
  sobie).
* Opcjonalnie: bieżący stan `src/cad_project/parameters.py` i `model.py`,
  jeśli zadanie dotyczy zmiany istniejącego modelu.

## Wynik

Ustrukturyzowana analiza zawierająca:

1. **Mapowanie wymagań → identyfikatory techniczne.** Dla każdego parametru
   z tabeli w `spec.md`, potwierdź odpowiadający wpis w `parameters.yaml`
   (pole `id`) i odwrotnie. Wypisz wszelkie rozbieżności.
2. **Braki.** Parametry lub reguły geometryczne wspomniane w opisie
   ("Geometria", "Reguły"), które nie mają jawnej wartości liczbowej,
   tolerancji albo jednostki.
3. **Sprzeczności.** Kombinacje wartości, które się wzajemnie wykluczają
   (np. `hole_edge_offset - hole_diameter/2 <= fillet_radius`, otwory
   wychodzące poza podstawę, ujemne wymiary).
4. **Status**: `READY` (można bezpiecznie generować kod) albo `BLOCKED`
   (lista konkretnych pytań do użytkownika, jedno pytanie na jedną
   niejednoznaczność).

## Kroki działania

1. Wczytaj `specs/parameters.yaml` — zweryfikuj, że każdy wpis ma pola:
   `id`, `name`, `value`, `unit`, `tolerance`, `description`.
2. Wczytaj blok ```yaml w `specs/spec.md` (sekcja "Parametry") — porównaj
   strukturalnie z `parameters.yaml` (tak jak robi to
   `tests/test_spec_compliance.py` — parser YAML, nigdy regex po Markdownie
   prozy).
3. Przejdź przez sekcję "Geometria" i "Reguły" w `spec.md`, i dla każdego
   zdania sprawdź, czy odnosi się do parametru, który istnieje w
   `parameters.yaml`.
4. Sprawdź reguły z `specs/constraints.md` pod kątem numerycznej spójności
   z aktualnymi wartościami w `parameters.yaml` (możesz to policzyć ręcznie
   albo uruchomić `python -c "from cad_project.parameters import
   check_engineering_preconditions; check_engineering_preconditions()"`).
5. Zwróć wynik w formacie z sekcji "Wynik" powyżej.

## Ograniczenia

* Nie ocenia jakości implementacji Build123d — tylko specyfikację.
* Nie wykonuje Build123d ani nie mierzy geometrii.
* Nie ocenia, czy testy pytest są poprawne — to rola `cad-validator`.

## Zabronione zachowania

* Nie zgaduj brakującej wartości inżynieryjnej i nie proponuj jej jako
  "rozsądnego domyślnego" bez wyraźnego oznaczenia, że to propozycja do
  zatwierdzenia przez człowieka, nie fakt ze specyfikacji.
* Nie edytuj `specs/*` w ramach tego skilla.
* Nie używaj kruchych wyrażeń regularnych do parsowania prozy Markdown —
  wyciągaj dane wyłącznie ze strukturalnych bloków (YAML/JSON) parserem
  dedykowanym (`yaml.safe_load`).

## Kryteria ukończenia

Skill uznaje się za ukończony, gdy zwrócono jednoznaczny status (`READY`
albo `BLOCKED` z konkretną listą pytań) i pełne mapowanie parametr → id
techniczne, bez żadnej niewyjaśnionej rozbieżności między `spec.md` a
`parameters.yaml`.
