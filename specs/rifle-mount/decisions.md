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

## 2026-07-29 — v2: łagodne przejście kołnierz → chwyt C (bez podpór przy druku)

**Żądanie użytkownika**: (1) regulacja odległości lufy od ścianki sejfu w
zakresie 8–14 cm — **już spełnione w v1** (`wall_to_barrel_center_min/max`
= 80/140mm to dokładnie 8/14cm; sprawdzono, że wyprowadzenie w tym pliku i
`check_engineering_preconditions()` są poprawne, nic tu nie wymagało
zmiany); (2) łagodne przejście między chwytem C a gwintem, tak żeby nie
trzeba było dodawać podpór przy druku 3D — to wymagało realnej zmiany
geometrii, opisanej niżej. Cała iteracja oznaczona jako **v2**
(`spec_version: "2.0.0"`).

**Diagnoza problemu z nawisem**: w v1 blok chwytu C (profil
`2×u_wall_thickness + u_internal_width` × `u_arm_length` = 42×40mm) siadał
bezpośrednio na kołnierzu Ø27mm (promień 13.5mm) — to nagły, 90-stopniowy
skok. Maksymalny promieniowy nawis (w rogach prostokątnego bloku,
odległość od osi = `sqrt(21² + 20²)` = **29mm** — trójkąt 20-21-29,
dokładny Pitagorejski) minus promień kołnierza = **15.5mm** nawisu bez
żadnego podparcia. Standardowy próg samo-podpierania w druku FDM to ~45°
od pionu — dla 15.5mm nawisu wymagałoby to ~15.5mm dodatkowej wysokości
przejścia.

**Konflikt z zakresem regulacji**: sztywna (nieregulowana) część
mechanizmu w v1 miała `fixed_offset` = 74mm (patrz wyprowadzenie wyżej), a
minimalna odległość to 80mm — czyli tylko **6mm zapasu** zanim
`wall_to_barrel_center_min` zostałoby naruszone (wysuw trzpienia musi
pozostać > 0 przy w pełni wkręconym mechanizmie). 15.5mm przejścia się
tam nie mieści. Użytkownik został o tym poinformowany wprost (nie
zgadywano rozwiązania) i zapytany, czy: (a) zachować dokładnie 80–140mm
kosztem bardzo małego marginesu mechanicznego, (b) lekko podnieść dolną
granicę (np. do 85–90mm) dla wygodnego marginesu, czy (c) wskazać własną
wartość pośrednią. **Użytkownik wybrał (a)** — zachować dokładnie
80–140mm.

**Rozwiązanie geometryczne** (żeby zmieścić przejście w 6mm zapasu):

1. `collar_diameter`: 27.0mm → **32.0mm** (nadal < `nut_boss_outer_diameter`
   = 33mm i > `thread_major_diameter` = 25mm — mieści się w istniejących
   ograniczeniach z `check_engineering_preconditions()`, tylko przesunięte
   bliżej górnej granicy; ~0.5mm promieniowego luzu do czoła tulei, patrz
   `constraints.md`).
2. Nowy parametr `cradle_corner_fillet_radius` = **19mm** — zaokrąglenie
   czterech pionowych krawędzi zewnętrznego profilu bloku C, zbliżające
   go do kształtu stadionu/owalu. To redukuje maksymalny promieniowy
   nawis z 29mm (róg ostrego prostokąta) do ~21.0–21.2mm (potwierdzone
   zarówno analitycznie — `hypot(21-19, 20-19) + 19 ≈ 21.24mm` — jak i
   bezpośrednim pomiarem przekrojów zbudowanej geometrii, patrz niżej).
3. Nowy parametr `cradle_transition_height` = **5.5mm** — lofterowana
   (płynna) bryła między okręgiem Ø32mm (szczyt kołnierza) a zaokrąglonym
   profilem bloku C z punktu 2 (ten sam promień `cradle_corner_fillet_radius`
   po obu stronach, żeby przejście i blok stykały się bez szwu).

**Weryfikacja kąta narostu — zmierzona, nie tylko wyliczona**: zbudowano
prototyp geometrii (kołnierz Ø32 + lofterowane przejście 5.5mm + blok
zaokrąglony r=19mm) i próbkowano przekroje `part.intersect(cienki_box)` co
0.5mm wysokości. Zmierzony promień rósł liniowo od 16.0mm (przy kołnierzu)
do 21.02mm (szczyt przejścia) w sposób monotoniczny — dając kąt narostu
**~42.4°** (`atan((21.02-16.0)/5.5)`), poniżej progu 45° z ~2.6° zapasu.
Cała zbudowana bryła Części B (kołnierz + przejście + zaokrąglony blok +
wycięcie C + gwint zewnętrzny) to nadal dokładnie 1 poprawna bryła
(`is_valid=True`) — sprawdzone przed wdrożeniem do `model.py`.

**Nowy `fixed_offset`** (dodano `cradle_transition_height`):
```
fixed_offset = mounting_plate_thickness + nut_boss_length + collar_length
             + cradle_transition_height + u_wall_thickness
             + barrel_diameter_reference/2
             = 4 + 44 + 10 + 5.5 + 6 + 10 = 79.5 mm

exposed_min = wall_to_barrel_center_min - fixed_offset = 80 - 79.5 = 0.5 mm
exposed_max = wall_to_barrel_center_max - fixed_offset = 140 - 79.5 = 60.5 mm
```
`exposed_min` = **0.5mm** — bardzo mały, ale ściśle dodatni zapas (wymóg
`check_engineering_preconditions()`: `exposed_min > 0`). To świadomy,
zaakceptowany przez użytkownika kompromis (opcja (a) wyżej) — patrz
`specs/rifle-mount/constraints.md` po jawne udokumentowanie tego
ograniczenia jako znanego dla v2.

`rod_threaded_length` (112mm, bez zmian) nadal z zapasem: wymagane
minimum = `exposed_max + thread_engagement_length` = 60.5 + 40 = 100.5mm,
margines 11.5mm (**lepiej** niż w v1, bo `cradle_transition_height`
skraca wysuw zamiast go wydłużać).

**Implementacja** (`src/cad_project/rifle_mount/model.py::build_arm_part`):
blok chwytu C jest teraz dodawany i filetowany (`cradle_corner_fillet_radius`
na jego 4 pionowych krawędziach) jako pierwszy element w `BuildPart`, żeby
`builder.edges().filter_by(Axis.Z)` jednoznacznie wybierało tylko jego
własne krawędzie (ten sam wzorzec co zaokrąglenie płyty w
`build_base_part`) — bez ryzyka złapania przypadkowych krawędzi z innych
elementów. Przejście to `loft()` między szkicem okręgu (na wysokości
szczytu kołnierza) a szkicem `RectangleRounded` (na wysokości startu
bloku C), oba jako jawne `Plane.XY.offset(z)` — zgodnie z zasadą modułu
"nigdy selekcji przez face()" (patrz docstring `model.py`), bo topologia
gwintu uniemożliwia bezpieczną selekcję przez faces().

**Nowe reguły walidacji** w
`check_engineering_preconditions()`: (1) `cradle_corner_fillet_radius`
musi być mniejszy niż połowa krótszego wymiaru profilu bloku C (inaczej
zaokrąglenie jest geometrycznie niewykonalne); (2) kąt narostu przejścia
(z konserwatywnego, analitycznego wzoru na narożnik — który daje ~21.24mm,
**większe** niż zmierzone ~21.02mm, więc jest to bezpieczne górne
oszacowanie) musi być ≤ 45°.

**Uzasadnienie całości**: to zmiana geometrii na wyraźne życzenie
użytkownika (łagodne przejście bez podpór), z liczbami wyprowadzonymi i
zmierzonymi (nie zgadniętymi) oraz z jawnym pytaniem do użytkownika w
punkcie, gdzie wymagania (dokładny zakres 80–140mm) i inżynieria
(potrzebna wysokość przejścia) się ze sobą ścierały.

## 2026-08-21 — v2.1: masywniejszy chwyt C (na wyraźne polecenie użytkownika)

**Żądanie użytkownika**: element chwytu C, na którym opiera się lufa
(tylna ścianka + ramiona boczne, `u_wall_thickness`), ma być bardziej
masywny, żeby lepiej podpierać lufę. Wyraźnie wykluczone: wydłużanie
gwintu/tulei/trzpienia (`thread_engagement_length`, `nut_boss_length`,
`rod_threaded_length` — bez zmian).

**Konflikt wykryty i przedstawiony użytkownikowi przed zmianą**:
`u_wall_thickness` wchodzi wprost do `fixed_offset`
(`src/cad_project/rifle_mount/parameters.py::check_engineering_preconditions`),
a zapas wysuwu przy minimalnej odległości (`exposed_min`) w v2 wynosił
tylko 0.5mm — każde zwiększenie `u_wall_thickness` o więcej niż to
łamałoby `wall_to_barrel_center_min` = 80mm. Dodatkowo, niezależnie od
tego, powiększenie gabarytu bloku chwytu C (przez grubszą ściankę)
zwiększa promieniowy nawis przejścia kołnierz→chwyt C, co przy
niezmienionym `cradle_transition_height` łamałoby próg 45° samo-podpierania
z v2 (przy `u_wall_thickness`=9mm bez innych zmian: kąt analityczny
~55.9°). Oba konflikty przedstawiono użytkownikowi wprost, z konkretnymi
liczbami, zamiast zgadywać rozwiązanie.

**Wybrane rozwiązanie** (spośród przedstawionych opcji, wybrane przez
użytkownika): podnieść `wall_to_barrel_center_min`, zamiast skracać
`collar_length` lub próbować zmieścić się w istniejącym zapasie.

**Docelowa wartość `u_wall_thickness`**: 6.0mm → **9.0mm** (+50%, wybrane
przez użytkownika spośród przedstawionych opcji +25%/+50%/własna wartość).

**Wyprowadzenie `cradle_transition_height`** (musi rosnąć razem z
`u_wall_thickness`, żeby kąt nawisu pozostał ≤45°):
```
half_x = u_wall_thickness + u_internal_width/2 = 9 + 15 = 24mm
half_y = u_arm_length/2 = 20mm  (bez zmian, u_arm_length nietknięte)
r = cradle_corner_fillet_radius = 19mm  (bez zmian)

max_cradle_radial_extent = hypot(half_x - r, half_y - r) + r
                          = hypot(24-19, 20-19) + 19
                          = hypot(5, 1) + 19 ≈ 24.10mm

transition_overhang = max_cradle_radial_extent - collar_diameter/2
                     = 24.10 - 16 = 8.10mm
```
Żeby zachować podobny margines bezpieczeństwa do progu 45° jak w
oryginalnej decyzji v2 (tam: zapas analityczny ~1.4°, zmierzony ~2.6°),
przyjęto **`cradle_transition_height` = 8.5mm** (zamiast minimalnego
8.10mm, które dawałoby dokładnie 45° bez żadnego zapasu):
```
transition_angle_deg = atan(8.10 / 8.5) ≈ 43.6°   (zapas analityczny ~1.4°)
```
Zgodnie z relacją z v2 (analityczna wartość jest konserwatywnym górnym
oszacowaniem), rzeczywisty kąt wyszedł korzystniej niż 43.6° analityczne.

**Zmierzone bezpośrednio na zbudowanej geometrii** (ta sama metoda co w
v2: próbkowanie przekrojów `arm.intersect(cienki_box)` co 0.5mm wysokości
od szczytu kołnierza do startu bloku C): promień rósł monotonicznie od
16.005mm (kołnierz) do 24.000mm (szczyt przejścia), dając kąt narostu
**~43.25°** — zapas **~1.75°** do progu 45°, potwierdzone przed wpisaniem
do specyfikacji (nie zgadnięte — patrz `.claude/CLAUDE.md`).

**Wyprowadzenie `wall_to_barrel_center_min`** (nowy `fixed_offset`):
```
fixed_offset = mounting_plate_thickness + nut_boss_length + collar_length
             + cradle_transition_height + u_wall_thickness
             + barrel_diameter_reference/2
             = 4 + 44 + 10 + 8.5 + 9 + 10 = 85.5mm

wall_to_barrel_center_min = fixed_offset + 0.5mm (ten sam zapas co w v2)
                           = 86.0mm
```
`wall_to_barrel_center_max` (140mm) pozostaje bez zmian — użytkownik nie
prosił o zmianę górnej granicy, a `rod_threaded_length` (112mm, bez zmian)
ma z nią jeszcze więcej zapasu niż w v2 (17.5mm zamiast 11.5mm), bo
maksymalny wysuw trzpienia się skrócił (140-85.5=54.5mm zamiast
140-79.5=60.5mm).

**Konsekwencja dla `u_arm_height`**: parametr ten (26mm, głębokość otwarcia
chwytu wzdłuż osi trzpienia) numerycznie odpowiadał w v2 formule
`u_wall_thickness + barrel_diameter_reference` (6+20=26), tak by lufa
referencyjna kończyła się dokładnie równo z otwartym czołem ramienia. Po
zmianie `u_wall_thickness` na 9mm ta zbieżność (9+20=29≠26) już nie
zachodzi. Świadomie pozostawione bez zmian — nie było przedmiotem żądania
użytkownika, nie jest wymogiem sprawdzanym przez
`check_engineering_preconditions()`, a jedyny efekt to lufa kończąca się
~3mm przed czołem ramienia zamiast dokładnie na czole (kosmetyczne, nie
funkcjonalne pogorszenie — lufa nadal swobodnie mieści się w otwarciu,
26mm > 20mm średnicy referencyjnej).

**Odrzucone alternatywy**: (a) zostawić `wall_to_barrel_center_min` na
80mm i skrócić `collar_length` i/lub `cradle_transition_height` zamiast —
odrzucone przez użytkownika na rzecz podniesienia dolnej granicy zakresu;
(b) mniejszy przyrost `u_wall_thickness` (+25% → 7.5mm) — odrzucone,
użytkownik wybrał +50%.

**Uzasadnienie całości**: zmiana geometrii na wyraźne życzenie użytkownika
(bardziej masywne podparcie lufy), z pełnym ujawnieniem użytkownikowi
dwóch niezależnych konfliktów inżynieryjnych (zapas wysuwu przy minimum,
kąt nawisu przejścia) przed wprowadzeniem jakiejkolwiek zmiany w
`specs/`, i z liczbami wyprowadzonymi analitycznie (nie zgadniętymi) —
zgodnie z `.claude/CLAUDE.md` ("Gdy specyfikacja jest niepełna lub
sprzeczna").

## 2026-08-21 — v2.2: kieszenie magnesów od strony ścianki (na wyraźne polecenie użytkownika)

**Żądanie użytkownika**: "w elemencie w którym są magnesy, zrób tak aby
były na odwrót". Niejednoznaczne sformułowanie — poproszono użytkownika o
doprecyzowanie zamiast zgadywać (patrz `.claude/CLAUDE.md`, "Gdy
specyfikacja jest niepełna lub sprzeczna"). Potwierdzone znaczenie:
odwrócić stronę płyty, od której wiercone są kieszenie na magnesy.

**Stan przed zmianą (v1–v2.1)**: kieszenie na magnesy wiercone od strony
**wewnętrznej** płyty (przeciwnej do ścianki sejfu), zostawiając
`magnet_pocket_wall_thickness` = 1mm materiału do strony **zewnętrznej**
(przyściennej) — magnes leży możliwie blisko metalowej ścianki dla
mocniejszego przyciągania, a kieszeń jest dostępna do wklejenia magnesu od
strony wewnętrznej (przed przyklejeniem płyty do ścianki).

**Zmiana (v2.2)**: kieszenie wiercone od strony **zewnętrznej**
(przyściennej), zostawiając `magnet_pocket_wall_thickness` materiału do
strony **wewnętrznej**. Konsekwencje fizyczne, przedstawione użytkownikowi
przed implementacją: magnes będzie oddalony od metalowej ścianki o 1mm
warstwy plastiku (jak poprzednio — ten wymiar się nie zmienił, zmienia się
tylko po której stronie leży), ale teraz magnes trzeba wkleić od strony
zewnętrznej, czyli **przed** przyklejeniem/przyłożeniem płyty do ścianki
sejfu (nie po). Nie zmienia to siły przyciągania (grubość ścianki nad
magnesem, `magnet_pocket_wall_thickness`, pozostaje 1.0mm — niezmieniona),
tylko stronę montażu.

**Implementacja** (`src/cad_project/rifle_mount/model.py::build_base_part`):
sketch kieszeni magnesów przeniesiony z `builder.faces().sort_by(Axis.Z)[-1]`
(góra/wewnętrzna) na `builder.faces().sort_by(Axis.Z)[0]` (dół/zewnętrzna/
przyścienna) — znak `extrude(amount=-magnet_thickness, mode=SUBTRACT)`
pozostał bez zmian (ujemny offset zawsze wycina do wnętrza względem
normalnej wybranej ściany, niezależnie od tego, którą ścianę wybrano).
Selekcja ściany tulei gwintowanej (`boss_base_face`, nadal góra/
wewnętrzna) nie wymagała zmiany — jest niezależna od strony kieszeni na
magnesy.

**Weryfikacja**: zbudowano Część A i sprawdzono bezpośrednio (klasyfikator
brył OCCT, punkt-w-bryle) że punkt tuż przy dolnej (zewnętrznej) ścianie w
osi otworu na magnes leży **poza** bryłą (pusta kieszeń), a punkt tuż przy
górnej (wewnętrznej) ścianie leży **wewnątrz** bryły (materiał) — potwierdza
odwrócenie kierunku, nie tylko wyliczenie. Bryła nadal `is_valid=True`,
dokładnie 1 bryła, objętość praktycznie niezmieniona względem v2.1
(30622.828 mm³ vs 30622.809 mm³ — różnica rzędu numerycznego szumu OCCT z
operacji boolowskich na przeciwnej ścianie, nie błąd). Wszystkie testy
`pytest tests/rifle_mount/` przechodzą, pełny pipeline (`build → measure →
validate → export → render`) kończy się `status: passed`.

**Bez zmian**: `magnet_pocket_wall_thickness` (1.0mm), pozycje magnesów
(`magnet_edge_offset`), liczba magnesów, wszystkie pozostałe parametry
Części A i całej Części B.

**Uzasadnienie**: zmiana geometrii na wyraźne (po doprecyzowaniu) życzenie
użytkownika, z jawnym ujawnieniem konsekwencji montażowej (kolejność
wklejania magnesów względem montażu do ścianki) przed implementacją, i z
weryfikacją bezpośrednio na zbudowanej bryle, nie tylko na kodzie.

## 2026-08-25 — v3: paski magnetyczne zamiast dysków (na wyraźne polecenie użytkownika)

**Żądanie użytkownika**: magnesy w rzeczywistości nie są dyskami
neodymowymi, tylko samoprzylepnymi paskami magnetycznymi z zestawu do
identyfikatorów (12-częściowy zestaw, produkt z Amazon.pl, wymiar
4×45×13mm), i płyta mocująca ma być pogrubiona tak, żeby zmieścić dwa
takie paski.

**Doprecyzowanie z użytkownikiem przed implementacją** (`AskUserQuestion`,
zgodnie z `.claude/CLAUDE.md` — "Gdy specyfikacja jest niepełna lub
sprzeczna"): oryginalne zdanie użytkownika było niejednoznaczne (ile
kieszeni, ile pasków w kieszeni, czy paski zastępują dyski czy są
dodatkowe, czy płyta może się powiększyć). Potwierdzone odpowiedzi:

1. Paski **całkowicie zastępują** 4 dyski neodymowe (nie są dodatkiem).
2. **Dwie kieszenie**, po **jednym pasku** w każdej (nie stos 2 pasków w
   jednej kieszeni) — czyli 2 paski łącznie, każdy 4mm grubości.
3. Płyta mocująca **może się powiększyć** ponad 60×60mm.

**Konflikt inżynieryjny wykryty i ujawniony użytkownikowi przed zmianą
`specs/`** (zgodnie z `.claude/CLAUDE.md`): pasek ma grubość 4mm (było
3mm dla dysku), więc `mounting_plate_thickness` musi wzrosnąć z 4.0mm do
5.0mm (reguła: `mounting_plate_thickness = magnet_thickness +
magnet_pocket_wall_thickness`, 4+1=5). Ten parametr wchodzi jednak do
stałego offsetu łańcucha wymiarowego Części B (patrz "Zależność
geometryczna" w `spec.md`):

```
offset (v2.2) = mounting_plate_thickness(4) + nut_boss_length(44) + collar_length(10)
              + cradle_transition_height(8.5) + u_wall_thickness(9)
              + barrel_diameter_reference/2(10)
              = 85.5 mm
offset (v3, wall_to_barrel_center_min niezmienione) = 86.5 mm
wysuw_min = wall_to_barrel_center_min(86.0) - offset(86.5) = -0.5 mm  ← NIEMOŻLIWE
```

Ujemny wysuw jest geometrycznie niemożliwy (mechanizm nie może wkręcić
się "głębiej niż zero") — dokładnie ten sam rodzaj konfliktu co przy
podnoszeniu `u_wall_thickness` w v2.1. Przedstawiono użytkownikowi przez
`AskUserQuestion` z rekomendowaną opcją; użytkownik wybrał **podniesienie
`wall_to_barrel_center_min` z 86.0mm do 87.0mm**, żeby przywrócić ten sam
+0.5mm zapasu co przed zmianą (zamiast zmniejszania innego parametru
stałego offsetu, np. `nut_boss_length` czy `cradle_transition_height`,
które są tam z innych, niezależnie wyprowadzonych powodów).

**Układ kieszeni na płycie** (potwierdzony z użytkownikiem,
rekomendowany wariant): dwie prostokątne kieszenie 45×13mm, dłuższym
wymiarem równoległe do krawędzi płyty (oś X), wyśrodkowane w X (`x=0`),
symetryczne w Y po przeciwnych stronach środka płyty/osi tulei
gwintowanej — jedna nad, jedna pod. Wyprowadzenie liczb:

* Tuleja gwintowana ma promień zewnętrzny `nut_boss_outer_diameter/2` =
  (25 + 2×4)/2 = **16.5mm**. Żeby kieszeń (rzutowana na płaszczyznę
  płyty) nie kolidowała z tuleją (ten sam wymóg co przy dyskach w v1–v2.2,
  mimo że kieszenie i tuleja są fizycznie po przeciwnych stronach płyty —
  zachowany dla spójności konstrukcyjnej/wizualnej), potrzeba:
  `magnet_center_offset_y - magnet_pocket_width/2 > 16.5mm`.
  Przyjęto `magnet_center_offset_y = 24.0mm` → najbliższa krawędź kieszeni
  w odległości 24 - 6.5 = **17.5mm** od osi, czyli **1.0mm** prześwitu do
  tulei.
* Płyta musi pomieścić obie kieszenie z zapasem do krawędzi:
  wzdłuż X potrzeba `mounting_plate_size/2 > magnet_pocket_length/2` (=
  22.5mm), wzdłuż Y potrzeba `mounting_plate_size/2 >
  magnet_center_offset_y + magnet_pocket_width/2` (= 30.5mm). Przyjęto
  `mounting_plate_size = 72.0mm` (kwadrat) → zapas 13.5mm w X, 5.5mm w Y
  do krawędzi płyty.

**Zaimplementowane zmiany parametrów** (`specs/rifle-mount/parameters.yaml`):

| Parametr | v2.2 | v3 |
|---|---|---|
| `magnet_diameter` (usunięty) → `magnet_pocket_length` / `magnet_pocket_width` | Ø12.0mm | 45.0×13.0mm |
| `magnet_thickness` | 3.0mm | 4.0mm |
| `magnet_count` | 4 | 2 |
| `mounting_plate_size` | 60.0mm | 72.0mm |
| `mounting_plate_thickness` | 4.0mm | 5.0mm |
| `magnet_edge_offset` (usunięty) → `magnet_center_offset_y` | 10.0mm (od krawędzi) | 24.0mm (od środka) |
| `wall_to_barrel_center_min` | 86.0mm | 87.0mm |

**Implementacja** (`src/cad_project/rifle_mount/model.py::build_base_part`):
sketch kieszeni magnesów zmieniony z `Circle(magnet_diameter/2)` na
`Rectangle(magnet_pocket_length, magnet_pocket_width)`; `_magnet_positions()`
zwraca teraz `((0, +magnet_center_offset_y), (0, -magnet_center_offset_y))`
zamiast czterech narożników. Kierunek wiercenia (od strony zewnętrznej/
przyściennej, `magnet_pocket_wall_thickness` materiału do wewnętrznej) —
niezmieniony z v2.2.
`check_engineering_preconditions()` (`parameters.py`) zastępuje stare
sprawdzenia (promień/rozstaw dysków, kolizja z tuleją liczona z odległości
promieniowej narożnika) nowymi sprawdzeniami dla prostokątnych kieszeni
(brak nakładania w Y, mieszczenie się w płycie w X i Y, prześwit do tulei
liczony jako najbliższa krawędź prostokąta wzdłuż osi Y, bo kieszeń
rozciąga się przez `x=0`).

**Bez zmian**: kierunek wiercenia kieszeni (v2.2), `magnet_pocket_wall_thickness`
(1.0mm), wszystkie parametry Części B poza pochodną zmianą
`wall_to_barrel_center_min` (stały offset łańcucha wymiarowego pozostaje
z tą samą strukturą, tylko z nowym `mounting_plate_thickness`).

**Uzasadnienie całości**: zmiana typu/kształtu/liczby magnesów na wyraźne
życzenie użytkownika, z pełnym doprecyzowaniem niejednoznacznego żądania
i pełnym ujawnieniem wykrytego konfliktu inżynieryjnego (ujemny wysuw
minimalny) przed wprowadzeniem jakiejkolwiek zmiany w `specs/`, z liczbami
wyprowadzonymi analitycznie (nie zgadniętymi) — zgodnie z
`.claude/CLAUDE.md` ("Gdy specyfikacja jest niepełna lub sprzeczna").
