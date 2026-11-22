# Steppe Russisch 1.4 – Russisch für Kasachstan 🇰🇿

## Einheitliche russische Stimme: Svetlana

Auf Wunsch wird das **Audio-Lernpaket** wieder vollständig auf `ru-RU-SvetlanaNeural` umgestellt (leichter Lernmodus: −7 % Sprechtempo). Die **128 ursprünglichen Aufnahmen** aus Steppe 1.1 werden übernommen, sofern ihre russischen Texte unverändert sind. Alle weiteren Wörter und Sätze werden mit **derselben Stimme** neu gesprochen.

Dafür verwendet `.github/workflows/content-updates.yml` 16 unabhängige Audiogruppen mit Wiederholungsversuchen. Jede einzelne neue MP3-Datei muss erfolgreich mit **Svetlana** erzeugt werden. **Es gibt keinen Ersatz durch Dmitri oder eSpeak.** Falls der externe Sprachdienst ausfällt, wird *kein* fehlerhaftes Sprachpaket veröffentlicht – die bisher installierten Aufnahmen bleiben verfügbar.

Wenn sämtliche **321 MP3-Dateien** geprüft sind, veröffentlicht GitHub ein neues Content-Release unter `content-latest`. Die bestehende Steppe-App ab **Version 1.4** kann unter **Einstellungen → Aktualisierungen → Lerninhalte aktualisieren** das neue Sprachpaket herunterladen, ohne die APK neu zu installieren. Nach dem erfolgreichen Herunterladen die Lernansicht neu öffnen. Die neuen Svetlana-Hörproben funktionieren anschließend auch **offline**. Andere Inhalte und der Lernstand bleiben erhalten.

Die Aufnahmen sind synthetische Stimmen, keine Aufnahmen echter Sprecherinnen. Der inoffizielle Edge-Read-Aloud-Dienst kann vorübergehend rate-limitieren oder ausfallen.

## NEU: Aktualisierungen ohne Deinstallation

Die Android-App 1.4 kann künftig neue **Wörter, Lektionen und russische Hörproben** als geprüftes Lernpaket von deinem GitHub abrufen. Neue Kursdaten erscheinen nach dem Neustart der Lernansicht – **ohne erneute APK-Installation**. Der Lernfortschritt und alle persönlichen Bewertungen bleiben unter dem bisherigen Schlüssel `steppe-russisch-kz-v1` auf dem Gerät.

- **Automatisch:** Steppe prüft neue Lernpakete ungefähr einmal pro Tag, sofern eine Internetverbindung besteht. Ohne Internet funktionieren die mitgelieferten Lektionen und Audiodateien wie bisher offline.
- **Manuell:** Unter **Einstellungen → Aktualisierungen → Lerninhalte aktualisieren**.
- **Sicherheit:** Der Download erfolgt ausschließlich per HTTPS von deinem GitHub. Das ZIP muss zu einer veröffentlichten SHA-256-Prüfsumme passen, alle Einträge dürfen nur Lerndaten und MP3s enthalten und bereits vorhandene Wort-IDs dürfen nicht verschwinden. Schlägt eine Prüfung fehl, bleibt der bisherige Lernstoff erhalten.
- **Veröffentlichung:** `.github/workflows/content-updates.yml` reagiert auf Änderungen an `content.json` / `content.js`, generiert fehlende MP3s mit einer neuronalen russischen Stimme und veröffentlicht das vollständige Offline-Lernpaket unter dem GitHub-Release-Tag `content-latest`. Die App erhält nur Daten, **keinen heruntergeladenen ausführbaren Code**.
- **Voraussetzung:** Neue Inhalte können erst nach der ersten erfolgreichen Veröffentlichung von `updates/latest.json` und `content-latest` abgerufen werden.

## App-Programmaktualisierungen – einmalig Signierung einrichten

Neue **Android-Funktionen** benötigen weiterhin eine neue APK. Damit Android diese wirklich **als Aktualisierung der vorhandenen App** akzeptiert und deinen Lernfortschritt erhält, müssen **Anwendungs-ID `com.steppe.russisch` und der private Signaturschlüssel über alle Updates gleich bleiben**. Android fordert bei einer APK-Aktualisierung möglicherweise weiterhin eine kurze Installationsbestätigung an. Vollautomatische Programmupdates sind normalerweise über den Play Store möglich.

Die vorherigen Test-APKs aus GitHub Actions wurden mit **wechselnden Debug-Schlüsseln** gebaut. **Darum kann der Wechsel zur ersten dauerhaft signierten Version leider einmalig die Sicherung des Lernstands, Deinstallation der alten App, Neuinstallation und den Import erfordern.** Danach ist bei folgenden App-Updates mit demselben Release-Schlüssel keine Deinstallation nötig.

Der CI-Build unterstützt eine dauerhaft stabile **Release-Signatur**, sobald in den GitHub-Repository-Secrets folgende vier Werte gesetzt wurden:

1. `STEPPE_KEYSTORE_B64`: Base64-kodierter Inhalt einer privaten Android-JKS-Datei
2. `STEPPE_STORE_PASSWORD`: Passwort der JKS-Datei
3. `STEPPE_KEY_ALIAS`: Alias des Schlüssels (z. B. `steppe`)
4. `STEPPE_KEY_PASSWORD`: Passwort des App-Schlüssels

Ein neues Schlüsselpaar kann auf einem vertrauenswürdigen Computer so erstellt werden:

```bash
keytool -genkeypair -v -keystore steppe-release.jks -storetype JKS \
  -alias steppe -keyalg RSA -keysize 3072 -validity 10000
base64 < steppe-release.jks | tr -d '\n' > steppe-keystore-base64.txt
```

**Wichtig:** Den privaten Schlüssel niemals in den öffentlichen GitHub-Code committen und nicht verlieren. Bewahre eine zweite, sichere Kopie auf. Die Base64-Datei dient nur zum einmaligen Eintragen des Secrets und sollte danach sicher gelöscht werden. GitHub-Secrets: `https://github.com/fabi455/steppe-russisch-kasachstan/settings/secrets/actions`.

Wenn der Schlüssel konfiguriert ist, veröffentlicht `.github/workflows/android-apk.yml` künftig bei neuen Programmversionen eine **signierte Release-APK** unter GitHub **Releases**. Unter **Einstellungen → App-Versionen ansehen** gelangst du dorthin. Ohne die vier Secrets gibt es weiterhin nur eine **Debug-Test-APK**, die noch keine verlässlichen In-Place-Programmupdates bietet.

---

# Steppe Russisch 1.3.1 – Russisch für Kasachstan 🇰🇿

**20 Lektionen, 241 Lernvokabeln, 80 Beispielsätze, 321 natürliche russische Neural-Hörproben** und ein **offline verfügbares Russisch-Deutsch-Wörterbuch mit 56.514 OpenRussian-Einträgen plus einem redaktionellen Zusatzwort**.

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

Insgesamt 20 Lektionen mit 241 Lernvokabeln und 80 Beispielsätzen. Die App übernimmt möglichst die **128 ursprünglichen Svetlana-Neural-Hörproben** aus dem bewährten Build von Version 1.1. Die **192 neuen Hörproben** entstehen zuverlässig offline durch das neuronale russische Piper-Modell **Dmitri** (Modelldokumentation siehe unten). Sollte das frühere Build-Artefakt nicht mehr verfügbar sein, erzeugt Piper auch die bisherigen 128 Clips neu. Alle Hörproben sind synthetisch, keine Aufnahmen echter Muttersprachler; zwischen älteren und neuen Lektionen können die Stimmen unterschiedlich klingen. Im Android-Build sind alle Hörproben offline verfügbar. Sprache ist **Russisch** mit Alltagsschwerpunkt Kasachstan, **kein Kasachischkurs**.

## Großwörterbuch

Über **Wörterbuch → Großwörterbuch** findest du **56.514 Stichwörter aus OpenRussian und einen weiteren redaktionellen Kurseintrag** mit deutschen Bedeutungen, außerdem Wortartenfilter, Suche in beide Richtungen und eine Merkliste. Diese Daten sind **offline eingebunden**. Anders als die 321 Kursaufnahmen haben die 56.514 Wörterbucheinträge **keine eigenen MP3-Dateien**. Ein Wörterbuch mit buchstäblich allen jemals verwendeten russischen Wörtern ist nicht möglich; Beugungsformen, Spezialvokabular und regionale Varianten sind teilweise unvollständig.

**Datenquelle und Lizenz:** <https://openrussian.org/>; Originaldaten: <https://github.com/Badestrand/russian-dictionary>, Commit `50e210c4803237779cb562bc1abcea529066031c`, unter **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, <https://creativecommons.org/licenses/by-sa/4.0/>. Bearbeitung: Zusammenführung gleicher Grundformen, Entfernung von Einträgen ohne deutsche Übersetzung, verkürzte Anzeigeform und kompaktes JSON. Der abgeleitete Wörterbuchdatensatz `dictionary/ru-de.js` steht ebenfalls unter **CC BY-SA 4.0**. Bitte diese Herkunfts- und Lizenzinformation bei jeder Weitergabe erhalten.

## Android-APK herunterladen

[GitHub Actions](https://github.com/fabi455/steppe-russisch-kasachstan/actions/workflows/android-apk.yml) öffnen, den **erfolgreichen Build** wählen, unter **Artifacts** `Steppe-Russisch-1.3.1-Wort-APK` herunterladen, ZIP entpacken und `app-debug.apk` auf dem Android-Handy öffnen. Diese APK ist eine Debug-Version zur persönlichen Installation, kein Play-Store-Release.

**Vor einem möglicherweise nötigen Deinstallieren der alten App:** Unter Einstellungen **Lernstand exportieren** und die JSON-Sicherung nach Installation von Steppe 1.3 importieren. Android-Debug-APK-Signaturen können sich zwischen Builds unterscheiden.

Die Offline-Web-Version liegt ebenfalls als GitHub-Actions-Artefakt `Steppe-Russisch-1.3.1-Offline-Web` vor, wenn der Build erfolgreich ist.

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

- `content.js` und `content.json`: 20 Lektionen und 321 eindeutige Audio-IDs
- `adaptive.js`: lokaler Algorithmus für Wiederholungsabstände und individuelle Übungsauswahl
- `app.js`: Lernoberfläche, Quiz, Lernfortschritt, Karteikarten
- `dictionary/ui.js`: offline Wörterbuchsuche und Merkliste
- `tools/build_dictionary.py`: Download mit Prüfhash der Wörterbuchquelle, Aufbereitung in `dictionary/ru-de.js`
- `tools/generate_audio.py`: erzeugt 321 russische Neural-MP3s im `audio/`-Verzeichnis
- `tools/build_standalone.py`: portable Offline-Browser-Version mit Wörterbuch und Audio
- `android/` + `.github/workflows/android-apk.yml`: Android-App und automatischer CI-Build

Nicht offizielles Angebot Kasachstans.

### Technischer Audio-Hinweis

Der GitHub-Build lädt die vorhandenen Svetlana-Clips optional aus dem erfolgreichen Steppe-1.1-GitHub-Artefakt. Alle fehlenden Dateien werden lokal mit dem von [Piper Voices](https://huggingface.co/rhasspy/piper-voices/tree/main/ru/ru_RU/dmitri/medium) bereitgestellten russischen Dmitri-Modell erzeugt. Die vorhandenen 128 MP3s werden dadurch nicht unnötig neu synthetisiert. Bitte die Lizenz und das Modellblatt des Sprachmodells vor kommerzieller Weitergabe beachten.

## Neu in Version 1.3.1: Понаехали!

Zur Lektion 20 wurde die Wendung **Понаехали!** (gesprochen etwa *ponajéchali*) hinzugefügt. Deutsche Bedeutung: **„Da sind aber viele Leute hergezogen!“**. Die Wendung ist umgangssprachlich und **oft abwertend gegenüber zugezogenen Menschen**; sie sollte eher verstanden als unbedacht selbst verwendet werden. Der Suchbegriff **Панаехоли** wird als vom Nutzer genannte, nicht standardmäßige Schreibweise erkannt. Die richtige Schreibweise ist **Понаехали!**. Für das Wort gibt es eine zusätzliche neuronale Offline-Hörprobe. Dadurch hat der Kurs **241 Vokabeln, 80 Beispielsätze und 321 Audioaufnahmen**.
