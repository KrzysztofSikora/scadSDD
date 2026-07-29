# Log decyzji projektowych — Magnetic Rifle Barrel Mount

## 2026-07-28 — Nowy, osobny model obok `bracket-001`

**Decyzja**: nowa specyfikacja (`specs/rifle-mount/`) i nowy moduł kodu
(`src/cad_project/rifle_mount/`), zamiast rozszerzania/zastępowania
istniejącego uchwytu montażowego. Reużyto generyczne moduły
`measurements.py`, `exports.py`, `rendering.py` (biorą dowolny `Part`,
nie są specyficzne dla `bracket-001`). Osobny CLI
(`python -m cad_project.rifle_mount.cli`) i osobne drzewo wyjściowe
(`output/rifle-mount/`), żeby nie kolidować z plikami uchwytu montażowego.

**Uzasadnienie**: użytkownik wybrał tę opcję wprost, chcąc zachować
działający przykład referencyjny (`bracket-001`) nietknięty.

## 2026-07-28 — Punkt odniesienia zakresu regulacji

**Decyzja**: zakres 80–140 mm jest mierzony od zewnętrznej (przyściennej)
powierzchni płyty mocującej Części A do **środka lufy** spoczywającej w
chwycie U Części B, a nie do krawędzi U ani do samej długości mechanizmu
gwintowanego.

**Uzasadnienie**: to najbardziej użytkowa definicja funkcjonalna dla osoby
montującej uchwyt w sejfie (interesuje ją, gdzie faktycznie znajdzie się
lufa), wybrana wprost przez użytkownika.

**Konsekwencja obliczeniowa**: wymagało to rozbicia całkowitej długości na
stałą część (płyta + tuleja + kołnierz + dno U + promień lufy) i zmienną
część (wysuw gwintowanego trzpienia) — patrz niżej.

## 2026-07-28 — Wyprowadzenie długości mechanizmu

**Dane wejściowe (zatwierdzone przez użytkownika)**:
`mounting_plate_thickness=4, nut_boss_length=24, collar_length=10,
u_wall_thickness=6, barrel_diameter_reference=20` (promień 10).

**Obliczenie**:
```
fixed_offset = mounting_plate_thickness + nut_boss_length + collar_length
             + u_wall_thickness + barrel_diameter_reference/2
             = 4 + 24 + 10 + 6 + 10 = 54 mm

exposed_min = wall_to_barrel_center_min - fixed_offset = 80 - 54 = 26 mm
exposed_max = wall_to_barrel_center_max - fixed_offset = 140 - 54 = 86 mm
travel = exposed_max - exposed_min = 60 mm
       = wall_to_barrel_center_max - wall_to_barrel_center_min  ✓ (spójne)

rod_threaded_length >= exposed_max + thread_engagement_length
                     = 86 + 20 = 106 mm
=> przyjęto rod_threaded_length = 108 mm (2 mm marginesu bezpieczeństwa)
```

Przy takim doborze, zazębienie gwintu (`min(thread_engagement_length,
rod_threaded_length - exposed_length)`) wynosi dokładnie
`thread_engagement_length` = 20 mm w **całym** zakresie regulacji — nie
maleje przy maksymalnym wysunięciu. Sprawdzenie tej nierówności jest
zaimplementowane jako `check_engineering_preconditions()` w
`src/cad_project/rifle_mount/parameters.py`, analogicznie do
`bracket-001`.

**Uzasadnienie**: to jest wymóg bezpieczeństwa (patrz
`specs/rifle-mount/constraints.md`, pkt 2) — obliczenie, nie zgadywanie;
wartości pośrednie (fixed_offset components) zostały zaproponowane
człowiekowi do zatwierdzenia przed implementacją, zgodnie z zasadą "nie
zgaduj wartości inżynieryjnych, zaproponuj do zatwierdzenia".

## 2026-07-28 — Modelowanie gwintu: prawdziwy gwint trapezowy (bd_warehouse)

**Decyzja**: gwint między Częścią A i B jest modelowany jako rzeczywisty,
drukowalny gwint trapezowy (kąt 29°, jak ACME) przy użyciu biblioteki
`bd_warehouse` (`bd_warehouse.thread.TrapezoidalThread`), dodanej jako
nowa zależność w `pyproject.toml`. Build123d 0.11.1 nie ma wbudowanego
generatora gwintów — sprawdzono (`dir(build123d)` nie zawiera nic z
"Thread"), stąd potrzeba zewnętrznej biblioteki.

**Alternatywy odrzucone**: (a) uproszczona/reprezentacyjna geometria
gwintu — odrzucona, bo wprowadzałaby geometrię udającą cechę, której
naprawdę nie ma (niezgodne z zasadą "nie udawaj, że działa"); (b) brak
gwintu, gładkie połączenie teleskopowe — odrzucona, użytkownik chciał
realnego mechanizmu wkręcanego.

**Kompromis wydajnościowy**: budowanie samego gwintu (zewnętrznego +
wewnętrznego) zajmuje ok. 15s na tym sprzęcie (sweep helikalny w OCCT).
To istotnie wolniejsze niż `bracket-001` (< 1s). Testy w
`tests/rifle_mount/` używają fixture'ów o zasięgu modułu
(`scope="module"`), żeby nie odbudowywać modelu bez potrzeby, a testy
determinizmu/rebuild są ograniczone do jednego dodatkowego build per
plik testowy, nie per-test.

**Uzasadnienie**: użytkownik wybrał tę opcję wprost, świadomy kompromisu
czasowego, po tym jak przedstawiono trzy opcje (prawdziwy gwint /
uproszczony placeholder / brak gwintu w v1).

## 2026-07-28 — Kształt chwytu U: prostokątny rowek, nie półokrągły

**Decyzja**: chwyt U jest zamodelowany jako prosty, prostokątny rowek
(płaskie dno, proste ścianki, otwarty u góry), a nie geometrycznie
"okrągła litera U" z zaokrąglonym dnem dopasowanym do krzywizny lufy.
Dodano nowy parametr `u_arm_height` (25mm) — wysokość wewnętrzna ramion od
dna do górnej krawędzi, potrzebna do jednoznacznego zamknięcia geometrii
U, a nieobecna w pierwotnej rozmowie z użytkownikiem.

**Uzasadnienie**: (1) matematycznie, pozycja środka lufy względem dna
(`u_wall_thickness + barrel_diameter_reference/2`) jest identyczna
niezależnie od tego, czy dno jest płaskie czy zaokrąglone stycznie do
lufy (promień krzywizny się skraca w rachunku) — więc wybór nie wpływa na
wyprowadzenie zakresu regulacji 80–140mm. (2) Płaskie dno jest prostsze i
bardziej niezawodne do wydruku 3D niż wewnętrzny łuk (który zwykle
wymaga podpór). Potocznie "uchwyt/kanał w kształcie litery U" bardzo
często oznacza właśnie prosty prostokątny rowek (np. "U-bracket",
"U-channel" w sprzęcie), więc to nie jest odejście od intencji
użytkownika, tylko konkretyzacja niejednoznacznego opisu.
**Wysokość ramion (25mm) dobrana** tak, by z zapasem obejmować
`barrel_diameter_reference` (20mm) mierzone od dna.

## 2026-07-28 — Osadzenie magnesów i geometria płyty

**Decyzja**: płyta mocująca to kwadrat 50×50×4mm z zaokrągleniem
narożników R5mm; cztery magnesy Ø12×3mm w kieszeniach ślepych (1mm
ścianki nad magnesem), środki odsunięte 10mm od krawędzi płyty.

**Uzasadnienie**: rozmiar/liczba magnesów i grubość ścianki nad nimi były
wprost wybrane przez użytkownika; odsunięcie (10mm) i zaokrąglenie (R5mm)
to propozycje zaakceptowane bez zmian.

**Korekta wykryta podczas implementacji**: pierwotnie zaproponowany wymiar
płyty (50mm) powodowałby kolizję geometryczną — kieszenie na magnesy w
narożnikach (środek magnesu ~21.2mm od środka płyty, promień 6mm →
najbliższa krawędź kieszeni ~15.2mm od środka) nachodziłyby na tuleję
gwintowaną (promień 16.5mm = nut_boss_outer_diameter/2), która dopiero
później w kolejności specyfikacji uzyskała swój wymiar z parametrów
gwintu. Poprawiono na **60mm** (margines ~5.8mm między kieszenią a tuleją)
i dodano jawną kontrolę tej kolizji w
`check_engineering_preconditions()` (`src/cad_project/rifle_mount/parameters.py`),
żeby taka niespójność była wykrywana automatycznie przy każdej zmianie
parametrów, nie tylko przy pierwszym projektowaniu. Ta korekta dotyczyła
wyłącznie wartości zaproponowanej przez system (nie wymogu użytkownika)
i została zgłoszona użytkownikowi wprost.

## 2026-07-28 — Poprawka: chwyt U wyśrodkowany na osi trzpienia (bug zgłoszony przez użytkownika)

**Problem zgłoszony przez użytkownika**: po obejrzeniu obu części w
FreeCAD, użytkownik zauważył, że miejsce oparcia lufy w chwycie U nie
leży na tej samej osi co gwintowany trzpień — wygląda na przesunięte/
"zgięte" względem trzpienia. Słuszna obserwacja: to był rzeczywisty błąd
implementacji, nie kwestia gustu.

**Diagnoza**: w pierwotnej implementacji blok chwytu U był pozycjonowany
z wyrównaniem `Align.MIN` na osi X (prostopadłej do osi trzpienia) — jego
dolna ścianka dotykała stycznie powierzchni trzpienia/kołnierza (X=0),
zamiast być wyśrodkowana na jego osi. W efekcie środek lufy spoczywającej
w chwycie znajdował się `u_wall_thickness + barrel_diameter_reference/2`
= 16mm **nad** osią trzpienia, a nie na niej. Dodatkowo pierwotne
wyprowadzenie w tym pliku (`fixed_offset` z użyciem
`barrel_diameter_reference/2`) było niespójne z tym, jak kod faktycznie
pozycjonował szczelinę U wzdłuż osi Z (`u_wall_thickness +
u_internal_width/2`) — dwa różne, niezgodne ze sobą wzory na tę samą
odległość.

**Poprawka** (`src/cad_project/rifle_mount/model.py::build_arm_part`):
1. Blok chwytu U jest teraz wyrównany `Align.CENTER` na osi X (dolna
   szczelina/ściana pozycjonowana względem środka bloku, nie względem
   jego dolnej krawędzi), więc cały chwyt jest wyśrodkowany na osi
   trzpienia.
2. `u_arm_height` poprawiono z 25.0mm na **26.0mm**, tak aby całkowita
   wysokość chwytu (`u_wall_thickness + u_arm_height` = 32mm) była
   dokładnie dwukrotnością odległości od dna szczeliny do osi trzpienia
   (`u_wall_thickness + barrel_diameter_reference/2` = 16mm) — to daje
   środkowi lufy referencyjnej dokładnie zerowe przesunięcie względem osi
   trzpienia (współosiowość).
3. Wyprowadzenie `fixed_offset` w tym pliku i w
   `specs/rifle-mount/spec.md` poprawiono, by używać spójnego, zgodnego z
   kodem wzoru: `u_wall_thickness + u_internal_width/2` (21mm) zamiast
   `u_wall_thickness + barrel_diameter_reference/2` (16mm) jako składnik
   wzdłuż osi Z. Nowy `fixed_offset` = 59mm (był błędnie 54mm).
   `check_engineering_preconditions()` i
   `validation.py::_thread_engagement_range_check()` zaktualizowano tym
   samym wzorem.
4. `rod_threaded_length` (108mm) **nie wymagał zmiany** — przy
   poprawionym `fixed_offset` (59mm zamiast 54mm) wymagane minimum to
   101mm (był 106mm), więc margines nawet się zwiększył (7mm zamiast
   2mm).

**Uzasadnienie**: to poprawka błędu geometrycznego, nie zmiana wymagań
użytkownika — zakres regulacji (80–140mm), rozmiar prześwitu U (30mm) i
wszystkie pozostałe wymagania pozostają identyczne. Poprawiono wyłącznie
to, JAK chwyt U jest ustawiony względem osi trzpienia, zgodnie z
oczekiwaniem współosiowości.

## 2026-07-29 — Reorientacja chwytu: U -> C (zgłoszone przez użytkownika po obejrzeniu w FreeCAD)

**Problem zgłoszony przez użytkownika**: po obejrzeniu Części B w FreeCAD,
użytkownik ocenił, że profil chwytu, patrząc z boku (wzdłuż osi lufy),
powinien wyglądać jak litera „C" (otwarty do przodu, w stronę czubka
ramienia), a nie jak „U" (otwarty do góry, prostopadle do osi trzpienia).
To decyzja projektowa użytkownika co do kształtu produktu, nie błąd
implementacji (w przeciwieństwie do poprzedniej poprawki współosiowości
powyżej).

**Analiza geometryczna**: chwyt U/C żyje w płaszczyźnie prostopadłej do
osi lufy (Y), rozpiętej przez oś trzpienia (Z) i oś prostopadłą (X).
Pierwotnie otwarcie było wzdłuż X (symetryczna „szerokość" prześwitu
`u_internal_width` wzdłuż Z), co odczytuje się jako „U" patrząc z osią
trzpienia poziomo. Jedyna sensowna reorientacja o 90° wokół osi lufy to
zamiana ról X i Z: otwarcie przenosi się na Z (w stronę czubka ramienia —
otwarcie w stronę kołnierza jest niemożliwe, bo kolidowałoby fizycznie z
kołnierzem), a symetryczny prześwit (`u_internal_width`) przenosi się na
X. To nie jest wybór między kilkoma opcjami, tylko jedyna geometrycznie
spójna interpretacja polecenia „jak C, nie jak U".

**Konsekwencja dla współosiowości**: w nowej orientacji oś X (dawniej
wymagająca starannego doboru `u_arm_height`, żeby wypaść dokładnie na
osi trzpienia — patrz poprawka wyżej) jest symetryczna **z konstrukcji**
(prześwit `u_internal_width` wyśrodkowany wokół X=0 niezależnie od
wartości innych parametrów). Poprzedni check `coaxial_offset` w
`check_engineering_preconditions()` stał się więc nieaktualny (sprawdzał
zależność, która już nie istnieje) i został usunięty — współosiowość jest
teraz niezmiennikiem geometrii, nie czymś do zwalidowania przy każdej
zmianie parametrów.

**Konsekwencja dla `fixed_offset`**: oś Z (dawniej symetryczny prześwit,
`u_wall_thickness + u_internal_width/2` = 21mm) staje się teraz
asymetryczna (ściana oporowa + głębokość otwarcia), analogicznie do tego,
jak wcześniej działała oś X: lufa opiera się o tylną ściankę, więc
odległość od kołnierza do środka lufy = `u_wall_thickness +
barrel_diameter_reference/2` = 6+10 = **16mm** (zamiast 21mm). To
przywraca pierwotną, prostszą formułę sprzed poprawki współosiowości
(54mm — patrz wyżej), zanim uwzględniono w niej rozmiar tulei
(`nut_boss_length`) po jego wydłużeniu (patrz niżej) — ostateczny
`fixed_offset` = 74mm, patrz `spec.md` ("Zależność geometryczna").

`u_arm_height` (26mm) nie wymagał zmiany — liczbowo odpowiada
`u_wall_thickness + barrel_diameter_reference` (6+20=26), więc lufa
mieści się dokładnie w głębokości otwarcia, stykając się z tylną ścianką
i kończąc równo z otwartym czołem ramienia. Ten sam numeryczny dobór,
który wcześniej (przypadkowo, przez konstrukcję wzoru współosiowości)
zapewniał symetrię w X, teraz naturalnie zapewnia dopasowanie głębokości
w Z — bez dodatkowego przeliczania.

**Implementacja** (`src/cad_project/rifle_mount/model.py::build_arm_part`):
blok chwytu i wycięcie prześwitu zamieniły role osi X i Z (patrz kod);
rowek na wkładkę filcową analogicznie przeniesiony z tylnej ścianki wzdłuż
Z (był wzdłuż X). Bok chwytu wzdłuż lufy (Y, `u_arm_length`) bez zmian.

**Uzasadnienie**: to zmiana kształtu na wyraźne życzenie użytkownika, nie
domysł inżynierski — geometria (kierunek otwarcia) była jednoznacznie
wyprowadzalna z opisu „jak C, nie jak U" plus ograniczenia fizycznego
(nie może kolidować z kołnierzem), a numeryczna konsekwencja
(`fixed_offset`) jest przeliczeniem, nie zgadywaniem.

## 2026-07-29 — Wydłużenie zazębienia gwintu (na wyraźne polecenie użytkownika)

**Decyzja**: `thread_engagement_length` 20mm → **40mm** (+100%,
zatwierdzone przez użytkownika spośród zaproponowanych opcji +50%/+100%/
własna wartość). Odpowiednio wydłużono `nut_boss_length` 24mm → **44mm**
(zachowując wzorzec „zazębienie + 4mm marginesu/wejścia na gwint") oraz
`rod_threaded_length` 108mm → **112mm**.

**Obliczenie `rod_threaded_length`** (z uwzględnieniem nowego
`fixed_offset` = 74mm po reorientacji U→C powyżej):
```
exposed_max = wall_to_barrel_center_max - fixed_offset = 140 - 74 = 66mm
rod_threaded_length >= exposed_max + thread_engagement_length
                     = 66 + 40 = 106mm
=> przyjęto rod_threaded_length = 112mm (6mm marginesu bezpieczeństwa,
   analogicznie do marginesu przyjętego w pierwotnym wyprowadzeniu)
```

**Uzasadnienie**: użytkownik zauważył, że po reorientacji U→C margines
zazębienia przy maksymalnym wysunięciu skurczyłby się z 7mm do ~2mm
(przy niezmienionym 108mm), i wprost poprosił o wydłużenie zarówno
zazębienia gwintu, jak i tulei w Części A, w którą wkręca się trzpień —
to wymóg bezpieczeństwa/solidności połączenia (patrz
`specs/rifle-mount/constraints.md`, pkt 2), nie kwestia gustu. Docelowa
wartość (+100%) została wybrana przez użytkownika spośród
przedstawionych opcji, nie zgadnięta.
