#!/bin/bash

# Definer stien til det specifikke Python-miljø
PYTHON_ENV="/home/specialminds/phython/bin/activate"

# 1. Definer stien til repos.json filen
REPOS_FILE="/home/specialminds/discord-bot/repos.json"

# 2. Skift til mappen, hvor spillene skal gemmes
cd /home/specialminds/webgames || { echo "Kan ikke navigere til /home/specialminds/webgames"; exit 1; }

# 3. Læs repos.json filen og klon/opdater hvert repository
if [ -f "$REPOS_FILE" ]; then
    #echo "Læser repository-listen fra $REPOS_FILE"
    repos=$(jq -r '.[]' "$REPOS_FILE")  # Bruger jq til at parse JSON-fil

    # Opret en liste over de repository-navne, der er angivet i repos.json
    declare -A repo_names_in_file
    for repo_url in $repos; do
        repo_name=$(basename "$repo_url" .git)  # Ekstraher repo-navnet fra URL
        repo_names_in_file["$repo_name"]=1

        # Hvis mappen eksisterer, opdater den, ellers klon den
        if [ -d "$repo_name" ]; then
            #echo "Opdaterer repository: $repo_name"
            cd "$repo_name" || { echo "Kan ikke navigere til $repo_name"; exit 1; }
            git pull -f
            cd ..
        else
            echo "Kloner repository: $repo_name"
            git clone "$repo_url"
        fi
    done

    # 4. Find og slet mapper, der ikke længere er i repos.json
    for existing_repo in */; do
        repo_dir_name=$(basename "$existing_repo")
        if [[ -z "${repo_names_in_file[$repo_dir_name]}" ]]; then
            rm -rf "$repo_dir_name"
        fi
    done

else
    echo "$REPOS_FILE ikke fundet. Sørg for at botten har oprettet denne fil med overvågede repositories."
    exit 1
fi

# 5. Navigér til Retropie ports mappe
cd /home/specialminds/RetroPie/roms/ports/ || { echo "Kan ikke navigere til /home/specialminds/RetroPie/roms/ports/"; exit 1; }

# 6. Slet genveje til spil, der ikke længere findes i GitHub-repoet
for sh_file in *.sh; do
    game_name="${sh_file%.sh}"  # Fjern .sh-udvidelsen for at få spilnavnet
    if [ ! -d "/home/specialminds/webgames/$game_name" ]; then
        #echo "Sletter genvej for: $game_name, da mappen ikke længere findes"
        rm "$sh_file"
    fi
done

# 7. Opret genveje for spil, hvis der findes en index.html-, main.py- eller .x86_64-fil
#echo "Opretter genveje for spil, der har en index.html-, main.py- eller .x86_64-fil"
for repo_dir in /home/specialminds/webgames/*; do
    if [ -d "$repo_dir" ]; then
        repo_name=$(basename "$repo_dir")

        # Find alle spilmapper inde i repo-mappen
        for game in "$repo_dir"/*; do
            if [ -d "$game" ]; then
                game_name=$(basename "$game")

                # Tjek om der findes en index.html-fil (til webspil)
                if [ -f "$game/index.html" ]; then
                    sh_file="/home/specialminds/RetroPie/roms/ports/${game_name}.sh"
                    if [ ! -f "$sh_file" ]; then
                        echo "#!/bin/bash" > "$sh_file"
                        echo "google-chrome --password-store=basic --kiosk \"http://localhost:8000/${game_name}/index.html\"" >> "$sh_file"
                        chmod +x "$sh_file"
                        echo "Genvej oprettet for webspillet: $game_name"
                    fi

                # Tjek om der findes en main.py-fil (til Python-spil)
		elif [ -f "$game/main.py" ]; then
		    sh_file="/home/specialminds/RetroPie/roms/ports/${game_name}.sh"
		    if [ ! -f "$sh_file" ]; then
			echo "#!/bin/bash" > "$sh_file"
			echo "source $PYTHON_ENV" >> "$sh_file"
			echo "python /home/specialminds/webgames/${repo_name}/${game_name}/main.py --fullscreen" >> "$sh_file"
			chmod +x "$sh_file"
			echo "Genvej oprettet for Python-spillet: $game_name"
		    fi

                # Tjek om der findes en .x86_64-fil (til Linux eksekverbare spil)
                elif [ -f "$game/${game_name}.x86_64" ]; then
                    sh_file="/home/specialminds/RetroPie/roms/ports/${game_name}.sh"
                    if [ ! -f "$sh_file" ]; then
                        echo "#!/bin/bash" > "$sh_file"
                        echo "/home/specialminds/webgames/${repo_name}/${game_name}/${game_name}.x86_64" >> "$sh_file"
                        chmod +x "$sh_file"
                        echo "Genvej oprettet for Linux-spillet: $game_name"
                    fi
                else
                    echo "Ingen index.html, main.py eller .x86_64 fundet for: $game_name. Genvej oprettes ikke."
                fi

                # 8. Tjek om der findes en .png-fil (til ikon) og kopier den, hvis den findes
                icon_file="$game/icon.png"
                if [ -f "$icon_file" ]; then
                    #echo "Ikon fundet for spil: $game_name. Kopierer ikon."
                    cp "$icon_file" "/home/specialminds/RetroPie/roms/ports/${game_name}.png"
                fi
            fi
        done
    fi
done
