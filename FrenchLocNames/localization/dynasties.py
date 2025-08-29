# script: format_families_final.py

# Lire le fichier d'entrée
with open("dynasties.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Séparer toutes les entrées par espaces ou tabulations
entries = content.split()  # split() gère les espaces et tabulations multiples

formatted_lines = []

for entry in entries:
    if not entry.strip():
        continue
    last_part = entry.split(".")[-1]  # ne garder que la dernière partie
    formatted_lines.append(f' {last_part}:0 "des {last_part}"')

# Écrire dans le fichier de sortie
with open("dynasties_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(formatted_lines))

print(f"{len(formatted_lines)} familles ont été formatées et écrites dans families_output.txt")
