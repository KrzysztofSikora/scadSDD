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
   zakresie regulacji (80–140 mm). To nie jest opcjonalny margines
   bezpieczeństwa — niedostateczne zazębienie oznacza, że część B może się
   wykręcić pod obciążeniem wysuniętej lufy.
3. **Kołnierz jako ogranicznik.** `collar_diameter` musi być ściśle
   większy niż `thread_major_diameter` (żeby fizycznie ograniczał
   wkręcanie) i ściśle mniejszy niż średnica zewnętrzna tulei
   (`thread_major_diameter + 2×nut_wall_thickness`), żeby mógł oprzeć się
   o jej czoło bez kolizji geometrycznej.
4. **Magnesy nie mogą się nakładać.** Rozstaw między środkami sąsiednich
   magnesów musi być większy niż `magnet_diameter`, inaczej kieszenie by
   się przecinały.
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
  czy 4× magnes Ø12×3mm faktycznie utrzyma karabin przy maksymalnym
  wysięgu 140mm (to zależy od masy broni, grubości ścianki sejfu i klasy
  magnesu N35/N42/N52, czego specyfikacja nie precyzuje) — to świadome
  ograniczenie zakresu v1, nie błąd. Jeśli potrzebna weryfikacja
  wytrzymałościowa, wymaga osobnej analizy inżynierskiej poza tym
  repozytorium.
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
