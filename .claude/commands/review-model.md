---
description: Independent cross-check of spec vs parameters vs model code vs tests vs validation report.
---

Wykonaj niezależny przegląd zgodności: **specyfikacja → implementacja →
wynik**. To przegląd, nie naprawa — nie zmieniaj kodu w trakcie tego
polecenia, chyba że użytkownik wyraźnie o to poprosi po przedstawieniu
wyników.

Porównaj ze sobą:

1. `specs/spec.md` + `specs/parameters.yaml` + `specs/constraints.md`
   (wymagania),
2. `src/cad_project/parameters.py` i `src/cad_project/model.py`
   (implementacja),
3. `tests/*.py` (co faktycznie jest sprawdzane),
4. `output/reports/validation-report.json` (ostatni zmierzony wynik — jeśli
   nie istnieje albo jest nieaktualny względem bieżącego kodu, uruchom
   `python -m cad_project.cli all` żeby go odświeżyć, i powiedz to wprost).

Przedstaw raport z następującymi sekcjami:

## Wymagania spełnione
Lista wymagań z `specs/spec.md` (parametry, geometria, reguły, DoD), które są
zaimplementowane, przetestowane i potwierdzone przez raport walidacji z
odniesieniem do konkretnego pliku/linii/testu/checku.

## Wymagania niespełnione
Wymagania, które nie są spełnione albo nie są w pełni zaimplementowane —
z konkretnym wskazaniem różnicy (oczekiwane vs rzeczywiste, plik, linia).

## Wymagania nieweryfikowalne
Wymagania, których obecny zestaw testów/walidacji nie jest w stanie
potwierdzić ani zaprzeczyć (np. wymaga interpretacji człowieka, albo wymaga
narzędzia, którego nie mamy). Wyjaśnij dlaczego.

## Ukryte założenia
Decyzje podjęte w kodzie, które nie wynikają wprost ze specyfikacji, ale
były konieczne do jej zrealizowania (np. kolejność operacji fillet/otwory,
sposób wyśrodkowania bryły, wybór metody renderowania). Odnieś się do
`specs/decisions.md` — czy założenie jest tam udokumentowane?

## Potencjalne problemy konstrukcyjne
Np. czy tolerancje są realistyczne dla wybranej metody wytwarzania, czy
otwory nie są zbyt blisko zaokrąglenia, czy grubość ścianki przy otworze
montażowym jest sensowna.

## Ograniczenia automatycznej walidacji
Podsumuj to, co już jest udokumentowane w `specs/constraints.md`
(np. detekcja liczby otworów opiera się na jawnych metadanych, nie na
w pełni niezawodnej analizie topologicznej) i dodaj wszystko, co
zaobserwowałeś podczas przeglądu, a nie jest jeszcze tam opisane.

Nie modyfikuj `specs/`, `output/reports/validation-report.json` ani kodu w
ramach tego polecenia — to przegląd tylko do odczytu.
