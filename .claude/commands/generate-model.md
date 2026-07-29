---
description: Read the spec, check it's complete, then generate/update the Build123d model code (never the spec).
---

Wykonaj poniższe kroki po kolei, w tej kolejności. Nie pomijaj kroków
weryfikacyjnych, nawet jeśli zadanie wygląda na proste.

1. **Przeczytaj specyfikację.**
   - `specs/spec.md` (metadane, parametry, geometria, reguły, Definition of
     Done),
   - `specs/parameters.yaml` (maszynowe źródło wartości),
   - `specs/constraints.md` i `specs/decisions.md`.

2. **Sprawdź kompletność i spójność.**
   - Czy każdy parametr użyty w opisie geometrii ma odpowiadający wpis w
     `specs/parameters.yaml` (id, wartość, jednostka, tolerancja, opis)?
   - Czy tabela w `specs/spec.md` (blok ```yaml) zgadza się z
     `specs/parameters.yaml`? (`tests/test_spec_compliance.py` to
     automatyzuje — możesz go uruchomić.)
   - Czy reguły geometryczne w `specs/spec.md` ("Reguły") nie wykluczają się
     wzajemnie (np. `hole_edge_offset` vs `fillet_radius` vs wymiary bazy)?
   - Jeśli znajdziesz brak albo sprzeczność: **zatrzymaj się**, opisz
     problem, wskaż dokładnie brakujący/sprzeczny element, zaproponuj
     pytanie do użytkownika. Nie zgaduj wartości.

3. **Zaktualizuj lub wygeneruj kod modelu.**
   - Zmieniaj tylko `src/cad_project/model.py` (i, jeśli naprawdę potrzeba,
     `src/cad_project/parameters.py` dla nowych akcesorów — ale nigdy
     `specs/parameters.yaml` bez wyraźnego polecenia).
   - Zachowaj: jedno źródło parametrów, determinizm, brak eksportu przy
     imporcie, zwracanie `ModelResult(part, features)` z jawnymi metadanymi
     cech.
   - Pamiętaj o ograniczeniu Build123d: zagnieżdżone buildery muszą być w tej
     samej ramce Pythona co rodzic (nie wydzielaj `BuildSketch` do osobnej
     funkcji przyjmującej builder).

4. **Nie zmieniaj specyfikacji.** Jeśli podczas implementacji odkryjesz, że
   specyfikacja powinna się zmienić (np. brakujący parametr), zapytaj
   użytkownika zamiast edytować `specs/` samodzielnie.

5. **Uruchom testy.**
   ```bash
   pytest tests/ -v
   ```
   Jeśli coś nie przechodzi, napraw **implementację**, nie test i nie
   tolerancję — chyba że test sam jest błędny (np. literówka), co
   uzasadnij wprost.

6. Podsumuj: co zmieniłeś, wynik testów, czy specyfikacja pozostała
   nietknięta.
