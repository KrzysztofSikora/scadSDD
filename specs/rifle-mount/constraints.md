# Ograniczenia projektowe i procesowe — Magnetic Rifle Barrel Mount

Uzupełnia `specs/rifle-mount/spec.md`. Traktuj na równi ze `spec.md` i
`parameters.yaml` jako źródło prawdy dla ograniczeń nie będących wprost
wymiarami.

## Ograniczenia inżynieryjne

1. **Dwie osobne bryły, nie jedna.** W przeciwieństwie do
   `bracket-001`, ten model **musi** wytwarzać dwie fizycznie osobne części
   (Część A i Część B), które użytkownik skręca ręcznie. Walidacja sprawdza
   `solid_count == 1` **dla każdej części z osobna**, nie dla całego
   złożenia.
2. **Zazębienie gwintu.** `rod_threaded_length` musi zawsze zapewniać co
   najmniej `thread_engagement_length` rzeczywistego zazębienia w całym
   zakresie regulacji (87–140 mm). To nie jest opcjonalny margines
   bezpieczeństwa — niedostateczne zazębienie oznacza, że część B może się
   wykręcić pod obciążeniem wysuniętej lufy.
3. **Kołnierz jako ogranicznik.** `collar_diameter` musi być ściśle
   większy niż `thread_major_diameter` (żeby fizycznie ograniczał
   wkręcanie) i ściśle mniejszy niż średnica zewnętrzna tulei
   (`thread_major_diameter + 2×nut_wall_thickness`), żeby mógł oprzeć się
   o jej czoło bez kolizji geometrycznej.
4. **Paski magnetyczne nie mogą się nakładać ani kolidować z tuleją.**
   (v3) Dwie prostokątne kieszenie na paski magnetyczne muszą leżeć
   symetrycznie po przeciwnych stronach środka płyty, bez wzajemnego
   nakładania, bez wychodzenia poza krawędź płyty i bez kolizji z rzutem
   tulei gwintowanej — patrz `spec.md` ("Reguły") i
   `decisions.md` ("v3 — paski magnetyczne zamiast dysków").
5. **Prześwit U musi mieć zapas.** `u_internal_width` musi być zauważalnie
   większy niż `barrel_diameter_reference` — to nie jest pasowanie
   precyzyjne, tylko swobodny wsuw (patrz `spec.md`).
6. **Rowek na wkładkę nie może przebić ścianki.** `liner_groove_depth <
   u_wall_thickness`, z rozsądnym marginesem (rowek nie powinien zajmować
   więcej niż połowy grubości ścianki, żeby nie osłabiać konstrukcji).

## Ograniczenia procesowe (workflow)

Te same zasady co dla `bracket-001` (patrz `specs/constraints.md` i
`.claude/CLAUDE.md`) obowiązują też tutaj: `specs/rifle-mount/*` jest
źródłem prawdy, Claude nie zgaduje brakujących wartości inżynieryjnych,
nie zmienia tolerancji żeby przepchnąć walidację, itd.

## Znane ograniczenia i decyzje o zakresie (v1)

* **Gwint jest realną, drukowalną geometrią** (biblioteka `bd_warehouse`,
  gwint trapezowy/ACID 29°), nie uproszczoną reprezentacją — decyzja
  podjęta świadomie z użytkownikiem (patrz `decisions.md`). Konsekwencja:
  budowanie modelu jest zauważalnie wolniejsze niż dla `bracket-001`
  (rząd kilkunastu sekund na sam gwint) — patrz `decisions.md` po
  szczegóły wydajności i jak to uwzględniono w projekcie testów.
* **Brak modelowania siły magnesów.** Model geometryczny nie weryfikuje,
  czy 2× pasek magnetyczny 45×13×4mm (od v3 — patrz `decisions.md` "v3 —
  paski magnetyczne zamiast dysków") faktycznie utrzyma karabin przy
  maksymalnym wysięgu 140mm (to zależy od masy broni, grubości ścianki
  sejfu i siły przyciągania konkretnego paska, czego specyfikacja nie
  precyzuje) — to świadome ograniczenie zakresu, nie błąd. Jeśli potrzebna
  weryfikacja wytrzymałościowa, wymaga osobnej analizy inżynierskiej poza
  tym repozytorium.
* **Brak analizy wytrzymałości ścianek na zginanie.** Podobnie, model nie
  weryfikuje naprężeń w trzpieniu/tulei/kołnierzu przy maksymalnym
  wysięgu (140mm, moment gnący od masy karabinu) — to potencjalny
  "problem konstrukcyjny" do wskazania przez `cad-reviewer`, nie coś, co
  automatyczna walidacja geometrii może ocenić bez symulacji FEM.
* **Detekcja cech gwintu** (podobnie jak liczba otworów w `bracket-001`)
  opiera się na jawnych metadanych zwracanych przez `build_model()`, nie
  na w pełni niezawodnej analizie topologicznej gwintu (topologia gwintu
  helikalnego jest znacznie bardziej złożona niż proste otwory
  cylindryczne).

## Znane ograniczenia i decyzje o zakresie (v2)

* **Margines wysuwu przy minimalnej odległości jest bardzo mały (0.5mm).**
  Dodanie w v2 łagodnego, drukowalnego-bez-podpór przejścia między
  kołnierzem a chwytem C (`cradle_transition_height`) wykorzystuje niemal
  cały zapas, jaki istniał między `fixed_offset` a
  `wall_to_barrel_center_min` (patrz `specs/rifle-mount/decisions.md`, "v2
  — łagodne przejście C/gwint"). Przy w pełni wkręconym mechanizmie wysuw
  trzpienia poza tuleją wynosi tylko ~0.5mm — technicznie dodatnie
  (spełnia `check_engineering_preconditions()`), ale praktycznie oznacza
  zerowy zapas na tolerancje wydruku. Użytkownik świadomie wybrał
  zachowanie tego marginesu identycznym (dokładnie 0.5mm) w v2 i ponownie
  w v2.1 zamiast wygodniejszego marginesu — to świadome, powtórzone
  ograniczenie zakresu, nie błąd.
* **Luz między kołnierzem a czołem tulei zmniejszony do ~0.5mm promienia.**
  `collar_diameter` powiększono z 27mm do 32mm (v2), żeby skrócić wymaganą
  wysokość przejścia — zostaje ~1mm luzu na średnicy (0.5mm promienia) do
  `nut_boss_outer_diameter` (33mm). Wystarczające dla druku FDM przy
  typowych tolerancjach (rzędu ±0.1–0.3mm na wymiar), ale ciaśniejsze niż
  pozostałe pasowania w tym modelu — warte uwagi przy ewentualnej dalszej
  zmianie `nut_wall_thickness` lub `thread_major_diameter`.
* **Kąt narostu przejścia ma niewielki zapas do progu 45°.**
  Wartość progu 45° to standardowe (nie zmierzone materiałowo) założenie
  o granicy samo-podpierania w druku FDM — różne materiały/drukarki mogą
  tolerować więcej lub mniej. Jeśli w praktyce dany model drukarki/materiał
  wymaga mniejszego kąta, może być konieczne dalsze zmniejszenie nawisu
  (większy `collar_diameter` lub inny kształt bloku C) kosztem jeszcze
  mniejszego marginesu przy minimalnym wysuwie — a to już koliduje z
  zachowaniem dokładnego zakresu regulacji (patrz punkt wyżej).

## Znane ograniczenia i decyzje o zakresie (v2.1)

* **Zakres regulacji nie jest już równy 8–14cm.** Pogrubienie
  `u_wall_thickness` (6→9mm, na wyraźne polecenie użytkownika, dla
  bardziej masywnego podparcia lufy) wymagało podniesienia
  `wall_to_barrel_center_min` z 80mm do 86mm, żeby zachować dodatni zapas
  wysuwu trzpienia i kąt nawisu przejścia ≤45° — patrz
  `specs/rifle-mount/decisions.md` ("v2.1 — masywniejszy chwyt C"). Nowy
  zakres to 86–140mm; opcja zachowania dokładnie 80mm kosztem innego
  kompromisu (skrócenie `collar_length` lub `cradle_transition_height`)
  została przedstawiona i odrzucona przez użytkownika na rzecz podniesienia
  dolnej granicy.
* **`u_arm_height` (26mm) nie zostało przeliczone razem z
  `u_wall_thickness`.** Wcześniej (v2) liczbowo odpowiadało
  `u_wall_thickness + barrel_diameter_reference`, tak by lufa referencyjna
  kończyła się równo z otwartym czołem ramienia — po zwiększeniu
  `u_wall_thickness` do 9mm ta zbieżność liczbowa już nie zachodzi (lufa
  kończy się ~3mm przed czołem ramienia zamiast dokładnie na czole).
  Świadomie pozostawione bez zmian, bo nie było to przedmiotem żądania
  użytkownika i nie jest wymogiem sprawdzanym przez
  `check_engineering_preconditions()` — czysto kosmetyczna/funkcjonalna
  różnica, nie błąd konstrukcyjny.

## Znane ograniczenia i decyzje o zakresie (v3)

* **Zakres regulacji nie jest już równy 86–140mm.** Zastąpienie czterech
  dyskowych magnesów neodymowych dwoma paskami magnetycznymi (na wyraźne
  polecenie użytkownika) pogrubiło `mounting_plate_thickness` (4→5mm, bo
  pasek jest grubszy niż dysk), co wymagało podniesienia
  `wall_to_barrel_center_min` z 86mm do 87mm, żeby zachować dodatni zapas
  wysuwu trzpienia — patrz `specs/rifle-mount/decisions.md` ("v3 — paski
  magnetyczne zamiast dysków"). Nowy zakres to 87–140mm.
* **Kieszenie na paski magnetyczne są prostokątne, nie okrągłe, i jest ich
  dwie zamiast czterech.** `magnet_pocket_length`/`magnet_pocket_width`
  (45×13mm) zastępują `magnet_diameter` (Ø12mm); `magnet_center_offset_y`
  (odległość środka kieszeni od środka płyty) zastępuje
  `magnet_edge_offset` (odległość środka magnesu od krawędzi płyty) — te
  dwa parametry nie są równoważne liczbowo, bo opisują inny układ
  geometryczny (dwie kieszenie symetryczne względem środka, nie cztery w
  narożnikach). Płyta mocująca urosła z 60×60mm do 72×72mm, żeby
  pomieścić dłuższe kieszenie.
