# script: format_names.py

# Lire le fichier d'entrée
with open("names.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Séparer les noms par espace
names = content.split()

# Créer le contenu formaté
formatted_lines = [f' {name}:0 "{name}"' for name in names]

# Écrire dans le fichier de sortie
with open("names_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(formatted_lines))

print(f"{len(names)} noms ont été formatés et écrits dans output.txt")
