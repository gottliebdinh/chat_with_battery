# chat_with_battery

## Grundvoraussetzung: python 3 (mit pip lol)

## Discord beitreten
https://discord.gg/AejHQ4Eb

## requirements installieren:

'
pip install pandas json ollama matplotlib requests
'


(Ganzer Ollama teil fällt weg, sobald wir nen OpenAI Api Key haben)
## ollama runterladen 
https://ollama.com
dann modell runterladen: ich benutze aktuell gpt-oss, weil relativ gut und passt gut auf mein M2 max mit 64gb. Bei Macbook Air vllt eher für Demo einfach gemma:1b oder so benutzen.

## modell laufen lassen
dann in neuem terminal ollama öffnen
'
ollama serve
'
# ausführen
'
python dataclean.py
'
(modell sollte beim erstmaligen ausführen automatisch runtergeladen werden. Deswegen könnte es beim ersten Starten etwas dauern. Falls das nicht funktioniert: ollama pull gemma3:1b )