"""Windows: fuerza el modo UTF-8 de Python. Los JSON y guiones llevan tildes y el valor por
defecto en Windows es cp1252 (la narración llegaría rota al TTS). Se importa lo primero."""
import os, subprocess, sys

if os.name == "nt" and not sys.flags.utf8_mode and os.path.isfile(sys.argv[0]):
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", *sys.argv]))
