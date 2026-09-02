# Specyfikacja modelu CAD: Doniczka premium z samonawadnianiem

> **Ten plik jest źródłem prawdy dla wymagań.** Nie zmieniaj wartości,
> tolerancji ani reguł bez wyraźnego polecenia człowieka. Zobacz
> `.claude/CLAUDE.md` oraz `specs/planter/constraints.md` i
> `specs/planter/decisions.md`.

## Metadane

| Pole                  | Wartość                              |
|------------------------|----------------------------------------|
| Nazwa projektu        | Premium Self-Watering Planter          |
| Identyfikator modelu  | `self-watering-planter-001`            |
| Wersja specyfikacji   | `1.0.0`                                |
| Jednostki             | milimetry (mm)                         |

**Iteracja 1 (v1, ta wersja)**: pierwszy model serii doniczek do sprzedaży
jako pliki STL na Etsy. Ustala **rdzeń serii** — rozmiar, kształt,
mechanizm samonawadniania, wszystkie wymiary funkcjonalne — który ma
pozostać **identyczny** we wszystkich przyszłych wariantach; jedynym
elementem geometrii przeznaczonym do wymiany między wariantami jest wzór
płytkich żłobień na zewnętrznej ściance wkładu (`pattern_*` w
`parameters.yaml`) — patrz "Architektura wymiennego wzoru" w
`specs/planter/decisions.md`.

## Opis funkcjonalny

Doniczka dwuczęściowa z pasywnym samonawadnianiem:

* **Insert ("wkład")** — stożkowa (lekko zwężająca się ku dołowi) donica
  na ziemię, z żłobioną ścianką zewnętrzną (wzór "premium fluted"),
  perforowanym rdzeniem kapilarnym zwisającym ze środka dna w głąb
  zbiornika, otworami drenażowymi/wentylacyjnymi w dnie i cienkościenną
  spódnicą pozycjonującą pod spodem.
* **Reservoir ("zbiornik")** — płytki zbiornik na wodę, na/w którym
  spoczywa wkład (spódnica wkładu wchodzi na wcisk w gardziel zbiornika),
  z zewnętrznym dziubkiem do nalewania wody bez zdejmowania wkładu, z
  otworem przelewowym ustalającym maksymalny poziom wody i z nóżkami pod
  spodem.

Rdzeń kapilarny **nie jest** litym plastikowym knotem — to perforowana
rura, którą użytkownik wypełnia ziemią; to ziemia w rurze (mająca
bezpośredni kontakt z wodą w zbiorniku przez szczeliny i otwarty dolny
koniec) faktycznie podciąga wilgoć, korzystając z naturalnej kapilarności
substratu — patrz `specs/planter/constraints.md` ("Brak gwarancji
podciągania wody przez sam plastik") po pełne zastrzeżenie.

## Parametry

Maszynowym źródłem prawdy jest [`specs/planter/parameters.yaml`](parameters.yaml).
Fragment poniżej jest jego dosłowną kopią, weryfikowaną automatycznie
(`tests/planter/test_spec_compliance.py`, parser YAML, nigdy regex po
Markdownie).

| Nazwa | ID techniczne | Wartość | Jednostka | Tolerancja |
|---|---|---|---|---|
| Średnica góra wkładu | `insert_top_outer_diameter` | 130.0 | mm | ±0.3 |
| Średnica dół wkładu | `insert_bottom_outer_diameter` | 126.0 | mm | ±0.3 |
| Wysokość ścianki wkładu | `insert_body_height` | 110.0 | mm | ±0.3 |
| Grubość ścianki wkładu | `insert_wall_thickness` | 2.4 | mm | ±0.1 |
| Grubość dna wkładu | `insert_floor_thickness` | 4.0 | mm | ±0.2 |
| Zaokrąglenie górnej krawędzi | `top_rim_fillet_radius` | 1.2 | mm | ±0.1 |
| Średnica otworu drenażowego | `drainage_hole_diameter` | 4.0 | mm | ±0.1 |
| Liczba otworów drenażowych | `drainage_hole_count` | 8 | szt. | 0 |
| Okrąg rozmieszczenia otworów | `drainage_hole_circle_diameter` | 90.0 | mm | ±0.5 |
| Wysokość spódnicy | `spigot_height` | 8.0 | mm | ±0.2 |
| Luz pasowania spódnicy | `fit_clearance` | 0.3 | mm | ±0.05 |
| Średnica zewn. rdzenia kapilarnego | `capillary_tube_outer_diameter` | 24.0 | mm | ±0.3 |
| Średnica wewn. rdzenia kapilarnego | `capillary_tube_inner_diameter` | 18.0 | mm | ±0.3 |
| Wystawanie rdzenia w ziemię | `capillary_tube_soil_protrusion` | 60.0 | mm | ±0.3 |
| Szerokość szczeliny rdzenia | `capillary_tube_slot_width` | 2.0 | mm | ±0.1 |
| Liczba szczelin rdzenia | `capillary_tube_slot_count` | 6 | szt. | 0 |
| Prześwit rdzenia nad dnem zbiornika | `capillary_tube_reservoir_clearance` | 3.0 | mm | ±0.2 |
| Wewn. średnica zbiornika | `reservoir_mouth_inner_diameter` | 100.0 | mm | ±0.3 |
| Grubość ścianki zbiornika | `reservoir_wall_thickness` | 3.0 | mm | ±0.1 |
| Głębokość komory zbiornika | `reservoir_cavity_depth` | 40.0 | mm | ±0.3 |
| Wysokość nóżek zbiornika | `reservoir_foot_height` | 4.0 | mm | ±0.2 |
| Średnica nóżek zbiornika | `reservoir_foot_diameter` | 10.0 | mm | ±0.3 |
| Liczba nóżek zbiornika | `reservoir_foot_count` | 3 | szt. | 0 |
| Średnica zewn. dziubka | `fill_spout_outer_diameter` | 10.0 | mm | ±0.2 |
| Średnica wewn. dziubka | `fill_spout_inner_diameter` | 6.0 | mm | ±0.2 |
| Wystawanie dziubka ponad krawędź | `fill_spout_top_protrusion` | 15.0 | mm | ±0.3 |
| Prześwit dna dziubka | `fill_spout_bottom_clearance` | 3.0 | mm | ±0.2 |
| Średnica otworu przelewowego | `overflow_hole_diameter` | 5.0 | mm | ±0.2 |
| Wysokość otworu przelewowego | `overflow_hole_height_from_floor` | 28.0 | mm | ±0.3 |
| Gęstość materiału (opcjonalna) | `material_density` | 1.24e-6 | kg/mm³ | — |
| Liczba żłobień wzoru | `pattern_flute_count` | 24 | szt. | 0 |
| Głębokość żłobień wzoru | `pattern_flute_depth` | 1.5 | mm | ±0.1 |
| Szerokość kątowa żłobienia | `pattern_flute_width_deg` | 6.0 | ° | ±0.5 |
| Margines żłobień od krawędzi | `pattern_flute_end_margin` | 5.0 | mm | ±0.5 |

### Fragment maszynowy (kopia `specs/planter/parameters.yaml`)

```yaml
project:
  name: "Premium Self-Watering Planter"
  model_id: "self-watering-planter-001"
  spec_version: "1.0.0"
  units: "mm"

parameters:
  # --- Insert ("wkład") -------------------------------------------------
  - id: insert_top_outer_diameter
    name: "Średnica zewnętrzna wkładu (góra)"
    value: 130.0
    unit: mm
    tolerance: 0.3
    description: >
      Średnica zewnętrzna wkładu na ziemię przy górnej krawędzi. Dobrana
      na podstawie researchu najpopularniejszych samonawadniających
      doniczek STL na Etsy (typowy zakres ok. 90-140mm) — patrz
      specs/planter/decisions.md ("Wybór rozmiaru bazowego serii").

  - id: insert_bottom_outer_diameter
    name: "Średnica zewnętrzna wkładu (dół, przy oparciu)"
    value: 126.0
    unit: mm
    tolerance: 0.3
    description: >
      Średnica zewnętrzna wkładu przy dolnej krawędzi (tam gdzie wkład
      opiera się na zbiorniku). Celowo bliska insert_top_outer_diameter
      (subtelne zwężenie, ~1° kąta), żeby zostawić bezpieczny margines
      między rozszerzającą się ścianką wkładu a dziubkiem do nalewania
      wody (fill_spout_*) zamontowanym na zbiorniku poniżej — patrz
      wyprowadzenie w specs/planter/decisions.md.

  - id: insert_body_height
    name: "Wysokość ścianki wkładu"
    value: 110.0
    unit: mm
    tolerance: 0.3
    description: >
      Wysokość stożkowej ścianki wkładu, licząc od dolnej krawędzi
      (płaszczyzna oparcia na zbiorniku, Z=0) do górnej krawędzi.

  - id: insert_wall_thickness
    name: "Grubość ścianki wkładu"
    value: 2.4
    unit: mm
    tolerance: 0.1
    description: >
      Grubość ścianki wkładu (i spódnicy pozycjonującej pod spodem) —
      ok. 6 obwodów przy dyszy 0.4mm, standard dla solidnej doniczki.

  - id: insert_floor_thickness
    name: "Grubość dna wkładu"
    value: 4.0
    unit: mm
    tolerance: 0.2
    description: >
      Grubość dna wkładu (pogrubiona względem ścianki bocznej, żeby
      solidnie utrzymać otwory drenażowe i rdzeń kapilarny) — dobudowana
      jako dodatkowa warstwa wewnątrz po operacji shell, patrz model.py.

  - id: top_rim_fillet_radius
    name: "Promień zaokrąglenia górnej krawędzi wkładu"
    value: 1.2
    unit: mm
    tolerance: 0.1
    description: >
      Zaokrąglenie tylko zewnętrznej krawędzi górnego otworu wkładu (nie
      wewnętrznej — przy grubości ścianki 2.4mm zaokrąglenie obu krawędzi
      naraz jest geometrycznie niewykonalne na tak wąskiej powierzchni
      czołowej; zweryfikowane bezpośrednio budową w
      specs/planter/decisions.md).

  - id: drainage_hole_diameter
    name: "Średnica otworu drenażowego/wentylacyjnego"
    value: 4.0
    unit: mm
    tolerance: 0.1
    description: >
      Średnica każdego z otworów w dnie wkładu (napowietrzenie/drenaż
      nadmiaru wody z ziemi, nie są głównym mechanizmem nawadniania).

  - id: drainage_hole_count
    name: "Liczba otworów drenażowych"
    value: 8
    unit: count
    tolerance: 0
    description: Liczba otworów rozmieszczonych równomiernie na okręgu drainage_hole_circle_diameter.

  - id: drainage_hole_circle_diameter
    name: "Średnica okręgu rozmieszczenia otworów drenażowych"
    value: 90.0
    unit: mm
    tolerance: 0.5
    description: >
      Średnica okręgu, na którym leżą środki otworów drenażowych w dnie
      wkładu — dobrana tak, by nie kolidować ani z rdzeniem kapilarnym w
      środku, ani ze ścianką boczną.

  - id: spigot_height
    name: "Wysokość spódnicy pozycjonującej"
    value: 8.0
    unit: mm
    tolerance: 0.2
    description: >
      Wysokość cienkościennej spódnicy zwisającej pod dnem wkładu, która
      wchodzi (na wcisk) w gardziel zbiornika i centruje/pozycjonuje
      wkład — patrz specs/planter/decisions.md.

  - id: fit_clearance
    name: "Luz pasowania spódnicy w gardzieli zbiornika"
    value: 0.3
    unit: mm
    tolerance: 0.05
    description: >
      Promieniowy luz między zewnętrzną średnicą spódnicy a wewnętrzną
      średnicą gardzieli zbiornika (pasowanie wsuwane, typowe dla FDM).

  # --- Rdzeń kapilarny (perforowana rura) --------------------------------
  - id: capillary_tube_outer_diameter
    name: "Średnica zewnętrzna rdzenia kapilarnego"
    value: 24.0
    unit: mm
    tolerance: 0.3
    description: >
      Średnica zewnętrzna centralnej, perforowanej rury łączącej wodę w
      zbiorniku z ziemią we wkładzie. Rura jest wypełniana ziemią przez
      użytkownika — to ziemia w rurze faktycznie podciąga wodę
      (kapilarność ziemi/substratu), nie sam plastik — patrz
      specs/planter/constraints.md ("Brak gwarancji podciągania wody
      przez sam plastik").

  - id: capillary_tube_inner_diameter
    name: "Średnica wewnętrzna rdzenia kapilarnego"
    value: 18.0
    unit: mm
    tolerance: 0.3
    description: Średnica wewnętrzna (bore) rury kapilarnej — tu użytkownik wsypuje ziemię.

  - id: capillary_tube_soil_protrusion
    name: "Wysokość wystawania rdzenia w ziemię"
    value: 60.0
    unit: mm
    tolerance: 0.3
    description: >
      Wysokość, na jaką rdzeń kapilarny wystaje ponad dno wkładu (Z=0) w
      głąb komory na ziemię — tak by korzenie miały łatwy dostęp.

  - id: capillary_tube_slot_width
    name: "Szerokość szczeliny w ściance rdzenia"
    value: 2.0
    unit: mm
    tolerance: 0.1
    description: >
      Szerokość pionowych szczelin wyciętych w ściance rury kapilarnej na
      całej jej długości — pozwalają ziemi w rurze mieć bezpośredni
      kontakt z wodą/powietrzem na zewnątrz rury.

  - id: capillary_tube_slot_count
    name: "Liczba szczelin w rdzeniu kapilarnym"
    value: 6
    unit: count
    tolerance: 0
    description: >
      Liczba pionowych szczelin rozmieszczonych równomiernie wokół
      obwodu rury (między nimi zostają żebra nośne).

  - id: capillary_tube_reservoir_clearance
    name: "Prześwit dna rdzenia nad dnem zbiornika"
    value: 3.0
    unit: mm
    tolerance: 0.2
    description: >
      Odstęp między dolnym końcem rdzenia kapilarnego a wewnętrznym dnem
      zbiornika — rdzeń sięga blisko dna (żeby działać nawet przy niskim
      poziomie wody), ale go nie dotyka (nie blokuje przepływu wody pod
      spodem).

  # --- Zbiornik ("zbiornik") --------------------------------------------
  - id: reservoir_mouth_inner_diameter
    name: "Wewnętrzna średnica gardzieli/komory zbiornika"
    value: 100.0
    unit: mm
    tolerance: 0.3
    description: >
      Wewnętrzna średnica zbiornika, stała na całej głębokości
      (reservoir_cavity_depth) — górna część tej samej komory pełni
      funkcję gardzieli przyjmującej spódnicę wkładu.

  - id: reservoir_wall_thickness
    name: "Grubość ścianki zbiornika"
    value: 3.0
    unit: mm
    tolerance: 0.1
    description: >
      Grubość ścianki i dna zbiornika (ta sama wartość dla obu — dno nie
      wymaga dodatkowego pogrubienia jak we wkładzie, bo nie mocuje
      żadnych elementów).

  - id: reservoir_cavity_depth
    name: "Głębokość komory na wodę"
    value: 40.0
    unit: mm
    tolerance: 0.3
    description: >
      Głębokość wewnętrznej komory zbiornika, licząc od górnej krawędzi
      (Z=0, ta sama płaszczyzna co dolna krawędź wkładu) do wewnętrznego
      dna.

  - id: reservoir_foot_height
    name: "Wysokość nóżek zbiornika"
    value: 4.0
    unit: mm
    tolerance: 0.2
    description: Wysokość nóżek pod dnem zbiornika (stabilność, cyrkulacja powietrza).

  - id: reservoir_foot_diameter
    name: "Średnica nóżek zbiornika"
    value: 10.0
    unit: mm
    tolerance: 0.3
    description: Średnica każdej z nóżek pod dnem zbiornika.

  - id: reservoir_foot_count
    name: "Liczba nóżek zbiornika"
    value: 3
    unit: count
    tolerance: 0
    description: Liczba nóżek rozmieszczonych równomiernie pod dnem zbiornika.

  - id: fill_spout_outer_diameter
    name: "Średnica zewnętrzna dziubka do nalewania"
    value: 10.0
    unit: mm
    tolerance: 0.2
    description: >
      Średnica zewnętrzna pionowej rurki do nalewania wody bez zdejmowania
      wkładu, dospawanej do zewnętrznej ścianki zbiornika.

  - id: fill_spout_inner_diameter
    name: "Średnica wewnętrzna dziubka do nalewania"
    value: 6.0
    unit: mm
    tolerance: 0.2
    description: Średnica wewnętrzna (bore) dziubka — kanał, którym leci woda.

  - id: fill_spout_top_protrusion
    name: "Wystawanie dziubka ponad krawędź zbiornika"
    value: 15.0
    unit: mm
    tolerance: 0.3
    description: >
      Wysokość, na jaką dziubek wystaje ponad płaszczyznę Z=0 (górna
      krawędź zbiornika/dolna krawędź wkładu) — musi być dostępny do
      nalewania mimo rozszerzającej się ścianki wkładu powyżej, patrz
      wyprowadzenie marginesu w specs/planter/decisions.md.

  - id: fill_spout_bottom_clearance
    name: "Prześwit dna dziubka nad dnem zbiornika"
    value: 3.0
    unit: mm
    tolerance: 0.2
    description: >
      Odstęp między dolnym końcem kanału dziubka a wewnętrznym dnem
      zbiornika — woda dolewana dociera nisko, bez chlupania, ale kanał
      nie blokuje dna.

  - id: overflow_hole_diameter
    name: "Średnica otworu przelewowego"
    value: 5.0
    unit: mm
    tolerance: 0.2
    description: >
      Średnica poziomego otworu w ściance zbiornika, wyznaczającego
      maksymalny poziom wody i odprowadzającego nadmiar na zewnątrz.

  - id: overflow_hole_height_from_floor
    name: "Wysokość otworu przelewowego nad dnem zbiornika"
    value: 28.0
    unit: mm
    tolerance: 0.3
    description: >
      Wysokość środka otworu przelewowego mierzona od wewnętrznego dna
      zbiornika — ustala maksymalny poziom wody (musi zostawiać zapas do
      krawędzi i nie kolidować ze spódnicą wkładu, patrz decisions.md).

  - id: material_density
    name: "Gęstość materiału (opcjonalna, do obliczenia masy)"
    value: 1.24e-6
    unit: kg/mm3
    tolerance: 0
    description: Domyślna gęstość materiału (PLA) używana wyłącznie do obliczenia masy.

  # --- Wzór ścianki zewnętrznej (v1: "premium fluted", wymienny) --------
  - id: pattern_flute_count
    name: "Liczba żłobień wzoru ścianki"
    value: 24
    unit: count
    tolerance: 0
    description: >
      Liczba pionowych, płytkich żłobień wyciętych w zewnętrznej ściance
      wkładu (jedyny element geometrii, który ma się zmieniać między
      wariantami serii — patrz specs/planter/decisions.md "Architektura
      wymiennego wzoru").

  - id: pattern_flute_depth
    name: "Głębokość żłobień wzoru ścianki"
    value: 1.5
    unit: mm
    tolerance: 0.1
    description: >
      Głębokość każdego żłobienia — ściśle mniejsza niż
      insert_wall_thickness (zostawia >= 0.5mm ścianki na dnie żłobienia,
      sprawdzane w check_engineering_preconditions()), na tyle głęboka,
      żeby wzór był wyraźnie widoczny/wyczuwalny na wydruku.

  - id: pattern_flute_width_deg
    name: "Szerokość kątowa żłobienia wzoru ścianki"
    value: 6.0
    unit: deg
    tolerance: 0.5
    description: >
      Szerokość kątowa (w stopniach, wokół osi Z) pojedynczego narzędzia
      tnącego żłobienie — musi być mniejsza niż 360/pattern_flute_count,
      żeby sąsiednie żłobienia się nie stykały.

  - id: pattern_flute_end_margin
    name: "Margines żłobień od góry i dołu wkładu"
    value: 5.0
    unit: mm
    tolerance: 0.5
    description: >
      Odstęp, na jaki żłobienia NIE sięgają do górnej krawędzi (żeby nie
      kolidować z zaokrągleniem top_rim_fillet_radius — nieregularna,
      poszarpana krawędź czołowa uniemożliwia fillet, zweryfikowane
      bezpośrednio budową) ani do dolnej krawędzi wkładu — zostawia gładki
      pasek na obu końcach.
```

## Geometria

Kolejność operacji (patrz `src/cad_project/planter/model.py`). Z=0 jest
wspólną płaszczyzną odniesienia obu części: dolna krawędź wkładu (miejsce
oparcia) i górna krawędź zbiornika.

### Insert — wkład na ziemię

1. **Bryła stożkowa**: `Cone` o promieniu dolnym
   `insert_bottom_outer_diameter/2`, promieniu górnym
   `insert_top_outer_diameter/2`, wysokości `insert_body_height`, od Z=0
   w górę.
2. **Wydrążenie (shell)**: górna ściana wybrana jako otwarcie, offset do
   wewnątrz o `insert_wall_thickness` — zostawia jednolitą grubość
   ścianki i dna śledzącą oryginalny (jeszcze niezdobiony) kształt
   stożka.
3. **Wzór ścianki — żłobienia** (jedyny element wymienny między
   wariantami serii, patrz `decisions.md` "Architektura wymiennego
   wzoru"): `pattern_flute_count` klinowych narzędzi tnących
   (częściowe `Cone` o `arc_size=pattern_flute_width_deg`, tym samym
   kącie zbieżności co bryła główna, przesunięte promieniowo do
   wewnątrz o `pattern_flute_depth`), odjętych od zewnętrznej
   powierzchni, rozmieszczonych równomiernie (`PolarLocations`),
   niesięgających `pattern_flute_end_margin` od górnej i dolnej
   krawędzi.
4. **Pogrubienie dna**: dodatkowy walec wewnątrz, od Z=`insert_wall_thickness`
   w górę o (`insert_floor_thickness - insert_wall_thickness`) —
   dno wychodzi grubsze niż ścianka boczna.
5. **Otwory drenażowe**: `drainage_hole_count` pionowych otworów
   Ø`drainage_hole_diameter`, na okręgu `drainage_hole_circle_diameter`,
   przez całą grubość dna.
6. **Spódnica pozycjonująca**: cienkościenna tuleja (grubość
   `insert_wall_thickness`) zwisająca poniżej Z=0 na wysokość
   `spigot_height`, średnica zewnętrzna wyprowadzona z
   `reservoir_mouth_inner_diameter - 2×fit_clearance`.
7. **Zaokrąglenie górnej krawędzi**: promień `top_rim_fillet_radius`,
   **tylko zewnętrzna** krawędź górnego otworu (wewnętrzna krawędź na tej
   samej, wąskiej ściance czołowej nie jest zaokrąglana — geometrycznie
   niewykonalne dla dwóch fillet-ów naraz na ściance węższej niż suma ich
   promieni, zweryfikowane bezpośrednio budową, patrz `decisions.md`).
8. **Rdzeń kapilarny**: perforowana rura Ø`capillary_tube_outer_diameter`
   (bore Ø`capillary_tube_inner_diameter`), od
   Z=−(`spigot_height + reservoir_cavity_depth − capillary_tube_reservoir_clearance`)
   do Z=+`capillary_tube_soil_protrusion`, z `capillary_tube_slot_count`
   pionowymi szczelinami szerokości `capillary_tube_slot_width` na całej
   długości.

### Reservoir — zbiornik na wodę

1. **Bryła walcowa**: `Cylinder` o promieniu
   `reservoir_mouth_inner_diameter/2 + reservoir_wall_thickness`, od
   Z=−`reservoir_cavity_depth` do Z=0.
2. **Wydrążenie (shell)**: górna ściana (Z=0) jako otwarcie, offset o
   `reservoir_wall_thickness` — stała średnica komory na całej
   głębokości (górna część tej samej komory pełni funkcję gardzieli
   przyjmującej spódnicę wkładu).
3. **Nóżki**: `reservoir_foot_count` nóżek Ø`reservoir_foot_diameter` ×
   `reservoir_foot_height` pod prawdziwym dnem.
4. **Dziubek do nalewania**: rura Ø`fill_spout_outer_diameter` (bore
   Ø`fill_spout_inner_diameter`) dospawana płasko do zewnętrznej ścianki
   (oś na promieniu równym zewnętrznej średnicy zbiornika), od
   Z=−(`reservoir_cavity_depth − fill_spout_bottom_clearance`) do
   Z=+`fill_spout_top_protrusion`; otwór dziubka zachodzi na wewnętrzną
   komorę o ok. 1mm z konstrukcji (promień osi dziubka równy zewnętrznej
   średnicy zbiornika minus promień wewnętrzny bore'u dziubka jest
   mniejszy niż promień wewnętrzny komory) — brak osobnego otworu
   łączącego, patrz `decisions.md`.
5. **Otwór przelewowy**: poziomy otwór Ø`overflow_hole_diameter` w
   ściance, na wysokości `overflow_hole_height_from_floor` od
   wewnętrznego dna, po stronie przeciwnej do dziubka.

## Reguły

* Model składa się z dokładnie **dwóch części** (insert, reservoir) — nie
  jednej połączonej bryły (mają być osobno wydrukowane, insert wyjmowany
  do napełniania/przesadzania).
* `insert_floor_thickness` musi być ≥ `insert_wall_thickness` (dno
  dobudowywane jako pogrubienie jednolitej grubości ścianki po shell, nie
  może być cieńsze).
* `top_rim_fillet_radius` musi być mniejszy niż `insert_wall_thickness`
  (fillet tylko zewnętrznej krawędzi, patrz Geometria pkt. 7).
* `pattern_flute_depth` musi zostawiać ≥ 0.5mm ścianki na dnie żłobienia
  (`pattern_flute_depth < insert_wall_thickness - 0.5`).
* `pattern_flute_width_deg × pattern_flute_count` musi być < 360°
  (żłobienia się nie stykają).
* `pattern_flute_end_margin × 2` musi być < `insert_body_height`.
* Wyprowadzona `spigot_outer_diameter` (=
  `reservoir_mouth_inner_diameter − 2×fit_clearance`) musi zostawiać
  margines > 2mm do `insert_bottom_outer_diameter` (pierścień oparcia) i
  do wyprowadzonej `reservoir_mouth_outer_diameter` (zasłonięty szew).
* `capillary_tube_inner_diameter` musi być mniejsza niż
  `capillary_tube_outer_diameter`.
* `capillary_tube_slot_count × capillary_tube_slot_width` musi zostawiać
  ≥ 40% obwodu rury jako żebra nośne.
* `capillary_tube_reservoir_clearance` musi być mniejsze niż
  `reservoir_cavity_depth − spigot_height` (rdzeń sięga głębiej niż
  spódnica).
* Otwór przelewowy (`overflow_hole_height_from_floor ±
  overflow_hole_diameter/2`) nie może kolidować z dnem zbiornika ani ze
  strefą wsuwu spódnicy (górne `spigot_height` komory).
* Dziubek do nalewania musi zachować > 2mm prześwitu do zewnętrznej
  powierzchni wkładu na całej wysokości swojego wystawania — sprawdzane
  jawnie w `check_engineering_preconditions()` (zakłada, że
  `insert_top_outer_diameter ≥ insert_bottom_outer_diameter`, czyli
  ścianka wkładu nigdy się nie zwęża idąc w górę).
* Żadna z dwóch części nie może mieć ujemnej objętości ani pustej
  geometrii; każda z osobna ma być pojedynczą bryłą.

## Oczekiwane wyniki

Ponieważ model składa się z dwóch fizycznie osobnych części, eksport
generuje pliki dla **obu części osobno**:

* `output/planter/step/insert.step`, `output/planter/step/reservoir.step`,
* `output/planter/stl/insert.stl`, `output/planter/stl/reservoir.stl`,
* `output/planter/previews/insert.png`, `output/planter/previews/reservoir.png`,
* `output/planter/reports/validation-report.json`,
* `output/planter/logs/build.log`.

## Definition of Done

- [ ] kod uruchamia się bez błędów (`python -m cad_project.planter.cli build`),
- [ ] Insert i Reservoir to każda dokładnie jedna bryła,
- [ ] wymiary insertu (średnice, wysokość) zgodne ze specyfikacją,
- [ ] liczba otworów drenażowych i żłobień wzoru zgodna ze specyfikacją,
- [ ] wyprowadzona średnica spódnicy mieści się w gardzieli zbiornika z
      dodatnim, ograniczonym luzem,
- [ ] eksport STEP i STL działa dla obu części,
- [ ] podgląd PNG istnieje dla obu części (lub błąd renderera jest jawnie
      i osobno zaraportowany, bez blokowania eksportu STEP/STL),
- [ ] wszystkie testy `pytest tests/planter/` przechodzą,
- [ ] raport walidacji ma status `passed`,
- [ ] żłobienia wzoru widoczne bezpośrednio na zbudowanej bryle (nie
      tylko w deklaracji parametrów) — zweryfikowane porównaniem objętości
      przed/po odjęciu wzoru, patrz `decisions.md`.
