# Log decyzji projektowych

Chronologiczny zapis decyzji technicznych podjętych podczas tworzenia
projektu i ich uzasadnień. Nowe decyzje dopisuj na końcu pliku — nie
nadpisuj historii.

## 2026-07-28 — Wybór silnika CAD

**Decyzja**: Build123d (tryb `BuildPart`/API obiektowe) jako jedyny silnik
geometrii, na Pythonie 3.12, z natywnym backendem OpenCascade (OCP).

**Uzasadnienie**: wymaganie użytkownika wprost wyklucza CadQuery, OpenSCAD i
Fusion 360. Build123d działa lokalnie, bez GUI, i udostępnia API wystarczające
do parametrycznego modelowania, eksportu STEP/STL oraz tesselacji do
podglądu.

## 2026-07-28 — Maszynowe źródło parametrów: YAML

**Decyzja**: `specs/parameters.yaml` jest jedynym maszynowym źródłem prawdy
dla wartości liczbowych. `specs/spec.md` zawiera czytelną dla ludzi tabelę
oraz dosłowną kopię YAML w bloku ```yaml, którą testy porównują z plikiem
`parameters.yaml` przez `yaml.safe_load` (parser strukturalny, bez regexów po
Markdownie). `src/cad_project/parameters.py` wczytuje `parameters.yaml`
bezpośrednio w runtime, więc kod nie może z nim dryfować z definicji.

**Uzasadnienie**: użytkownik prosił o rozwiązanie, w którym parametry
maszynowe są jednoznaczne i łatwe do walidacji, oraz przestrzegał przed
kruchym parserem Markdown opartym o przypadkowe wyrażenia regularne. YAML
+ dedykowany parser (PyYAML) + porównanie strukturalne (nie tekstowe)
spełnia oba wymagania.

## 2026-07-28 — Reprezentacja metadanych cech modelu

**Decyzja**: `build_model()` zwraca `ModelResult(part: Part, features:
ModelFeatures)`, gdzie `ModelFeatures` to zamrożony dataclass z jawnymi
polami: `hole_count`, `hole_diameter_mm`, `hole_positions_mm`,
`base_length_mm`, `base_width_mm`, `base_thickness_mm`, `fillet_radius_mm`.

**Uzasadnienie**: wiarygodna, w pełni automatyczna detekcja "liczby otworów"
metodami czysto topologicznymi (bez znajomości intencji projektowej) jest
zawodna — cylindryczne ścianki mogą pochodzić z otworów, zaokrągleń albo
innych operacji. Zamiast udawać, że taka detekcja działa niezawodnie, model
jawnie zwraca metadane cech, które są traktowane jako część kontraktu
`build_model()` i weryfikowane w testach determinizmu (muszą być identyczne
przy dwóch niezależnych budowach). Uzupełniająco, `validation.py` wykonuje
najlepszy-możliwy (best-effort) przegląd topologiczny cylindrycznych ścianek
o promieniu zgodnym z `hole_diameter/2`, ale wynik tego przeglądu jest
oznaczony w raporcie jako informacyjny, a nie rozstrzygający.

## 2026-07-28 — Generowanie podglądu PNG bez GUI/VTK

**Decyzja**: środowisko ma zainstalowany `cadquery-ocp-novtk` (OCP bez
bindingów VTK), więc standardowe podglądy 3D Build123d/OCP (`ocp_vscode`,
viewer VTK) nie są dostępne. Podgląd PNG jest generowany przez:
1. tesselację każdej ściany bryły osobno (`Face.tessellate()`),
2. ręczne cieniowanie Lambertowskie na podstawie normalnych trójkątów,
3. renderowanie w `matplotlib` (`Axes3D`, backend `Agg`, w pełni headless),
   z `computed_zorder=False` i jawnym porządkiem rysowania ścian od
   najniższej do najwyższej współrzędnej Z, aby uniknąć błędnego sortowania
   głębi przez domyślny algorytm malarski `Poly3DCollection` (zaobserwowany
   błąd: duże, nieregularne trójkąty triangulacji OCCT dla ścian z otworami
   powodowały artefakty przy sortowaniu całej siatki jako jednej kolekcji).

**Uzasadnienie**: to podejście nie wymaga VTK, GUI, Xvfb ani zewnętrznych
usług, jest w pełni deterministyczne i headless, i naprawia konkretny,
zaobserwowany błąd wizualny (patrz commit historii implementacji). Błąd
renderowania jest przechwytywany osobno i nie blokuje eksportu STEP/STL
(patrz `src/cad_project/rendering.py` i `src/cad_project/cli.py`).

## 2026-07-28 — Determinizm eksportu STEP

**Decyzja**: `export_step()` jest wywoływane z jawnym, stałym parametrem
`timestamp`, aby uniknąć niedeterministycznych znaczników czasu w nagłówku
pliku STEP. Testy determinizmu i tak nie porównują binarnej zawartości
STEP — porównują wyłącznie mierzalne właściwości geometryczne (bounding box,
objętość, powierzchnię, liczbę brył, metadane cech).

**Uzasadnienie**: użytkownik wprost zastrzegł, by nie porównywać
bezrefleksyjnie binarnej zawartości STEP ze względu na możliwe zmienne
metadane.

## 2026-07-28 — FreeCAD jako opcjonalny viewer (nie zależność pipeline'u)

**Decyzja**: dodano `scripts/view.sh` (i `make view`) otwierający
`output/step/model.step` w FreeCAD, jeśli jest zainstalowany na systemie.
FreeCAD **nie** jest dodany jako zależność Pythona ani do `pyproject.toml`
— to zewnętrzny program GUI instalowany osobno przez użytkownika (apt,
Flatpak albo AppImage), udokumentowany w README ("Wymagania systemowe" i
"Podgląd modelu w FreeCAD"). Jeśli FreeCAD nie jest zainstalowany, skrypt
kończy się czytelnym błędem z instrukcją instalacji, zamiast cichej
porażki albo próby automatycznej instalacji (instalacja systemowa wymaga
świadomej zgody użytkownika, m.in. bo zwykle wymaga `sudo`).

**Uzasadnienie**: użytkownik poprosił o dodanie FreeCAD jako narzędzia do
oglądania wygenerowanego modelu STEP. Ponieważ podstawowy wymóg projektu to
działanie w pełni headless (patrz `specs/constraints.md`), FreeCAD musi
pozostać czysto opcjonalnym dodatkiem do interaktywnej inspekcji przez
człowieka, nie częścią automatycznego pipeline'u `build/export/validate/render`.
