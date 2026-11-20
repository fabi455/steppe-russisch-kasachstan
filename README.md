# Steppe – Russisch für Kasachstan 🇰🇿

Deutschsprachige Sprachlern-App auf Basis des Lernaufbaus von **Norrœna**, mit **8 Lektionen, 96 Vokabeln, 32 Sätzen**, wiederholbaren Quizfragen, Karteikarten mit Intervalltraining, Wörterbuch, Audio (normal/langsam), Fortschritt, Favoriten und Export/Import. **128 russische MP3-Hörbeispiele** werden beim Android-Build automatisch erzeugt und anschließend vollständig in die installierbare App eingebaut.

## Wie benutzen?

**Ohne Installation:** `Steppe-Russisch-Kasachstan-Offline.html` auf dem Gerät öffnen. Alle Lerninhalte und die Hörbeispiele sind darin enthalten; keine Verbindung nötig. Browser muss lokale HTML-Dateien öffnen können.

**Web-App:** Projektdateien entpacken und im Projektordner `python3 -m http.server 8000` ausführen; dann `http://localhost:8000` aufrufen. PWA per Browser-Menü installieren; alle Lerninhalte lassen sich nach dem ersten Besuch offline nutzen.

**Android-App:** Die APK gibt es über [GitHub Actions](https://github.com/fabi455/steppe-russisch-kasachstan/actions/workflows/android-apk.yml): Erfolgreichen Build öffnen, dann unter „Artifacts“ `Steppe-Russisch-Android-APK` herunterladen, ZIP entpacken und `app-debug.apk` installieren. Das Verzeichnis `android/` ist ein eigenständiges Android-WebView-Projekt mit den lokalen Lerninhalten. Zum Bauen Android SDK 35, JDK 17 und Gradle 8.9 installieren, danach im Verzeichnis `android` `gradle :app:assembleDebug` ausführen. Ergebnis: `android/app/build/outputs/apk/debug/app-debug.apk`. Alternativ das Repository auf GitHub veröffentlichen: `.github/workflows/android-apk.yml` erzeugt eine APK als GitHub Actions Artefakt. **Die Audio-Dateien werden im Workflow erzeugt, sodass der Quellcode ohne binäre Audiodateien auskommt.**

## Was wird gelernt?

1. Hallo, Kasachstan! – Begrüßungen
2. Ich spreche Russisch – Sich vorstellen
3. Tenge & Zahlen – Preise und Bezahlen
4. Unterwegs in der Stadt – Taxi, Flughafen, Wegbeschreibung
5. Bazar & Essen – Bestellen und Einkaufen
6. Freunde & Familie – Gespräche
7. Bahn & Reise – Fahrkarten und Zeiten
8. Hotel & Hilfe – Reservierung und Notsituationen

Der Fokus sind typische Gespräche auf Russisch in Kasachstan, **kein Kazakh-Sprachkurs**. Die kyrillische Schrift wird mit einer vereinfachten Umschrift zum Einstieg ergänzt; die Hörbeispiele wurden mit einer neuronalen russischen Stimme (Edge Read Aloud: Svetlana) synthetisiert und sind keine echten Sprecheraufnahmen.

## Datenschutz

Alle Daten bleiben lokal auf dem Gerät; keine Werbung, Konten, Tracker oder Cloud-Verbindung. Import und Export des Lernfortschritts als JSON.

## Quellen / landeskundlicher Hintergrund

- Kasachische Staatsverfassung, Art. 7: https://www.gov.kz/article/232335?lang=en
- Nationalbank Kasachstans zur Landeswährung Tenge: https://nationalbank.kz/en/page/currency-history

Kein offizielles Angebot der Republik Kasachstan. Version 1.1, Lernprojekt.

## Hinweis zur Web-App

Für den Betrieb über einen lokalen Webserver die Audiodateien einmal erzeugen: `python3 -m pip install edge-tts==7.3.1 && python3 tools/generate_audio.py`. Danach liegen sie unter `audio/`. Die Android-App enthält sie nach dem GitHub-Build komplett offline.

## Version 1.1 – natürlichere russische Stimme

Die alte eSpeak-Ausgabe wurde durch die russische Neuralstimme `ru-RU-SvetlanaNeural` ersetzt. Alle 128 Hörbeispiele werden **beim Build** über ein inoffizielles Edge-Read-Aloud-Modul erzeugt und anschließend vollständig **offline** in die APK gepackt. Die russische Neuralstimme klingt natürlicher, bleibt aber synthetisch. Audioaufnahmen von Muttersprachlern werden nicht vorgetäuscht. Fällt der Online-Dienst bei der Erstellung aus, schlägt der Build fehl, statt stillschweigend Roboter-Audio zu verwenden.

Der Lernfortschritt bleibt in der App erhalten, wenn sie über eine kompatibel signierte Version installiert wird. Bei GitHub-Debug-APKs kann das Signaturzertifikat zwischen Builds wechseln: Vor einem nötigen Deinstallieren **Einstellungen → Sicherung exportieren**, nach der Installation **Sicherung importieren**.
