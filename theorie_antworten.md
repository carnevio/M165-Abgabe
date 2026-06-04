# Theorie-Antworten – MongoDB Modul

## 1.1 Was ist ein ODM?

ODM steht für **Object Document Mapper**.

Kurz gesagt ist ein ODM ein "Übersetzer" zwischen deinem Python/C#-Code und MongoDB. Ohne ODM müsstest du immer direkt mit rohen MongoDB-Abfragen arbeiten und die Ergebnisse selbst in Objekte umwandeln. Der ODM macht das automatisch für dich.

Ein Beispiel: Du hast eine Klasse `Restaurant` in Python. Der ODM sorgt dafür, dass du einfach `restaurant.save()` aufrufen kannst – und er speichert das Objekt als Document in MongoDB. Beim Lesen passiert das Gleiche in die andere Richtung.

Das ist eigentlich dasselbe Konzept wie ein ORM (Object Relational Mapper, z.B. Entity Framework bei C#), nur eben für dokumentenbasierte Datenbanken statt für SQL.

Bekannte ODMs: `MongoEngine` und `Beanie` für Python.

---

## 4.1 Umgebungsvariablen lesen

```python
import os

path = os.environ.get("PATH")
print(path)
```

`os.environ` ist quasi ein Dictionary, das alle Umgebungsvariablen des Systems enthält. Mit `.get("KEY")` holst du den Wert raus – wenn die Variable nicht existiert, kommt einfach `None` zurück statt einem Fehler. Willst du stattdessen einen Fehler wenn sie fehlt, kannst du `os.environ["KEY"]` schreiben.

---

## 7.1 Files in MongoDB (GridFS)

### a) Welche Collections werden erstellt?

Wenn du eine Datei mit GridFS speicherst, tauchen in der Datenbank automatisch **zwei neue Collections** auf:

| Collection | Was drin ist |
|---|---|
| `fs.files` | Infos zur Datei: Name, Grösse, Upload-Datum, usw. |
| `fs.chunks` | Die eigentlichen Dateidaten, aufgeteilt in kleine Blöcke |

### b) Wie hängen die einzelnen Documents zusammen?

GridFS zerschneidet eine Datei in mehrere Chunks (standardmässig je 255 KB). Damit es später wieder zusammengesetzt werden kann, hat jeder Chunk ein Feld namens `files_id` – das ist die `_id` des zugehörigen Eintrags in `fs.files`. Ausserdem gibt es ein Feld `n`, das die Reihenfolge der Chunks angibt.

```
fs.files:  { _id: ObjectId("abc123"), filename: "foto.jpg", ... }
fs.chunks: { files_id: ObjectId("abc123"), n: 0, data: ... }
fs.chunks: { files_id: ObjectId("abc123"), n: 1, data: ... }
```

Beim Herunterladen sucht MongoDB alle Chunks mit der passenden `files_id` und setzt sie anhand von `n` wieder in der richtigen Reihenfolge zusammen.

### c) In welcher Codierung werden die Rohdaten gespeichert?

Die Rohdaten werden als **BSON Binary** gespeichert (`BinData`). Das ist das native Binärformat von MongoDB. Wenn man es z.B. in Compass oder als JSON exportiert, sieht man die Daten als **Base64-String** – das ist einfach die Textdarstellung von Binärdaten.
