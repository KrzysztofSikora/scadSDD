# Specyfikacja modelu CAD: Magnetyczny uchwyt na lufę karabinu do sejfu

> **Ten plik jest źródłem prawdy dla wymagań.** Nie zmieniaj wartości,
> tolerancji ani reguł bez wyraźnego polecenia człowieka. Zobacz
> `.claude/CLAUDE.md` oraz `specs/rifle-mount/constraints.md` i
> `specs/rifle-mount/decisions.md`.

## Metadane

| Pole                  | Wartość                          |
|------------------------|-----------------------------------|
| Nazwa projektu        | Magnetic Rifle Barrel Mount       |
| Identyfikator modelu  | `magnetic-rifle-mount-001`        |
| Wersja specyfikacji   | `1.0.0`                           |
| Jednostki             | milimetry (mm)                    |

## Opis funkcjonalny

Uchwyt mocowany magnetycznie do metalowej ścianki sejfu, przytrzymujący
lufę karabinu w chwycie w kształcie litery U. Składa się z **dwóch części**:

* **Część A („podstawa")** — płyta z czterema magnesami neodymowymi
  (mocowanie do ścianki) i tuleją z gwintem wewnętrznym.
* **Część B („ramię")** — trzpień z gwintem zewnętrznym, zakończony
  kołnierzem oporowym i chwytem U na lufę.

Wkręcanie/wykręcanie Części B w Część A reguluje odległość lufy od
ścianki sejfu w zakresie **80–140 mm** (mierzone od powierzchni płyty
stykającej się ze ścianką do środka lufy spoczywającej w chwycie U).

## Parametry

Maszynowym źródłem prawdy jest [`specs/rifle-mount/parameters.yaml`](parameters.yaml).
Fragment poniżej jest jego dosłowną kopią, weryfikowaną automatycznie
(`tests/rifle_mount/test_spec_compliance.py`, parser YAML, nigdy regex po
Markdownie).

| Nazwa | ID techniczne | Wartość | Jednostka | Tolerancja |
|---|---|---|---|---|
| Min. odległość ścianka→lufa | `wall_to_barrel_center_min` | 80.0 | mm | ±0.3 |
| Maks. odległość ścianka→lufa | `wall_to_barrel_center_max` | 140.0 | mm | ±0.3 |
| Referencyjna średnica lufy | `barrel_diameter_reference` | 20.0 | mm | ±0.5 |
| Średnica magnesu | `magnet_diameter` | 12.0 | mm | ±0.05 |
| Grubość magnesu | `magnet_thickness` | 3.0 | mm | ±0.05 |
| Liczba magnesów | `magnet_count` | 4 | szt. | 0 |
| Ścianka nad magnesem | `magnet_pocket_wall_thickness` | 1.0 | mm | ±0.1 |
| Wymiar płyty mocującej | `mounting_plate_size` | 60.0 | mm | ±0.2 |
| Grubość płyty mocującej | `mounting_plate_thickness` | 4.0 | mm | ±0.1 |
| Odsunięcie magnesu od krawędzi | `magnet_edge_offset` | 10.0 | mm | ±0.2 |
| Zaokrąglenie narożników płyty | `plate_corner_fillet_radius` | 5.0 | mm | ±0.2 |
| Skok gwintu | `thread_pitch` | 4.0 | mm | ±0.1 |
| Średnica trzpienia (gwint) | `thread_major_diameter` | 25.0 | mm | ±0.1 |
| Kąt gwintu | `thread_angle_deg` | 29.0 | ° | 0 |
| Zazębienie gwintu | `thread_engagement_length` | 20.0 | mm | ±0.2 |
| Ścianka tulei | `nut_wall_thickness` | 4.0 | mm | ±0.2 |
| Długość tulei | `nut_boss_length` | 24.0 | mm | ±0.2 |
| Długość gwintu na trzpieniu | `rod_threaded_length` | 108.0 | mm | ±0.3 |
| Długość kołnierza | `collar_length` | 10.0 | mm | ±0.2 |
| Średnica kołnierza | `collar_diameter` | 27.0 | mm | ±0.1 |
| Prześwit U | `u_internal_width` | 30.0 | mm | ±0.2 |
| Długość U (wzdłuż lufy) | `u_arm_length` | 40.0 | mm | ±0.2 |
| Wysokość ramion U | `u_arm_height` | 26.0 | mm | ±0.2 |
| Ścianka U | `u_wall_thickness` | 6.0 | mm | ±0.2 |
| Szerokość rowka na wkładkę | `liner_groove_width` | 2.0 | mm | ±0.1 |
| Głębokość rowka na wkładkę | `liner_groove_depth` | 1.0 | mm | ±0.1 |
| Gęstość materiału (opcjonalna) | `material_density` | 1.24e-6 | kg/mm³ | — |

### Fragment maszynowy (kopia `specs/rifle-mount/parameters.yaml`)

```yaml
project:
  name: "Magnetic Rifle Barrel Mount"
  model_id: "magnetic-rifle-mount-001"
  spec_version: "1.0.0"
  units: "mm"

parameters:
  - id: wall_to_barrel_center_min
    name: "Minimalna odległość ścianka -> środek lufy"
    value: 80.0
    unit: mm
    tolerance: 0.3
    description: >
      Minimalna odległość od ścianki sejfu (powierzchni stykającej się z
      magnesami) do środka lufy spoczywającej w chwycie U, przy
      maksymalnie wkręconym mechanizmie regulacji.

  - id: wall_to_barrel_center_max
    name: "Maksymalna odległość ścianka -> środek lufy"
    value: 140.0
    unit: mm
    tolerance: 0.3
    description: >
      Maksymalna odległość od ścianki sejfu do środka lufy, przy
      maksymalnie wykręconym (wysuniętym) mechanizmie regulacji.

  - id: barrel_diameter_reference
    name: "Referencyjna średnica lufy"
    value: 20.0
    unit: mm
    tolerance: 0.5
    description: >
      Założona średnica lufy (bez osprzętu) używana wyłącznie do
      wyznaczenia prześwitu w chwycie U i pozycji środka lufy. Nie jest
      cechą wytwarzaną modelu.

  - id: magnet_diameter
    name: "Średnica magnesu neodymowego"
    value: 12.0
    unit: mm
    tolerance: 0.05
    description: Średnica każdego z czterech magnesów dyskowych.

  - id: magnet_thickness
    name: "Grubość magnesu neodymowego"
    value: 3.0
    unit: mm
    tolerance: 0.05
    description: Grubość (wysokość) każdego magnesu dyskowego.

  - id: magnet_count
    name: "Liczba magnesów"
    value: 4
    unit: count
    tolerance: 0
    description: Liczba magnesów neodymowych mocujących do ścianki sejfu.

  - id: magnet_pocket_wall_thickness
    name: "Grubość ścianki nad magnesem"
    value: 1.0
    unit: mm
    tolerance: 0.1
    description: >
      Grubość plastiku pozostająca między dnem kieszeni magnesu a
      zewnętrzną (przyścienną) powierzchnią płyty mocującej.

  - id: mounting_plate_size
    name: "Wymiar płyty mocującej (kwadrat)"
    value: 60.0
    unit: mm
    tolerance: 0.2
    description: >
      Długość boku kwadratowej płyty mocującej z magnesami. Dobrana tak,
      by kieszenie na magnesy w narożnikach nie kolidowały z tuleją
      gwintowaną (nut_boss_outer_diameter) w środku płyty — patrz
      specs/rifle-mount/decisions.md.

  - id: mounting_plate_thickness
    name: "Grubość płyty mocującej"
    value: 4.0
    unit: mm
    tolerance: 0.1
    description: >
      Całkowita grubość płyty mocującej (magnet_thickness +
      magnet_pocket_wall_thickness) — spójność sprawdzana automatycznie.

  - id: magnet_edge_offset
    name: "Odsunięcie środka magnesu od krawędzi płyty"
    value: 10.0
    unit: mm
    tolerance: 0.2
    description: Odległość środka każdego magnesu od najbliższej krawędzi płyty.

  - id: plate_corner_fillet_radius
    name: "Promień zaokrąglenia narożników płyty"
    value: 5.0
    unit: mm
    tolerance: 0.2
    description: Zaokrąglenie czterech pionowych krawędzi narożników płyty mocującej.

  - id: thread_pitch
    name: "Skok gwintu"
    value: 4.0
    unit: mm
    tolerance: 0.1
    description: Skok grubego gwintu trapezowego łączącego obie części.

  - id: thread_major_diameter
    name: "Średnica zewnętrzna gwintu (trzpień)"
    value: 25.0
    unit: mm
    tolerance: 0.1
    description: Średnica zewnętrzna (major diameter) gwintowanego trzpienia.

  - id: thread_angle_deg
    name: "Kąt gwintu trapezowego"
    value: 29.0
    unit: deg
    tolerance: 0
    description: Kąt profilu gwintu trapezowego (standard ACME = 29°).

  - id: thread_engagement_length
    name: "Efektywna długość zazębienia gwintu"
    value: 20.0
    unit: mm
    tolerance: 0.2
    description: >
      Długość gwintu wewnętrznego w tulei — stałe zazębienie utrzymywane
      w całym zakresie regulacji (patrz specs/rifle-mount/decisions.md).

  - id: nut_wall_thickness
    name: "Grubość ścianki tulei wokół gwintu"
    value: 4.0
    unit: mm
    tolerance: 0.2
    description: >
      Grubość materiału tulei między rdzeniem gwintu wewnętrznego a jej
      zewnętrzną powierzchnią (tuleja OD = thread_major_diameter + 2x ta wartość).

  - id: nut_boss_length
    name: "Długość tulei gwintowanej"
    value: 24.0
    unit: mm
    tolerance: 0.2
    description: >
      Całkowita długość walcowej tulei na płycie mocującej (zazębienie
      20mm + margines/wejście na gwint).

  - id: rod_threaded_length
    name: "Długość gwintowanej części trzpienia"
    value: 108.0
    unit: mm
    tolerance: 0.3
    description: >
      Długość gwintu na trzpieniu, licząc od jego końca wchodzącego w
      tuleję — musi zapewniać pełne zazębienie (thread_engagement_length)
      w całym zakresie regulacji (patrz decisions.md — obliczenie).

  - id: collar_length
    name: "Długość kołnierza oporowego"
    value: 10.0
    unit: mm
    tolerance: 0.2
    description: >
      Długość gładkiego kołnierza między gwintowanym trzpieniem a
      chwytem U, ograniczającego maksymalne wkręcenie.

  - id: collar_diameter
    name: "Średnica kołnierza oporowego"
    value: 27.0
    unit: mm
    tolerance: 0.1
    description: >
      Średnica kołnierza — większa niż thread_major_diameter (żeby
      opierał się o czoło tulei), mniejsza niż średnica zewnętrzna tulei.

  - id: u_internal_width
    name: "Prześwit wewnętrzny chwytu U"
    value: 30.0
    unit: mm
    tolerance: 0.2
    description: >
      Szerokość wewnętrzna (prześwit) chwytu U, w którą swobodnie wsuwa
      się lufa.

  - id: u_arm_length
    name: "Długość chwytu U wzdłuż osi lufy"
    value: 40.0
    unit: mm
    tolerance: 0.2
    description: Długość (głębokość wzdłuż osi lufy) profilu U.

  - id: u_arm_height
    name: "Wysokość ramion chwytu U"
    value: 26.0
    unit: mm
    tolerance: 0.2
    description: >
      Wysokość wewnętrzna ramion U, licząc od dna (powierzchni podpierającej
      lufę) do górnej krawędzi otwarcia. Wartość dobrana tak, by chwyt U
      (wraz ze ścianką u_wall_thickness) był wyśrodkowany na osi trzpienia
      gwintowanego — środek lufy referencyjnej wypada wtedy dokładnie na
      osi gwintu (współosiowo). Poprawiono z 25.0mm po wykryciu, że chwyt
      U był przesunięty względem osi trzpienia — patrz
      specs/rifle-mount/decisions.md ("U cradle coaxial alignment fix").

  - id: u_wall_thickness
    name: "Grubość ścianek chwytu U"
    value: 6.0
    unit: mm
    tolerance: 0.2
    description: Grubość dna i ramion litery U.

  - id: liner_groove_width
    name: "Szerokość rowka na wkładkę filcową"
    value: 2.0
    unit: mm
    tolerance: 0.1
    description: >
      Szerokość rowka wzdłuż wewnętrznej powierzchni U na wklejaną
      wkładkę ochronną (filc/guma).

  - id: liner_groove_depth
    name: "Głębokość rowka na wkładkę filcową"
    value: 1.0
    unit: mm
    tolerance: 0.1
    description: Głębokość rowka na wkładkę ochronną, wcięta w ścianki U.

  - id: material_density
    name: "Gęstość materiału (opcjonalna, do obliczenia masy)"
    value: 1.24e-6
    unit: kg/mm3
    tolerance: 0
    description: Domyślna gęstość materiału (PLA) używana wyłącznie do obliczenia masy.
```

## Geometria

Kolejność operacji (patrz `src/cad_project/rifle_mount/model.py`):

### Część A — podstawa (mocowana do ścianki)

1. **Płyta mocująca**: kwadrat `mounting_plate_size` × `mounting_plate_size`
   × `mounting_plate_thickness`, zaokrąglone pionowe krawędzie narożników
   (`plate_corner_fillet_radius`).
2. **Kieszenie na magnesy**: cztery ślepe otwory Ø`magnet_diameter` ×
   `magnet_thickness` głębokości, wiercone od wewnętrznej strony płyty
   (przeciwnej do ścianki), tak żeby zostało `magnet_pocket_wall_thickness`
   materiału do zewnętrznej (przyściennej) powierzchni. Środki otworów
   odsunięte o `magnet_edge_offset` od krawędzi płyty, symetrycznie w
   czterech narożnikach.
3. **Tuleja gwintowana**: walec Ø(`thread_major_diameter` +
   2×`nut_wall_thickness`) × `nut_boss_length`, doklejony (fuzja) do
   wewnętrznej strony płyty, współosiowo z osią regulacji. Wewnątrz
   gwint wewnętrzny (`thread_pitch`, `thread_major_diameter`,
   `thread_angle_deg`) o efektywnej długości `thread_engagement_length`.

### Część B — ramię (z chwytem U)

1. **Trzpień gwintowany**: walec Ø`thread_major_diameter` z gwintem
   zewnętrznym (`thread_pitch`, `thread_angle_deg`) na długości
   `rod_threaded_length`.
2. **Kołnierz oporowy**: walec Ø`collar_diameter` × `collar_length`,
   współosiowy, na końcu trzpienia — ogranicza maksymalne wkręcenie
   (opiera się o czoło tulei Części A).
3. **Chwyt U**: profil w kształcie litery U (prześwit wewnętrzny
   `u_internal_width`, ścianki `u_wall_thickness`, otwór skierowany "w
   górę" względem osi regulacji leżącej poziomo), **wyśrodkowany na osi
   trzpienia/kołnierza** (nie oparty stycznie z boku), tak by lufa
   spoczywająca w chwycie leżała współosiowo z gwintem — wyciągnięty na
   długość `u_arm_length` wzdłuż osi lufy (prostopadle do osi regulacji),
   doklejony do kołnierza. Na wewnętrznej powierzchni U rowek
   (`liner_groove_width` × `liner_groove_depth`) na wklejaną wkładkę
   ochronną.

### Zależność geometryczna (wyprowadzenie w `decisions.md`)

Chwyt U jest **wyśrodkowany na osi trzpienia gwintowanego** (nie oparty
stycznie z boku) — środek lufy referencyjnej leży dokładnie na osi
gwintu/regulacji. Dzięki temu odległość od kołnierza do środka lufy wzdłuż
osi regulacji to po prostu `u_wall_thickness + u_internal_width/2`
(pozycja środka szczeliny U), a wysokość ramion (`u_arm_height`) jest
dobrana tak, by wysokość chwytu U (`u_wall_thickness + u_arm_height`)
była symetryczna względem tej osi.

Stały offset (części niezmienne przy regulacji):
`mounting_plate_thickness + nut_boss_length + collar_length +
u_wall_thickness + u_internal_width/2` = 4+24+10+6+15 = **59 mm**.

Wysuw trzpienia (część zmienna) = `wall_to_barrel_center_{min,max} -
59mm` = 21–81 mm (rozpiętość 60 mm, zgodna z różnicą
`wall_to_barrel_center_max - wall_to_barrel_center_min`).

`rod_threaded_length` (108 mm) musi być ≥ wysuw_max (81mm) +
`thread_engagement_length` (20mm) = 101mm — spełnione z 7mm marginesu.

## Reguły

* Model składa się z dokładnie **dwóch części** (Część A, Część B) — nie
  jednej połączonej bryły (mają być osobno wydrukowane i skręcane).
* Gwint musi zapewniać pełne zazębienie (`thread_engagement_length`) w
  całym zakresie regulacji 80–140 mm — patrz wyprowadzenie wyżej.
* Kołnierz oporowy (`collar_diameter`) musi być większy niż
  `thread_major_diameter` (żeby ograniczał wkręcanie) i mniejszy niż
  średnica zewnętrzna tulei `thread_major_diameter + 2×nut_wall_thickness`
  (żeby mógł się o nią oprzeć bez kolizji).
* Cztery magnesy nie mogą się nakładać ani wychodzić poza krawędź płyty:
  `magnet_edge_offset > magnet_diameter/2` i rozstaw między sąsiednimi
  magnesami (`mounting_plate_size - 2×magnet_edge_offset`) musi być
  większy niż `magnet_diameter`.
* `u_internal_width` musi być większy niż `barrel_diameter_reference`
  (swobodny prześwit).
* `liner_groove_depth` musi być mniejszy niż `u_wall_thickness` (rowek nie
  może przebijać ścianki na wylot).
* `mounting_plate_thickness` musi się zgadzać z sumą `magnet_thickness +
  magnet_pocket_wall_thickness`.
* Żadna z dwóch części nie może mieć ujemnej objętości ani pustej
  geometrii; każda z osobna ma być pojedynczą bryłą.

## Oczekiwane wyniki

Ponieważ model składa się z dwóch fizycznie osobnych części, eksport
generuje pliki dla **obu części osobno**:

* `output/rifle-mount/step/base.step`, `output/rifle-mount/step/arm.step`,
* `output/rifle-mount/stl/base.stl`, `output/rifle-mount/stl/arm.stl`,
* `output/rifle-mount/previews/base.png`, `output/rifle-mount/previews/arm.png`,
* `output/rifle-mount/reports/validation-report.json` (raport obejmuje obie części),
* `output/rifle-mount/logs/build.log`.

## Definition of Done

- [ ] kod uruchamia się bez błędów (`python -m cad_project.rifle_mount.cli build`),
- [ ] Część A i Część B to każda dokładnie jedna bryła,
- [ ] liczba magnesów i ich wymiary zgodne ze specyfikacją,
- [ ] gwint zewnętrzny (Część B) i wewnętrzny (Część A) mają zgodne
      parametry (średnica, skok, kąt) — sprawdzane przez porównanie
      metadanych cech obu części,
- [ ] wyliczone zazębienie gwintu ≥ `thread_engagement_length` w całym
      zakresie regulacji,
- [ ] chwyt U ma prześwit zgodny ze specyfikacją,
- [ ] eksport STEP i STL działa dla obu części,
- [ ] podgląd PNG istnieje dla obu części (lub błąd renderera jest jawnie
      i osobno zaraportowany, bez blokowania eksportu STEP/STL),
- [ ] wszystkie testy `pytest tests/rifle_mount/` przechodzą,
- [ ] raport walidacji ma status `passed`.
