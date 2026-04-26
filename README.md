# SauceDemo – Test Automation Suite

Automatisierte Regressionstests für [saucedemo.com](https://www.saucedemo.com) mit **Python**, **Playwright** und **pytest**.

---

## Architektur

Das Projekt folgt dem **Page Object Model (POM)**, um Selektoren und Aktionen von den eigentlichen Tests zu trennen. Dadurch bleibt der Code wartbar, wenn sich die UI ändert – man passt die Page-Klasse an, nicht jeden einzelnen Test.

```
.
├── .github/
│   └── workflows/
│       └── regression.yml   # CI-Pipeline (GitHub Actions)
├── pages/
│   ├── login_page.py        # Login-Seite POM
│   ├── product_page.py      # Produktliste POM
│   ├── cart_page.py         # Warenkorb POM
│   ├── checkout_page.py     # Checkout-Flow POM (Step 1, 2, Complete)
│   └── sidebar_menu.py      # Gemeinsame Sidebar-Komponente
├── tests/
│   ├── test_login.py        # Authentifizierungs-Tests
│   ├── test_product.py      # Sortierung & Warenkorb-Tests
│   ├── test_checkout.py     # End-to-End Checkout-Tests
│   └── test_sidebar.py      # Sidebar-Menü und Navigation
├── conftest.py              # Globale Fixtures (Browser, Page, Login-State)
├── pytest.ini               # pytest-Konfiguration
├── report.html              # Beispiel für pytest-html Report
└── requirements.txt         # Python-Abhängigkeiten
```

### Warum POM?

| Ohne POM | Mit POM |
|---|---|
| Selector `#login-button` in jedem Test | Selector an einer einzigen Stelle in `LoginPage` |
| Bei UI-Änderung: alle Tests anfassen | Bei UI-Änderung: nur die Page-Klasse anpassen |
| Lesbarkeit leidet | Tests lesen sich wie Prosa |

---

## Voraussetzungen

- Python ≥ 3.10
- pip

---

## Installation

```bash
# 1. Repository klonen
git clone https://github.com/<YOUR_USERNAME>/saucedemo-tests.git
cd saucedemo-tests

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Playwright-Browser herunterladen
python -m playwright install chromium
```

> **Hinweis Windows:** `playwright` ist nach der Installation möglicherweise nicht direkt im PATH verfügbar.
> Nutze deshalb immer `python -m playwright` statt nur `playwright`.

---

## Tests ausführen

### Alle Tests (Browser sichtbar)
```bash
python -m pytest -v
```

### Headless (kein Browserfenster – ideal für CI)
```bash
python -m pytest --headless -v
```

### Mit HTML-Report
```bash
python -m pytest --headless --html=report.html --self-contained-html -v
```
Der Report wird als `report.html` im Projektverzeichnis gespeichert und kann im Browser geöffnet werden.
Screenshots fuer `FAILED`- und `XFAIL`-Ergebnisse werden automatisch unter `artifacts/screenshots/` abgelegt.

### Nur eine Testdatei
```bash
python -m pytest tests/test_login.py -v
```

### Nur Sidebar-Tests
```bash
python -m pytest tests/test_sidebar.py -v
```

---

## Test-Scope

| **Bereich** | **Testfälle** |
|---|---|
| **Login** | Erfolgreicher Login, gesperrter User, falsches Passwort, leere Felder |
| **Sortierung** | A→Z, Z→A, Preis aufsteigend, Preis absteigend |
| **Warenkorb** | Artikel hinzufügen (1 & mehrere), Artikel entfernen, alle Artikel |
| **Checkout** | Happy Path (1 & 2 Artikel), Validierungsfehler, Navigation nach Bestätigung |
| **Sidebar** | Menü öffnen/schließen, All Items/Products, Logout, About, Reset App State, Präsenz auf allen authentifizierten Seiten |
| **Cross-User** | Ausgewählte Regressionen laufen zusätzlich mit `problem_user`, `error_user`, `performance_glitch_user` und `visual_user`: Login-Dauer, eindeutige Produktbilder, Z→A-Sortierung, Badge nach Add-to-Cart, visuelle Header-/Preisleisten-Checks, Katalogpreise auf der Produktseite, Checkout-Abschluss, Checkout-Button-Position im Warenkorb und Entfernen im Warenkorb |

---

## Cross-User Testing & Bug-Erkennung

SauceDemo stellt verschiedene User-Accounts mit absichtlich eingebauten Fehlern bereit.
Statt eine separate "Bug-Datei" zu pflegen, laufen ausgewählte Regressionen gezielt für mehrere User-Typen.

Wenn ein Test für `problem_user` fehlschlägt, der für `standard_user` besteht — **das ist der Bug-Fund**.

Bekannte Fehler sind mit `pytest.mark.xfail` markiert:

| Status | Bedeutung |
|---|---|
| `PASSED` | Verhalten korrekt |
| `xfail` | Test schlägt fehl — dokumentierter Bug |
| `xpass` | Test besteht obwohl `xfail` — Bug wurde behoben! |
| `FAILED` | Unerwarteter Fehler — neuer Bug oder Testfehler |

Aktuell dokumentierte Bugs umfassen unter anderem:

- `problem_user`: alle Produktbilder verwenden dieselbe Bildquelle.
- `problem_user` und `error_user`: Z→A-Sortierung hat keinen Effekt.
- `error_user`: Checkout kann nicht vollständig abgeschlossen werden.
- `visual_user`: Warenkorb-Symbol ist im Header verschoben und bleibt nicht sauber oben rechts.
- `visual_user`: Zwischen Preis und Add-to-cart-Button entsteht auf Produktkarten zu viel Abstand.
- `visual_user`: Produktpreise auf der Produktseite weichen vom Standardkatalog ab.
- `visual_user`: Checkout-Button ist im Warenkorb visuell fehlplatziert und bleibt nicht im Footer-Bereich.
- `standard_user`: `Reset App State` leert zwar den Warenkorb, setzt aber den aktuellen `Remove`-Button auf der Produktseite erst nach Reload wieder auf `Add to cart`.

Bei `FAILED` und dokumentierten `XFAIL`-Ergebnissen wird automatisch ein Full-Page-Screenshot unter `artifacts/screenshots/` gespeichert. Das erleichtert die visuelle Analyse der absichtlich fehlerhaften User-Typen.

```bash
# Nur Cross-User Tests ausführen
python -m pytest -k "cross_user or test_each or test_sort_za or test_add_to_cart or test_product_prices or test_cart_icon or test_price_and_button or test_checkout_completes or test_checkout_button or test_remove_in_cart or test_login_completes" -v
```

---

## CI/CD (GitHub Actions)

Die Pipeline startet automatisch bei jedem Push und Pull Request auf `main`:

1. Python-Umgebung aufsetzen
2. Abhängigkeiten installieren
3. Playwright-Browser herunterladen
4. Tests im Headless-Modus ausführen
5. HTML-Report als Artefakt speichern (14 Tage)

Konfiguration: [`.github/workflows/regression.yml`](.github/workflows/regression.yml)
