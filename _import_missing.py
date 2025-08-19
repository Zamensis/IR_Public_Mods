import os, re, yaml
from collections import defaultdict

def collect_all_french_translations(french_root):
    """
    Collects all French translations into a dict: key -> translated value.
    Priority:
        1. Files outside 'Vanilla'
        2. Then files inside 'Vanilla' (only if key not already set)
    Skips any file inside a 'generated' folder.
    """
    translations = {}

    def scan_files(priority):
        for root, _, files in os.walk(french_root):
            parts = root.split(os.sep)
            if 'generated' in parts:
                continue

            in_vanilla = 'Vanilla' in parts
            if (priority == 'non_vanilla' and in_vanilla) or (priority == 'vanilla' and not in_vanilla):
                continue

            for file in files:
                if file.endswith('_l_french.yml'):
                    full_path = os.path.join(root, file)
                    with open(full_path, 'r', encoding='utf-8-sig') as f:
                        for line in f:
                            # Ignorer les lignes commentées
                            if line.lstrip().startswith('#'):
                                continue

                            if ':' not in line:
                                continue

                            match = re.match(r'^\s*([^:]+):(?:\d+)?\s*(.*)', line)
                            if match:
                                key = match.group(1).strip()
                                value = match.group(2).strip()
                                if key not in translations:
                                    translations[key] = value

    # 1. Priorité aux fichiers non-Vanilla
    scan_files(priority='non_vanilla')
    # 2. Puis fichiers Vanilla (si clé absente)
    scan_files(priority='vanilla')

    return translations

def fix_language_header(file_path):
    """Replaces the first instance of 'l_english:' with 'l_french:'"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == 'l_english:':
            lines[i] = 'l_french:\n'
            break  # only replace the first occurrence

    with open(file_path, 'w', encoding='utf-8-sig') as f:
        f.writelines(lines)

def process_english_file(eng_path, output_path, fr_dict):
    missing_keys = []
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(eng_path, 'r', encoding='utf-8-sig') as eng:
        lines = eng.readlines()

    new_lines = []

    for line in lines:
        # Garder la fin de ligne telle quelle
        line_ending = ''
        if line.endswith('\r\n'):
            line_ending = '\r\n'
            line_core = line[:-2]
        elif line.endswith('\n'):
            line_ending = '\n'
            line_core = line[:-1]
        else:
            line_core = line

        if ':' in line_core and not line_core.lstrip().startswith('#'):
            match = re.match(r'^(\s*)([^:]+):(?:\s*(\d+))?\s*(.*)', line_core)
            if match:
                indent = match.group(1)
                key = match.group(2).strip()
                version = match.group(3)  # peut être None
                eng_value = match.group(4)

                value = fr_dict.get(key, eng_value)
                if key not in fr_dict:
                    missing_keys.append(key)

                if version is None:
                    new_line_core = f"{indent}{key}: {value}"
                else:
                    new_line_core = f"{indent}{key}:{version} {value}"

                new_lines.append(new_line_core + line_ending)
                continue

        # Sinon ligne inchangée
        new_lines.append(line)

    with open(output_path, 'w', encoding='utf-8-sig') as out:
        out.writelines(new_lines)

    fix_language_header(output_path)
    return missing_keys

def replicate_and_merge(english_root, french_root, output_root):
    fr_dict = collect_all_french_translations(french_root)
    all_missing = {}

    for dirpath, _, files in os.walk(english_root):
        for file in files:
            if file.endswith('_l_english.yml'):
                rel_dir = os.path.relpath(dirpath, english_root)
                base_name = file.replace('_l_english.yml', '')
                eng_path = os.path.join(dirpath, file)
                out_rel_path = os.path.join(rel_dir, f'{base_name}_l_french.yml')
                out_path = os.path.join(output_root, out_rel_path)

                print(f"[PROCESSING] {eng_path}")
                missing_keys = process_english_file(eng_path, out_path, fr_dict)
                print(f"  └─ {len(missing_keys)} missing translation(s) filled with English")

                if missing_keys:
                    # Stocker la liste par chemin relatif dans generated (avec slash normalisé)
                    key_for_dict = out_rel_path.replace(os.sep, '/')
                    all_missing[key_for_dict] = missing_keys

    # Écriture du fichier YAML listant les clés manquantes par fichier
    if all_missing:
        missing_file_path = os.path.join(output_root, '_missing_translations.yml')
        with open(missing_file_path, 'w', encoding='utf-8') as yf:
            yaml.dump(all_missing, yf, allow_unicode=True, sort_keys=True)

        print(f"\n[SUMMARY] Missing keys summary written to: {missing_file_path}")
    else:
        print("\n[SUMMARY] No missing keys found.")
    
def verify_translations():
    from glob import glob
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    english_dir = os.path.join(base_dir, 'english')
    generated_dir = os.path.join(base_dir, 'french', 'generated')

    for eng_path in glob(os.path.join(english_dir, '**', '*_l_english.yml'), recursive=True):
        rel_path = os.path.relpath(eng_path, english_dir)
        fr_path = os.path.join(generated_dir, rel_path.replace('_l_english.yml', '_l_french.yml'))

        if not os.path.exists(fr_path):
            print(f"[MISSING] French file not generated: {fr_path}")
            continue

        with open(eng_path, encoding='utf-8-sig') as ef, open(fr_path, encoding='utf-8-sig') as ff:
            e_lines = [l for l in ef if ':' in l and not l.lstrip().startswith('#')]
            f_lines = [l for l in ff if ':' in l and not l.lstrip().startswith('#')]

            if len(e_lines) != len(f_lines):
                print(f"[MISMATCH] Line count differs: {rel_path} ({len(e_lines)} EN vs {len(f_lines)} FR)")
                
def detect_duplicate_keys_across_files(root_dir, lang_code, output_filename):
    """
    Détecte toutes les clés apparaissant plusieurs fois dans un ou plusieurs fichiers
    _l_<lang_code>.yml sous root_dir.

    Trie le résultat selon :
    1. Le premier dossier/fichier où la clé apparaît
    2. L'ordre des chemins pour les fichiers associés à chaque clé
    """
    key_sources = defaultdict(list)  # key -> list of relative file paths (may include duplicates)

    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(f'_l_{lang_code}.yml'):
                full_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(full_path, root_dir).replace(os.sep, '/')

                with open(full_path, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        if ':' in line and not line.lstrip().startswith('#'):
                            match = re.match(r'^\s*([^:]+):(?:\d+)?\s*.*', line)
                            if match:
                                key = match.group(1).strip()
                                key_sources[key].append(rel_path)

    # Garder uniquement les clés avec plus d’une occurrence
    duplicates = {
        key: sorted(paths, key=lambda p: (p.count('/'), p))  # trie les fichiers par profondeur puis alphab.
        for key, paths in key_sources.items()
        if len(paths) > 1
    }

    # Trier les clés selon le premier fichier (chemin + profondeur)
    sorted_items = sorted(
        duplicates.items(),
        key=lambda item: (item[1][0].count('/'), item[1][0])
    )

    # Formatage final
    if sorted_items:
        with open(output_filename, 'w', encoding='utf-8') as out:
            for key, sources in sorted_items:
                out.write(f"- {key} ({', '.join(sources)})\n")

        print(f"[DUPLICATES] Duplicate keys written to: {output_filename}")
    else:
        print(f"[DUPLICATES] No duplicate keys found in {lang_code} files.")

if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    english_dir = os.path.join(base_dir, 'english')
    french_dir = os.path.join(base_dir, 'french')
    output_dir = os.path.join(french_dir, 'generated')

    replicate_and_merge(english_dir, french_dir, output_dir)
    verify_translations()
    detect_duplicate_keys_across_files(english_dir, 'english', os.path.join(output_dir, '_duplicate_english.yml'))
    detect_duplicate_keys_across_files(french_dir, 'french', os.path.join(output_dir, '_duplicate_french.yml'))