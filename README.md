# SauceDemo – Test Automation Suite

Automatisierte Regressionstests für [saucedemo.com](https://www.saucedemo.com) mit **Python**, **Playwright** und **pytest**.

![CI](https://github.com/<YOUR_USERNAME>/saucedemo-tests/actions/workflows/regression.yml/badge.svg)

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
│   ├── inventory_page.py    # Produktliste POM
│   ├── cart_page.py         # Warenkorb POM
│   └── checkout_page.py     # Checkout-Flow POM (Step 1, 2, Complete)
├── tests/
│   ├── test_login.py        # Authentifizierungs-Tests
│   ├── test_inventory.py    # Sortierung & Warenkorb-Tests
│   ├── test_checkout.py     # End-to-End Checkout-Tests
│   └── test_bugs.py         # Dokumentierte Bugs (problem_user, error_user, performance_glitch_user)
├── conftest.py              # Globale Fixtures (Browser, Page, Login-State)
├── pytest.ini               # pytest-Konfiguration
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

### Nur eine Testdatei
```bash
python -m pytest tests/test_login.py -v
```

---

## Test-Scope

| **Bereich** | **Testfälle** |
|---|---|
| **Login** | Erfolgreicher Login, gesperrter User, falsches Passwort, leere Felder |
| **Sortierung** | A→Z, Z→A, Preis aufsteigend, Preis absteigend |
| **Warenkorb** | Artikel hinzufügen (1 & mehrere), Artikel entfernen, alle Artikel |
| **Checkout** | Happy Path (1 & 2 Artikel), Validierungsfehler, Navigation nach Bestätigung |
| **Cross-User** | Alle oben genannten Verhaltenstests laufen auch mit `problem_user`, `error_user`, `performance_glitch_user` und `visual_user` |

---

## Cross-User Testing & Bug-Erkennung

SauceDemo stellt verschiedene User-Accounts mit absichtlich eingebauten Fehlern bereit.
Statt eine separate "Bug-Datei" zu pflegen, laufen die gleichen Verhaltenstests für **alle User**.

Wenn ein Test für `problem_user` fehlschlägt, der für `standard_user` besteht — **das ist der Bug-Fund**.

Bekannte Fehler sind mit `pytest.mark.xfail` markiert:

| Status | Bedeutung |
|---|---|
| `PASSED` | Verhalten korrekt |
| `xfail` | Test schlägt fehl — dokumentierter Bug |
| `xpass` | Test besteht obwohl `xfail` — Bug wurde behoben! |
| `FAILED` | Unerwarteter Fehler — neuer Bug oder Testfehler |

```bash
# Nur Cross-User Tests ausführen
python -m pytest -k "cross_user or test_each or test_sort_za or test_add_to_cart or test_checkout_completes or test_remove_in_cart or test_login_completes" -v
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
