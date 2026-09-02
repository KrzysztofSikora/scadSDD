# Log decyzji projektowych — Premium Self-Watering Planter

## 2026-09-02 — Nowy, trzeci niezależny model obok `bracket-001` i `magnetic-rifle-mount-001`

**Żądanie użytkownika**: nowy projekt — doniczka, z której powstanie
zestaw plików STL do sprzedaży na Etsy. Najpierw jedna "premium" doniczka
z samonawadnianiem; potem wzór ścianki ma być wymienny między wariantami
serii, przy zachowanych rozmiarach/kształcie.

**Decyzja**: nowa specyfikacja (`specs/planter/`) i nowy moduł kodu
(`src/cad_project/planter/`), zamiast rozszerzania istniejących modeli —
ten sam wzorzec co przy dodaniu `magnetic-rifle-mount-001`. Reużyto
generyczne moduły `measurements.py`, `exports.py`, `rendering.py`. Osobny
CLI (`python -m cad_project.planter.cli`) i osobne drzewo wyjściowe
(`output/planter/`).

**Doprecyzowanie wymagań** (`AskUserQuestion`, zgodnie z
`.claude/CLAUDE.md` — "Gdy specyfikacja jest niepełna lub sprzeczna",
skoro żądanie nie precyzowało rozmiaru, konstrukcji ani mechanizmu
knota):

1. Rozmiar bazowy — użytkownik poprosił o sprawdzenie na Etsy jakie
   rozmiary mają najczęściej kupowane doniczki STL, zamiast wyboru z
   proponowanej listy.
2. Konstrukcja samonawadniania: **2 części** — wkład na ziemię + zbiornik
   pod spodem (wybór rekomendowany, potwierdzony).
3. Mechanizm podciągania wody: **wydrukowany kanał/komin kapilarny, bez
   dodatkowych części** (nie sznurek/knot bawełniany) — wybór świadomie
   opisany jako "bardziej złożona geometria i mniej pewne działanie
   fizyczne", wybrany mimo to.
4. Wymienny wzór: **tylko zewnętrzna ścianka doniczki ma wzór/relief**,
   reszta (rdzeń funkcjonalny) identyczna między wariantami (wybór
   rekomendowany, potwierdzony).

## 2026-09-02 — Wybór rozmiaru bazowego serii (research rynkowy)

Na wyraźne polecenie użytkownika sprawdzono (WebSearch) rozmiary
najpopularniejszych samonawadniających doniczek STL na Etsy zamiast
zgadywać:

* Przykładowy bestseller ("Plant Pot STL Self-watering With Unique Water
  Level Indicator") drukuje się w 100% jako 140×140×105mm.
* Kolekcja wielorozmiarowa popularnego wzoru (Mushroom Forest Planter):
  S 85×72mm, M 113×97mm, L 140×120mm (szerokość×wysokość).
* Ogólny zakres popularnych doniczek STL na Etsy/Printables/Cults:
  ok. 90-140mm szerokości, 70-120mm wysokości.

**Decyzja**: `insert_top_outer_diameter = 130.0mm`,
`insert_body_height = 110.0mm` — w środku zaobserwowanego popularnego
zakresu, dość duże żeby zmieścić realny mechanizm samonawadniania
(zbiornik + rdzeń kapilarny), ale wciąż drukowalne na typowym stole
180×180mm i mniejszym.

Sources:
- [Plant Pot STL Self-watering With Unique Water Level Indicator](https://www.etsy.com/listing/4343219157/plant-pot-stl-self-watering-with-unique)
- [Enchanting Mushroom Forest Planter](https://cults3d.com/en/3d-model/art/enchanting-mushroom-forest-planter-3d-print-stl-files)

## 2026-09-02 — Architektura złożenia: spódnica + gardziel, nie zagnieżdżenie na pełną głębokość

**Problem**: pierwszy pomysł (insert zagnieżdżony głęboko w zbiorniku,
osobna szeroka "kryza" oparcia) tworzył sprzeczność wymiarową — insert
wysokości 110mm nie mógł jednocześnie mieć dna tuż nad wodą (zbiornik
głęboki tylko 40mm) i sięgać dnem do prawdziwego dna zbiornika.

**Rozwiązanie**: klasyczny układ "false bottom" — insert i zbiornik
**stykają się tylko w jednej płaszczyźnie** (Z=0): dolna krawędź insertu
(pierścień oparcia, szerokość ~13mm) spoczywa bezpośrednio na górnej
krawędzi zbiornika, a cienkościenna **spódnica** (Ø99.4mm, wysokość 8mm)
zwisająca ze środka dna insertu wchodzi na wcisk (luz `fit_clearance`
0.3mm) w gardziel zbiornika — funkcja czysto pozycjonująca/centrująca,
nie nośna. Zbiornik jest prostym walcem o stałej średnicy na całej
głębokości (bez osobnego "kołnierza") — górna część tej samej komory po
prostu pełni rolę gardzieli.

## 2026-09-02 — Wyprowadzenie marginesów: spódnica, zasłonięcie szwu, dziubek

Wszystkie trzy poniższe marginesy wymagały `insert_bottom_outer_diameter`
zauważalnie większego niż `reservoir_mouth_outer_diameter` — stąd
subtelne zwężenie insertu ku dołowi (126mm dół vs 130mm góra, kąt ~1°),
nie odwrotnie (insert szerszy u góry, klasyczny kształt doniczki).

1. **Spódnica (derived `spigot_outer_diameter = reservoir_mouth_inner_diameter
   − 2×fit_clearance` = 100 − 0.6 = 99.4mm) vs `insert_bottom_outer_diameter`
   (126mm)**: margines pierścienia oparcia = (126−99.4)/2 = 13.3mm —
   wymagane > 2mm w `check_engineering_preconditions()`, tu duży zapas.
2. **`reservoir_mouth_outer_diameter` (derived = 100+2×3 = 106mm) vs
   `insert_bottom_outer_diameter` (126mm)**: zasłonięcie szwu
   (10mm na stronę) — insert w pełni zakrywa zbiornik z góry, "cache-pot"
   look.
3. **Dziubek do nalewania**: zamontowany płasko na zewnętrznej ściance
   zbiornika (oś na promieniu `reservoir_mouth_outer_diameter/2` = 53mm),
   musi wystawać ponad Z=0 (`fill_spout_top_protrusion` = 15mm) żeby być
   dostępny mimo rozszerzającej się ścianki insertu powyżej. Sprawdzenie:
   `insert_bottom_outer_diameter/2 − (reservoir_mouth_outer_diameter/2 +
   fill_spout_outer_diameter/2)` = 63 − (53+5) = 5mm margines (wymagane
   > 2mm). **Pierwsza próba** z `insert_bottom_outer_diameter = 114mm`
   dawała margines ~1mm (za mało, praktycznie stykający się z rozszerzającą
   się ścianką) — podniesiono do 126mm właśnie dla tego marginesu.

## 2026-09-02 — Bug: `Align.CENTER` na częściowym `Cone` (arc_size) centruje bounding box klina, nie oś obrotu

**Objaw**: pierwsza implementacja żłobień (subtract N klinowych `Cone`
z `arc_size=pattern_flute_width_deg`, `align=(CENTER,CENTER,MIN)`,
rozmieszczonych przez `PolarLocations(0, N)`) budowała się bez błędu
(1 bryła, `is_valid=True`), ale wizualnie żłobienia były niewidoczne w
podglądzie PNG. Wstępna analiza objętości sugerowała nawet, że któryś z
wcześniejszych testów pokazywał głębokość żłobienia inną niż zadeklarowana
(pozorna rozbieżność ~0.9mm) — po dokładniejszym sprawdzeniu (próbkowanie
siatki trójkątów na konkretnych kątach/Z, patrz niżej) okazało się, że
było to fałszywe dopasowanie do niepowiązanej powierzchni wewnętrznej
komory (nie do dna żłobienia) — właściwy test był inny.

**Właściwa diagnoza**: porównanie objętości bryły PRZED i PO operacji
`SUBTRACT` żłobień pokazało **różnicę 0.0mm³** — żłobienia nic nie
wycinały, niezależnie od `pattern_flute_depth` (0.8mm i 1.5mm dawały
identyczny wynik końcowy). Sprawdzenie samego narzędzia tnącego
(`Cone(..., arc_size=6, align=(Align.CENTER, Align.CENTER, Align.MIN))`)
w izolacji ujawniło przyczynę: dla **częściowego** stożka (arc_size < 360)
Build123d liczy `Align.CENTER` względem **bounding box wycinka klina**,
nie względem prawdziwej osi obrotu (promień 0) — dla klina 0-6° to
przesuwa całą bryłę o promień(!) w bok, całkowicie z dala od osi Z, więc
przy rotacji przez `PolarLocations` narzędzie nigdy nie przecinało
głównej bryły w zamierzonym miejscu.

**Naprawa**: `align=(Align.MIN, Align.MIN, Align.MIN)` zamiast `CENTER` —
dla wycinka klina 0°-`arc_size`, `Align.MIN` w X i Y ustawia wierzchołek
klina (promień 0, prawdziwa oś obrotu) dokładnie w lokalnym (0,0),
dokładnie tam gdzie `PolarLocations` oczekuje punktu obrotu. Zweryfikowane
bezpośrednio: objętość odjęta wzrosła z 0.0mm³ do ~14 042mm³ łącznie
(~585mm³/żłobienie, rząd wielkości zgodny z szacunkiem analitycznym
głębokość×szerokość_łuku×wysokość ≈ 1005mm³/żłobienie — różnica
wynika z tego, że rzeczywisty klin zbiega do zera przy promieniu 0, a
przybliżenie analityczne zakłada prostokąt), a w podglądzie PNG żłobienia
są wyraźnie widoczne jako pionowe pasy na całym obwodzie.

**Wniosek dla przyszłych wariantów wzoru**: każda nowa implementacja
`_carve_wall_pattern()` używająca częściowych (`arc_size < 360`)
prymitywów Build123d musi weryfikować **bezpośrednio na zbudowanej
bryle** (porównanie objętości przed/po, nie tylko brak wyjątku), że
narzędzie faktycznie coś wycina — brak wyjątku i `is_valid=True` **nie
gwarantują**, że operacja miała jakikolwiek efekt. Dodano to jako punkt
Definition of Done w `spec.md`.

## 2026-09-02 — Fillet tylko zewnętrznej krawędzi górnej

**Problem**: `fillet()` na obu krawędziach (zewnętrznej i wewnętrznej)
górnej ściany insertu (promień 2.0mm, zaokrąglenie zadeklarowane
pierwotnie w parametrach) rzucał `Standard_Failure` z OCCT — ściana
czołowa ma szerokość dokładnie `insert_wall_thickness` (2.4mm), za wąska
żeby zmieścić dwa zaokrąglenia po 2mm naraz (2+2=4mm > 2.4mm).

**Naprawa**: `top_rim_fillet_radius` obniżone z 2.0mm do 1.2mm (< grubość
ścianki, z zapasem), i w `model.py` zaokrąglana jest **tylko** krawędź
zewnętrzna (`edges().sort_by(SortBy.RADIUS)[-1]`), nie obie. Zweryfikowane
bezpośrednio budową (1 bryła, `is_valid=True`). Dodano jawne sprawdzenie
`top_rim_fillet_radius < insert_wall_thickness` w
`check_engineering_preconditions()`.

Przy okazji odkryto **drugą** przyczynę tego samego błędu: żłobienia
sięgające aż do górnej krawędzi tworzyły postrzępioną (nieokrągłą)
krawędź czołową, na której fillet też zawodzi niezależnie od promienia.
Naprawione dodaniem `pattern_flute_end_margin` (5.0mm) — żłobienia nie
sięgają do żadnej z krawędzi, zostawiając gładki, w pełni okrągły pasek
na górze (do zaokrąglenia) i na dole.

## 2026-09-02 — Architektura wymiennego wzoru (dla przyszłych wariantów serii)

Zgodnie z żądaniem użytkownika ("potem z tego projektu będzie można
podmieniać wzór a rozmiary i kształty będą takie same w seriach"),
geometria jest podzielona na dwie wyraźnie oddzielone warstwy:

* **Rdzeń** (`build_insert_part`, `build_reservoir_part` poza wywołaniem
  `_carve_wall_pattern`): wszystkie wymiary funkcjonalne — nigdy nie
  powinny się zmieniać między wariantami serii.
* **Wzór** (`_carve_wall_pattern` + blok `pattern_*` w `parameters.yaml`):
  jedyna część geometrii przeznaczona do podmiany. Nowy wariant = nowa
  implementacja tej jednej funkcji (inny kształt narzędzia tnącego, inny
  wzór rozmieszczenia) + odpowiadający jej blok `pattern_*` parametrów, z
  zachowaniem sygnatury `_carve_wall_pattern(builder, bottom_r, top_r) ->
  None`, wywoływanej dokładnie raz, zaraz po operacji `offset` (shell), a
  przed pogrubieniem dna. Ta funkcja **nigdy** nie powinna wymagać zmiany
  żadnego wymiaru poza blokiem `pattern_*`.

Nie zbudowano generycznego systemu "wtyczek"/rejestru wzorów (byłaby to
abstrakcja ponad to, czego wymaga jeden zaimplementowany dotąd wariant —
patrz `.claude/CLAUDE.md` o unikaniu przedwczesnej abstrakcji). Gdy
powstanie drugi faktyczny wariant wzoru, ten punkt decyzji jest miejscem
do ponownej oceny, czy taki system nabiera sensu.

**Uzasadnienie całości**: nowy, trzeci model repozytorium, z rozmiarem
opartym na realnym researchu rynkowym (nie zgadniętym), z jawnym
zastrzeżeniem o niepewności fizycznej mechanizmu kapilarnego (ujawnionym
użytkownikowi przed wyborem), z architekturą jawnie oddzielającą
niezmienny rdzeń od wymiennego wzoru zgodnie z wymaganiem serii, i z
dwoma błędami geometrii (fillet, brak-efektu żłobień) znalezionymi i
naprawionymi przez bezpośrednią weryfikację na zbudowanej bryle, nie
tylko przez brak wyjątku — zgodnie z `.claude/CLAUDE.md`.
