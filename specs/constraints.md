# Ograniczenia projektowe i procesowe

Ten plik uzupełnia `specs/spec.md` o ograniczenia, które nie są wymiarami
geometrycznymi, ale mają wpływ na sposób generowania i akceptowania modelu.
Traktuj go jako część źródła prawdy — na równi ze `spec.md` i
`parameters.yaml`.

## Ograniczenia inżynieryjne

1. **Materiał i grubość ścianek**: podstawa ma stałą grubość
   `base_thickness = 5.0 mm`. Żadna operacja (fillet, otwory) nie może
   redukować lokalnej grubości materiału do zera ani tworzyć przerwania
   ciągłości bryły.
2. **Otwory przelotowe**: wszystkie cztery otwory montażowe muszą przechodzić
   przez całą grubość podstawy. Otwory ślepe (nieprzelotowe) są niezgodne ze
   specyfikacją.
3. **Brak przecinania się cech**: promień zaokrąglenia (`fillet_radius`) i
   odsunięcie otworu od krawędzi (`hole_edge_offset`) muszą być tak dobrane,
   aby otwory nie przecinały strefy zaokrąglenia narożnika. Jeśli zmiana
   parametrów naruszy tę zależność, generowanie modelu ma się zatrzymać z
   jasnym komunikatem (patrz `.claude/CLAUDE.md`, zasada "nie zgaduj").
4. **Pojedyncza bryła**: wynikowy model musi być jedną spójną bryłą
   (`solid_count == 1`). Wynik w postaci wielu brył lub bryły zerowej
   objętości jest błędem specyfikacji lub implementacji, nie czymś do
   "naprawienia" przez rozluźnienie testów.

## Ograniczenia procesowe (workflow)

1. **Specyfikacja jest źródłem prawdy.** Claude nie ma prawa zmieniać
   wartości, tolerancji ani reguł w `specs/` w celu przepchnięcia testów.
2. **Jedno źródło parametrów maszynowych.** `specs/parameters.yaml` jest
   jedynym miejscem, z którego kod odczytuje wartości liczbowe. Tabela w
   `spec.md` jest kopią do czytania przez ludzi i musi być z nim zgodna
   (weryfikowane automatycznie).
3. **Brak zgadywania.** Jeśli specyfikacja jest niepełna lub sprzeczna,
   proces generowania ma się zatrzymać, a nie przyjmować wartości domyślne
   wymyślone ad hoc.
4. **Rozdzielenie eksportu STEP/STL od renderowania PNG.** Błąd renderera
   podglądu nie może zablokować wygenerowania plików STEP/STL ani zafałszować
   raportu — musi być raportowany jako osobny, jawny błąd.
5. **Determinizm.** Budowanie modelu z tych samych parametrów musi dawać ten
   sam wynik geometryczny (bounding box, objętość, powierzchnia, liczba brył,
   cechy) przy każdym uruchomieniu. Metadane plikowe (np. znaczniki czasu w
   STEP) nie są częścią tej gwarancji i nie powinny być porównywane binarnie.

## Znane ograniczenia automatycznej walidacji

* Automatyczna, w pełni topologiczna detekcja "czy to jest otwór montażowy"
  (odróżnienie otworu od zaokrąglenia albo innej cylindrycznej cechy) jest
  zawodna bez dodatkowej analizy CAD. Walidacja liczby i średnicy otworów
  opiera się więc na jawnych metadanych cech (`ModelFeatures`) zwracanych
  przez `build_model()`, uzupełnionych o niezależny, najlepszy-możliwy
  (best-effort) przegląd topologiczny oznaczony w raporcie jako
  informacyjny — patrz `src/cad_project/validation.py` i
  `docs/mcp-roadmap.md` dla kontekstu przyszłych usprawnień.
