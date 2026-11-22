# Steppe Russisch 1.3 – Russisch für Kasachstan 🇰🇿

**20 Lektionen, 240 Lernvokabeln, 80 Beispielsätze, 320 natürliche russische Neural-Hörproben** und ein **offline verfügbares Russisch-Deutsch-Wörterbuch mit 56.514 Einträgen**.

## Neu: Dein persönlicher Lernpfad

In der Navigation auf **Mein Lernpfad** tippen. Steppe erstellt automatisch passende Lernempfehlungen aus deinem tatsächlichen Lernstand:
- **„Kann ich“** bei einer Vokabel verschiebt die nächste Wiederholung zunächst um einen Tag, danach um drei Tage und anschließend in längeren Abständen.
- **„Noch üben“** oder eine **falsche Quizantwort** markiert das Wort als unsicher und gibt ihm früher erneut eine Chance.
- Die **Lernrunde wird bei jedem neuen Start** neu zusammengestellt (bis zu zwölf Wörter/Sätze pro Runde), mit Schwerpunkt auf schwierigen, fälligen und neuen Wörtern.
- Ein passender **Wissenstest** fragt gezielt Wörter aus dem entsprechenden Lernstatus ab; dadurch ändert sich die nächste Empfehlung.
- Deine vorhandenen **Lernstände und Lektionsergebnisse aus Version 1.1 bleiben kompatibel**, weil die ursprünglichen acht Lektionen und ihre Audio-IDs unverändert sind.

Der Algorithmus funktioniert **lokal auf deinem Gerät, ohne Cloud-KI und ohne Konto**. Er erkennt keine gesprochene Aussprache; die Selbsteinschätzung erfolgt über die beiden Buttons und die Quiz-Antworten.

## Lerninhalte

Die ursprünglichen acht Lektionen bleiben bestehen. Zwölf zusätzliche Lektionen vermitteln:
1. Zeit & Verabredungen
2. Wetter & Kleidung
3. Metro, Bus & Taxi
4. Wege & Orientierung
5. Apotheke & Gesundheit
6. Arbeit & Studium
7. Handy & Internet
8. Kleidung & Einkaufen
9. Bank & Geldwechsel
10. Natur & Ausflüge
11. Wohnung & Unterkunft
12. Probleme & Notfälle

Insgesamt 20 Lektionen mit 240 Lernvokabeln und 80 Beispielsätzen. Die 320 eingebetteten MP3s werden beim Build bevorzugt durch die neuronale russische Stimme **Svetlana** erzeugt. Falls dieser externe Sprachdienst einzelne Aufnahmen nicht liefert, nutzt der Build als Reserve das lokal laufende neuronale Piper-Modell **Dmitri** (Sprachdatensatz CC0). Die Stimmen sind synthetisch, keine echten Sprecheraufnahmen. Die Tonfarbe kann deshalb in einzelnen Hörproben variieren. Im Android-Build sind alle Hörproben offline verfügbar. Sprache ist **Russisch** mit Alltagsschwerpunkt Kasachstan, **kein Kasachischkurs**.

## Großwörterbuch

Über **Wörterbuch → Großwörterbuch** findest du **56.514 unterschiedliche russische Stichwörter** mit deutschen Bedeutungen, außerdem Wortartenfilter, Suche in beide Richtungen und eine Merkliste. Diese Daten sind **offline eingebunden**. Anders als die 320 Kursaufnahmen haben die 56.514 Wörterbucheinträge **keine eigenen MP3-Dateien**. Ein Wörterbuch mit buchstäblich allen jemals verwendeten russischen Wörtern ist nicht möglich; Beugungsformen, Spezialvokabular und regionale Varianten sind teilweise unvollständig.

**Datenquelle und Lizenz:** <https://openrussian.org/>; Originaldaten: <https://github.com/Badestrand/russian-dictionary>, Commit `50e210c4803237779cb562bc1abcea529066031c`, unter **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, <https://creativecommons.org/licenses/by-sa/4.0/>. Bearbeitung: Zusammenführung gleicher Grundformen, Entfernung von Einträgen ohne deutsche Übersetzung, verkürzte Anzeigeform und kompaktes JSON. Der abgeleitete Wörterbuchdatensatz `dictionary/ru-de.js` steht ebenfalls unter **CC BY-SA 4.0**. Bitte diese Herkunfts- und Lizenzinformation bei jeder Weitergabe erhalten.

## Android-APK herunterladen

[GitHub Actions](https://github.com/fabi455/steppe-russisch-kasachstan/actions/workflows/android-apk.yml) öffnen, den **erfolgreichen Build** wählen, unter **Artifacts** `Steppe-Russisch-1.3-Adaptiv-APK` herunterladen, ZIP entpacken und `app-debug.apk` auf dem Android-Handy öffnen. Diese APK ist eine Debug-Version zur persönlichen Installation, kein Play-Store-Release.

**Vor einem möglicherweise nötigen Deinstallieren der alten App:** Unter Einstellungen **Lernstand exportieren** und die JSON-Sicherung nach Installation von Steppe 1.3 importieren. Android-Debug-APK-Signaturen können sich zwischen Builds unterscheiden.

Die Offline-Web-Version liegt ebenfalls als GitHub-Actions-Artefakt `Steppe-Russisch-1.3-Offline-Web` vor, wenn der Build erfolgreich ist.

## Selbst entwickeln / bauen

JDK 17, Android SDK 35 und Gradle 8.9; Python 3.12 für den Build, `edge-tts==7.3.1`, `piper-tts==1.8.0`, die Stimme `ru_RU-dmitri-medium` sowie FFmpeg sind erforderlich.

```bash
python3 tools/build_dictionary.py
python3 -m pip install edge-tts==7.3.1 piper-tts==1.8.0
mkdir -p voice && cd voice && python3 -m piper.download_voices ru_RU-dmitri-medium && cd ..
python3 tools/generate_audio.py
python3 tools/build_standalone.py
cd android && gradle --no-daemon :app:assembleDebug
```

Die OpenRussian-Wörterbuch-CSV-Dateien und Neural-MP3-Aufnahmen werden **zur Buildzeit** online heruntergeladen/erzeugt. Einmal gebaut, benötigt die fertige Android-App für Lerninhalte, Wörterbuch, Karteikarten, Audio und Fortschritt **keinen Internetzugang**.

Persönliche Lerndaten werden lokal gespeichert; keine Registrierung, Werbung oder Nutzerverfolgung. Der Service der Buildzeit-TTS-Stimme ist ein externer, inoffizieller Dienst, der sich ändern kann.

## Technischer Aufbau

- `content.js` und `content.json`: 20 Lektionen und 320 eindeutige Audio-IDs
- `adaptive.js`: lokaler Algorithmus für Wiederholungsabstände und individuelle Übungsauswahl
- `app.js`: Lernoberfläche, Quiz, Lernfortschritt, Karteikarten
- `dictionary/ui.js`: offline Wörterbuchsuche und Merkliste
- `tools/build_dictionary.py`: Download mit Prüfhash der Wörterbuchquelle, Aufbereitung in `dictionary/ru-de.js`
- `tools/generate_audio.py`: erzeugt 320 russische Neural-MP3s im `audio/`-Verzeichnis
- `tools/build_standalone.py`: portable Offline-Browser-Version mit Wörterbuch und Audio
- `android/` + `.github/workflows/android-apk.yml`: Android-App und automatischer CI-Build

Nicht offizielles Angebot Kasachstans.
