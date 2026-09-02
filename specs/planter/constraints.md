# Ograniczenia projektowe i procesowe — Premium Self-Watering Planter

Uzupełnia `specs/planter/spec.md`. Traktuj na równi ze `spec.md` i
`parameters.yaml` jako źródło prawdy dla ograniczeń nie będących wprost
wymiarami.

## Ograniczenia inżynieryjne

1. **Dwie osobne bryły, nie jedna.** Insert i Reservoir **muszą** być
   dwiema fizycznie osobnymi częściami — insert ma być wyjmowany do
   przesadzania/napełniania rdzenia ziemią i do wglądu w poziom wody.
   Walidacja sprawdza `solid_count == 1` **dla każdej części z osobna**.
2. **Brak gwarancji podciągania wody przez sam plastik.** Rdzeń kapilarny
   to perforowana rura, nie lity knot. Kapilarne wznoszenie wody przez
   samą (niehydrofilową) ściankę PLA/PETG na odległość rzędu centymetrów
   jest fizycznie wątpliwe (szacunkowo rzędu ~1cm dla typowej szczeliny
   0.5-1mm i kąta zwilżania PLA, patrz `decisions.md`) — dlatego
   mechanizm celowo polega na **kapilarności ziemi/substratu**
   wypełniającego rurę, nie na plastiku. To świadome ograniczenie
   projektowe, ujawnione użytkownikowi w trakcie ustalania wymagań
   (`AskUserQuestion`, opcja "bardziej złożona geometria i mniej pewne
   działanie fizyczne" — wybrana świadomie). Model geometryczny nie
   weryfikuje rzeczywistej skuteczności nawadniania — to zależy od typu
   substratu, wilgotności, gatunku rośliny, czego specyfikacja nie
   precyzuje.
3. **Brak analizy wytrzymałości/szczelności.** Model nie weryfikuje
   szczelności zbiornika (typowe dla FDM: warstwy mogą przeciekać bez
   dodatkowego uszczelnienia, np. żywicą lub octanem winylu — poza
   zakresem tego repozytorium) ani wytrzymałości nóżek/spódnicy pod
   obciążeniem mokrej ziemi.
4. **Prześwit dziubka do nalewania.** Dziubek musi zachować > 2mm
   prześwitu do rozszerzającej się ścianki wkładu na całej wysokości
   swojego wystawania ponad Z=0 — sprawdzane jawnie w
   `check_engineering_preconditions()`. Zakłada, że insert nigdy się nie
   zwęża idąc w górę (`insert_top_outer_diameter ≥
   insert_bottom_outer_diameter`); odwrócenie tego założenia w przyszłym
   wariancie wymaga przeliczenia tego sprawdzenia od nowa (patrz uwaga w
   `parameters.py::check_engineering_preconditions`).
5. **Fillet tylko zewnętrznej krawędzi górnej.** Przy grubości ścianki
   `insert_wall_thickness` (2.4mm) zaokrąglenie obu krawędzi (zewnętrznej
   i wewnętrznej) na tej samej, wąskiej ściance czołowej jest
   geometrycznie niewykonalne dla OCCT — zweryfikowane bezpośrednio próbą
   budowy (patrz `decisions.md`). Zaokrąglana jest tylko krawędź
   zewnętrzna.

## Ograniczenia procesowe (workflow)

Te same zasady co dla `bracket-001` i `magnetic-rifle-mount-001` (patrz
`specs/constraints.md` i `.claude/CLAUDE.md`) obowiązują też tutaj:
`specs/planter/*` jest źródłem prawdy, Claude nie zgaduje brakujących
wartości inżynieryjnych, nie zmienia tolerancji żeby przepchnąć
walidację, itd.

## Architektura serii (dla przyszłych wariantów)

Ten model jest **pierwszym** z planowanej serii doniczek sprzedawanych
jako pliki STL. Żeby kolejne warianty faktycznie zachowały te same
rozmiary/kształt/mechanizm (wymóg użytkownika), obowiązuje podział:

* **Rdzeń (niezmienny między wariantami)**: wszystkie parametry poza
  blokiem `pattern_*` w `parameters.yaml` — wymiary insertu i zbiornika,
  rdzeń kapilarny, spódnica/gardziel, dziubek, otwór przelewowy, nóżki.
* **Wymienny wzór**: wyłącznie blok `pattern_*` (`pattern_flute_count`,
  `pattern_flute_depth`, `pattern_flute_width_deg`,
  `pattern_flute_end_margin`) i funkcja `_carve_wall_pattern()` w
  `model.py` — patrz `decisions.md` ("Architektura wymiennego wzoru") po
  pełne wyjaśnienie, jak podmienić wzór na kolejny wariant bez ruszania
  reszty modelu.

Nowy wariant serii **nie jest** nowym modelem w rozumieniu tabeli w
`.claude/CLAUDE.md` — to zmiana `pattern_*` (i ewentualnie nowej funkcji
carve) w tym samym `self-watering-planter-001`, nie nowy `specs/<model>/`.

## Znane ograniczenia i decyzje o zakresie (v1)

* **Rozmiar bazowy** (Ø130mm góra, Ø126mm dół, wys. 110mm) dobrany na
  podstawie researchu popularnych samonawadniających doniczek STL na
  Etsy (typowy zakres, patrz `decisions.md`), nie z wymogu użytkownika co
  do konkretnych milimetrów — jeśli późniejsza sprzedaż pokaże, że inny
  rozmiar sprzedaje się lepiej, zmiana rdzenia wymaga świadomej decyzji
  (przeliczenia wszystkich zależnych wymiarów: spódnicy, zbiornika,
  dziubka, rdzenia kapilarnego), nie prostej edycji jednej liczby.
* **Gwint/zatrzask nie zaimplementowany.** Insert opiera się na
  zbiorniku na wcisk (spódnica + pierścień oparcia), bez zatrzasku ani
  gwintu — insert można swobodnie unieść do kontroli poziomu wody/napełnienia.
  Świadomy wybór dla prostoty (mniej elementów do wydruku, łatwiejszy
  montaż), ale nie zabezpiecza przed przypadkowym zsunięciem przy
  przenoszeniu doniczki za wkład.
