# Plan na przyszłość: serwer MCP dla Build123d

## Status obecny

Ten projekt **nie ma** własnego serwera MCP i **nie potrzebuje go**, żeby
działać. Cały workflow Spec-Driven CAD jest w pełni obsługiwany przez
standardowe możliwości Claude Code:

* dostęp do systemu plików (odczyt `specs/`, zapis `src/`, odczyt
  `output/reports/validation-report.json`),
* terminal (`python -m cad_project.cli ...`, `pytest`, `ruff`, `make ...`),
* polecenia projektowe (`.claude/commands/*.md`) i skille
  (`.claude/skills/*/SKILL.md`).

Ten dokument opisuje, **kiedy** własny serwer MCP zacząłby dawać realną
przewagę, czego CLI mu **nie** zapewnia, oraz szkic narzędzi na wypadek
przyszłej implementacji. To plan na kolejną fazę — nie wymóg fazy obecnej.

## Kiedy własny MCP daje korzyści

1. **Ustrukturyzowane wejście/wyjście zamiast parsowania stdout.** CLI zwraca
   tekst logów i kod wyjścia; MCP tool może zwrócić bezpośrednio strukturę
   JSON (np. `ValidationReport` jako typowany obiekt), eliminując potrzebę
   parsowania.
2. **Współdzielony stan procesu.** Jeśli w przyszłości budowanie modelu
   stanie się kosztowne (duże złożone złożenia, długi czas obliczeń),
   serwer MCP mógłby utrzymywać zbudowany model w pamięci między
   wywołaniami (`build_model` raz, potem wielokrotne `measure_model`/
   `export_step` bez odbudowy), czego osobne wywołania CLI (każde to nowy
   proces Pythona) nie potrafią.
3. **Integracja z wieloma klientami MCP jednocześnie**, nie tylko Claude
   Code (np. inne narzędzia agentowe, IDE), bez duplikowania logiki CLI.
4. **Precyzyjna kontrola uprawnień na poziomie narzędzia**, np. osobne
   uprawnienie do "measure_model" (bezpieczne, tylko odczyt) vs
   "export_step" (zapis plików) — CLI/terminal daje kontrolę na poziomie
   całej komendy powłoki, nie na poziomie pojedynczej operacji.

## Czego serwer MCP NIE daje w porównaniu z CLI (na tym etapie)

* Nie przyspiesza samego Build123d/OCCT — koszt geometrii jest identyczny.
* Nie eliminuje potrzeby subprocessu do uruchomienia OCCT (to nadal Python +
  natywne biblioteki C++).
* Nie upraszcza niczego, co dziś jest trywialne przez `Bash` + jawne
  komendy CLI — dla pojedynczego, lokalnego projektu z jednym modelem,
  narzut utrzymania serwera (proces w tle, protokół, wersjonowanie
  schematów) przewyższa korzyść.
* Nie zastępuje jawnych plików źródła prawdy (`specs/`) — MCP tool i tak
  musiałby czytać te same pliki.

## Proponowane narzędzia MCP (faza przyszła)

| Narzędzie              | Wejście                                   | Wyjście |
|-------------------------|--------------------------------------------|---------|
| `build_model`           | *(brak, opcjonalnie hash parametrów)*      | `{ "built": true, "features": {...} }` albo błąd specyfikacji |
| `measure_model`         | *(brak — działa na ostatnio zbudowanym modelu)* | `Measurements` jako JSON (patrz `measurements.py`) |
| `validate_model`        | *(brak)*                                   | Pełny `ValidationReport` (identyczny schemat jak `output/reports/validation-report.json`) |
| `export_step`           | `path: str` (opcjonalna, domyślnie `output/step/model.step`) | `{ "status": "passed"/"failed", "path": str, "error": str? }` |
| `export_stl`            | `path: str` (opcjonalna)                   | jw. |
| `render_preview`        | `path: str` (opcjonalna)                   | `{ "status": ..., "path": ..., "error": str? }` — błąd renderera nigdy nie jest wyjątkiem protokołu MCP, zawsze polem `error` |
| `get_validation_report` | *(brak)*                                   | Zawartość ostatniego `output/reports/validation-report.json`, albo jawny błąd "brak raportu — uruchom validate_model" |

### Schemat wejść/wyjść

Wszystkie narzędzia zwracają JSON zgodny 1:1 ze strukturami już
zdefiniowanymi w `src/cad_project/validation.py`, `measurements.py`,
`exports.py`, `rendering.py` (dataclassy `ValidationCheck`, `Measurements`,
`ExportOutcome`, `RenderOutcome`) — serializowane przez `dataclasses.asdict`.
Nie definiujemy osobnego, równoległego schematu — MCP tool jest cienką
warstwą nad istniejącymi, już przetestowanymi funkcjami Pythona.

### Obsługa błędów

* Błąd specyfikacji (`SpecificationError`) → narzędzie zwraca
  `{"status": "blocked", "reason": "..."}`, nigdy nie zgaduje wartości.
* Błąd geometrii/eksportu → `{"status": "failed", "error": "..."}`, zgodnie
  z istniejącym wzorcem `ExportOutcome`/`RenderOutcome`.
* Nieoczekiwany wyjątek Pythona → przechwycony na granicy narzędzia MCP i
  zwrócony jako ustrukturyzowany błąd (nigdy surowy traceback do klienta),
  ale zalogowany w pełni po stronie serwera (`output/logs/build.log`).

### Bezpieczeństwo wykonywania kodu

* Serwer MCP wykonywałby wyłącznie predefiniowane funkcje z
  `src/cad_project/*` — **żadnego dowolnego `eval`/`exec` kodu
  użytkownika**. To nie jest "sandbox do uruchamiania cudzego kodu Build123d",
  tylko API nad konkretnym, ustalonym modelem.
* Ścieżki wyjściowe (`export_step`, `export_stl`, `render_preview`) muszą
  być walidowane, żeby nie wychodzić poza `output/` (zapobieganie zapisowi
  poza repozytorium przez np. `../../etc/...`).
* Serwer działałby lokalnie (stdio/lokalny socket), bez ekspozycji sieciowej
  domyślnie — zgodnie z resztą projektu ("lokalnie działający system").

## Plan implementacji (kolejna faza, nie teraz)

1. Wydzielić z `cli.py` cienką warstwę "pipeline API" (funkcje bez
   argparse/logging-do-pliku), żeby CLI i przyszły serwer MCP współdzieliły
   dokładnie tę samą logikę zamiast ją duplikować.
2. Dodać `mcp_server.py` (np. z użyciem oficjalnego SDK MCP dla Pythona),
   rejestrujący siedem narzędzi z tabeli powyżej jako cienkie wrappery nad
   krokiem 1.
3. Dodać testy kontraktowe: każde narzędzie MCP zwraca dokładnie to samo,
   co odpowiadająca komenda CLI dla tych samych parametrów wejściowych.
4. Udokumentować konfigurację serwera (jak dodać go do `claude mcp add`)
   bez zmiany istniejącego, samodzielnie działającego workflow CLI —
   serwer MCP ma być **dodatkiem**, nie zamiennikiem.

Do tego czasu: używaj `python -m cad_project.cli ...` i poleceń
`.claude/commands/*.md`.
