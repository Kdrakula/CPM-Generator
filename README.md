# Tkinter Graph Visualizer

Aplikacja GUI do wizualizacji grafów przy użyciu biblioteki `networkx`, `matplotlib` oraz `tkinter`.

## 📦 Wymagania

- Python 3.9+ (najlepiej oficjalna wersja z [https://www.python.org](https://www.python.org))
- `pip` (Python package installer)

## ⬇️ Klonowanie repozytorium

W terminalu:

```bash
git clone https://github.com/Kdrakula/CPM-Generator.git
cd CPM-Generator
```

## 🛠️ Instalacja bibliotek

W katalogu głównym znajduje się plik `requirements.txt`. Aby zainstalować wszystkie wymagane biblioteki:
```bash
pip install -r requirements.txt
```

### 📌 Zawartość `requirements.txt`
```text
tk
matplotlib
networkx
pygraphviz
```
Uwaga: `pygraphviz` wymaga, by na systemie był zainstalowany `Graphviz`.

### 💡 Instalacja `Graphviz` na macOS (jeśli jeszcze nie masz):
```bash
brew install graphviz
```
Na Windowsie pobierz z: https://graphviz.org/download/

## 🚀 Uruchamianie aplikacji

Po zainstalowaniu zależności uruchom aplikację:
```bash
python3 main.py
```
lub
```bash
python main.py
```