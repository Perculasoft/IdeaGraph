# 🧠 IdeaGraph
**Ein persönliches Denk- und Ideensystem, das Verbindungen erkennt, bevor man sie selbst sieht.**

---

## 🌍 Vision

**IdeaGraph** ist kein klassischer Notiz- oder Task-Manager.  
Es ist eine Plattform, die Gedanken, Konzepte und Ideen **semantisch versteht** und **vernetzt**, statt sie nur zu speichern.

Ziel ist es, ein System zu schaffen, das den kreativen Denkprozess abbildet:
- Ideen entstehen spontan – IdeaGraph hält sie fest.
- Die KI erkennt Zusammenhänge zwischen Ideen.
- Ähnliche oder synergistische Ideen werden automatisch verknüpft.
- Aus losen Gedanken entstehen Strukturen, Projekte und Innovationen.

> *„Ich möchte nicht mehr wissen, was ich schon gedacht habe –  
> sondern sehen, wie meine Gedanken miteinander sprechen.“*

---

## 💡 Kernidee

Jede Idee ist ein **Knoten** in einem semantischen Netzwerk.  
Die KI erstellt Vektoren (Embeddings) aus Titel, Beschreibung und Tags.  
So erkennt das System, **welche Ideen sich ähneln**, **aufeinander aufbauen** oder **kombinierbar** sind.

Das Ziel ist eine **visuelle, durchsuchbare Karte** deines Denkraums –  
eine Art digitales Gedächtnis mit semantischem Bewusstsein.

---

## 🧩 Architekturüberblick

| Ebene | Technologie | Aufgabe |
|-------|--------------|----------|
| **Frontend (UI)** | Blazor WebAssembly (PWA) | Eingabe, Übersicht, Visualisierung |
| **Backend (API)** | FastAPI (Python 3.11) | REST-Schnittstelle für Ideen, Ähnlichkeit & Relationen |
| **Vektorspeicher** | ChromaDB | Speicherung der semantischen Embeddings |
| **KI-Service** | OpenAI API (`text-embedding-3-small`) | Embedding-Berechnung |
| **Datenformat** | JSON / REST | Kommunikation zwischen UI und API |

---

## ⚙️ Funktionsumfang (MVP)

1. 📝 **Ideen erfassen**  
   Titel, Beschreibung, Tags – ein Klick, und die Idee ist im System.  

2. 🧠 **Semantische Analyse**  
   Beim Speichern wird über die OpenAI-API ein Embedding erzeugt und in ChromaDB abgelegt.

3. 🔍 **Ähnliche Ideen finden**  
   Über die Vektorsuche schlägt IdeaGraph thematisch verwandte Ideen vor.

4. 🕸️ **Netzwerk-Darstellung (später)**  
   Ideen erscheinen als Knoten-Graph, Relationen als Verbindungen.

---

## 🧰 Tech-Stack (aktuell)

- **Frontend:** .NET 9 Blazor WebAssembly (PWA, installierbar, kein Offline-Cache)
- **Backend:** Python 3.12 / FastAPI / Uvicorn
- **Vektordatenbank:** ChromaDB (Cloud)
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Kommunikation:** REST (JSON)



# Frontend entwickeln / starten
cd IdeaGraph.Wasm
dotnet run
