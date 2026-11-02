# Lernplan Big Data Processing — A3 und A4

**Erstellt:** 15. Oktober 2026 (Do, Woche 12)
**Zeitraum:** 15. Oktober – 2. November 2026
**Annahme:** etwa 4 Stunden pro Tag für BDP. Wenn andere Kurse (z. B. Deep Learning) in denselben Zeitraum fallen, verschieben sich die Puffertage, nicht die Abgabe.

## Termine

| Datum | Was | Gewicht |
|---|---|---|
| Fr 16.10., 10:30 | Q&A-Session, Raum 08.08.045 (A3- und A4-Fragen mitbringen) | — |
| Do 22.10., 23:59 | A3-Gruppen werden gesperrt (bei Einzelabgabe irrelevant) | — |
| **So 25.10., 23:59** | **A3 – Query Log Analysis mit Spark Streaming** | 25 % |
| vor A4 | LockDown Browser Practice Quiz (Pflicht) | — |
| **Mo 2.11., 00:01 – Di 3.11., 00:01** | **A4 – Timed Assessment**, 2 h ab Start, ein Versuch, Respondus LockDown Browser | 25 % |

A1 und A2 sind erledigt (A2 wurde am 3.10. bewertet). Eine Abschlussprüfung gibt es nicht. Offen sind also noch 50 % der Note.

## Zuerst: fehlende Canvas-Materialien herunterladen

Lokal fehlen die Inhalte, die für A3 und A4 am wichtigsten sind:

- [ ] **Woche 10 – Lecture-Folien** „Spark Streaming 1“ (lokal gibt es nur das Lab und die Code-Beispiele).
- [ ] **Woche 11 – Lecture** „Spark Streaming 2“.
- [ ] **Woche 11 – Practical** „Monitoring HDFS“ mit `spark-submit` und allen Code-Dateien. Laut Teaching Team ist das der Startpunkt für A3.
- [ ] **Woche 12 – Recording** von Kes Online-Lectorial am Di 13.10., 12:30. Darin wurde A4 erklärt; laut Ankündigung „DO NOT MISS“.
- [ ] Canvas-Seite *LockDown Browser Requirement* und eine eventuelle **A3-FAQ**-Diskussion.

Ablage: `Week 10/`, `Week 11/` und `Assignment 3/References/`. Die A3-Unterlagen (Spezifikation vom 6.10. mit aktualisiertem Appendix A, beide Querylog-CSVs und das Work-Log-Template) liegen bereits in `Assignment 3/`.

---

## Phase 1 — A3 fertigstellen (15.–25.10.)

Ziel ist, **am Fr 23.10. abzugeben**. Sa und So bleiben als Puffer. Parallel dazu täglich 30 Minuten A4-Wiederholung (siehe Phase 2, Wochen 1–5).

| Tag | Aufgabe | Fertig, wenn … |
|---|---|---|
| **Do 15.10.** | Canvas-Downloads erledigen (siehe oben). A3-Spezifikation komplett lesen und Fragen notieren. LockDown Practice Quiz machen. | Woche 10/11 liegt lokal, Fragenliste existiert, das Quiz läuft. |
| **Fr 16.10.** | Q&A um 10:30. Danach das Woche-11-Lab auf EMR durcharbeiten: `textFileStream` auf HDFS, `spark-submit`, Dateien mit `hadoop fs -put` nachschieben. | Ein Mini-Streaming-Job liest neue HDFS-Dateien und gibt Ergebnisse aus. |
| **Sa 17.10.** | Projektgerüst `streaming.a3` (ein `.scala`-File, Batch-Intervall 3 s, Argumente `input output threshold`). Textbereinigung und **Task 1** mit Ausgabe `task1-001`, `task1-002` … | Task-1-Ausgabe stimmt mit Appendix A überein. |
| **So 18.10.** | **Task 2**: Slow Queries, Threshold aus den Argumenten, max/avg/distinct users, Severity, vierstufige Sortierung. | Task-2-Ausgabe stimmt mit Appendix A überein. |
| **Mo 19.10.** | **Task 3**: `updateStateByKey`, Checkpoint unter `/s4271512/checkpoint`, NEW/INCREASED/UNCHANGED, Top 10. | Task-3-Ausgabe stimmt über beide Micro-Batches mit Appendix A überein. |
| **Di 20.10.** | **PG-Anforderung**: Task 3 nur ausgeben, wenn neue Dateien ankommen. Edge Cases testen: Header-Zeile, leere bereinigte Query, leere Batches, Gleichstände. | Leere Intervalle erzeugen keine Ordner, die Nummerierung bleibt lückenlos. |
| **Mi 21.10.** | Kompletter EMR-Lauf mit dem exakten Befehl aus der Spezifikation. Dateien nacheinander einspielen, `hadoop fs -cat` gegen Appendix A prüfen. JAR schlank halten. | Der Lauf mit dem Spezifikationsbefehl ist sauber und belegt. |
| **Do 22.10.** | Work Log (beide Abschnitte plus Checklist), Turnitin-PDF des Scala-Codes, ZIP mit nur `a3.jar` und `.scala`. | Drei Dateien: `s4271512_PG.zip`, `.pdf`, `.doc`. |
| **Fr 23.10.** | Abschluss-Audit (Namen, ZIP ohne Unterordner, PDF lesbar, DOC vollständig). **Abgeben.** | Abgabe in Canvas bestätigt. |
| Sa 24. – So 25.10. | Nur Puffer. | — |

### A3-Fallen aus der Spezifikation

- Die CSVs haben eine **Header-Zeile** (`query_id,user_id,…`), die gefiltert werden muss.
- Ausgabeordner tragen **laufende Nummern** pro Task (`task1-001`), keine Zeitstempel. Für ein leeres RDD wird kein Ordner angelegt.
- Genau **eine** `.scala`-Datei. Klasse `streaming.a3`. Pfade nicht hart codieren. Keine zusätzlichen `spark-submit`-Argumente.
- Stoppwörter und die Mindestlänge von 3 Zeichen werden **nach** dem Entfernen der Sonderzeichen angewendet. Records mit leerer bereinigter Query werden ignoriert.
- Task 2 sortiert nach: Severity aufsteigend (CRITICAL vor WARNING) → max DESC → count DESC → Query ASC.
- Task 3 rankt nach: accumulated DESC → current DESC → Query ASC.
- Bewertet wird auch das **Verständnis** von DStreams, Stateful Processing und Checkpointing. Die Design-Begründung im Work Log ist deshalb wichtig.

---

## Phase 2 — A4 vorbereiten (26.10.–1.11.)

**Wichtig:** A4 läuft im LockDown Browser, also ohne Notizen und ohne IDE. Der Cheat Sheet hilft dort nicht direkt. Lerne deshalb mit **Active Recall**: Datenfluss, Key-Value-Paare und Code-Muster aus dem Kopf aufschreiben, nicht nur nachlesen.

Inhalt und Fragetypen von A4 sind lokal nicht dokumentiert. Die Infos stehen im Recording vom 13.10. und kommen in den Q&A-Sessions. Passe die Schwerpunkte unten an, sobald du sie kennst.

| Tag | Wochen | Fokus | Stand im Learning Paper |
|---|---|---|---|
| **Mo 26.10.** | 1–3 | 3Vs, Scale out, HDFS (Blöcke, Replikation, NameNode/DataNode), YARN, MapReduce-Ablauf, Combiner, Partitioner, Shuffle/Sort | ausführlich |
| **Di 27.10.** | 4–5 | Pairs vs. Stripes, In-Mapper Combining, Secondary Sort, Order Inversion, Reduce-Side Joins, K-means als MapReduce | ausführlich |
| **Mi 28.10.** | 6–7 | Graphen: Adjazenzlisten, Parallel BFS / Shortest Path, ggf. PageRank. Pig (`GROUP`/`COGROUP`/`JOIN`, UDFs) und Hive | **dünn** – Folien L6 (132 S.) nacharbeiten |
| **Do 29.10.** | 8–9 | Mahout (Recommender), Solr, Storm (Spout/Bolt/Topologie). Spark: RDD, Lazy Evaluation, Lineage, Narrow vs. Wide, Transformationen vs. Actions | **dünn** – L8 und L9 (191 S.) nacharbeiten |
| **Fr 30.10.** | 10–11 | DStreams, Micro-Batches, Window-Operationen, `updateStateByKey`, Checkpointing, Accumulators/Broadcast. Eigenen A3-Code als Beispiel nutzen | **dünn bzw. fehlt** (Woche 11) |
| **Sa 31.10.** | alle | **Probeklausur unter Prüfungsbedingungen**: 2 h, ohne Unterlagen, selbst geschriebene Fragen aus allen Wochen. Danach Lücken auflisten. | — |
| **So 1.11.** | Lücken | Nur die Lücken vom Samstag schließen. LockDown Browser noch einmal starten. A4-Startzeit festlegen. | — |
| **Mo 2.11.** | — | **A4** mit Start zu einer festen, ausgeruhten Uhrzeit (Melbourne-Zeit). | — |

Zum Vorgehen pro Lerntag: Folien überfliegen, dann die Active-Recall-Fragen im Learning Paper ohne Nachsehen beantworten. Wo du hängst, bessere die passende Wochensektion im Learning Paper nach. Für die Wochen 6 und 8–11 lohnt sich das am meisten.

Während Phase 1 (je 30 Minuten pro Tag): Recall-Fragen der Wochen 1–5 durchgehen.
