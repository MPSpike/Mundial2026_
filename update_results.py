#!/usr/bin/env python3
"""
Atualiza index.html com os resultados mais recentes do Mundial 2026.
Fonte: openfootball/worldcup.json (domínio público, sem API key)
"""

import json
import re
import urllib.request

JSON_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
HTML_FILE = "index.html"

# Mapa de nomes EN (fonte) -> PT (usado no HTML)
TEAM_MAP = {
    "Mexico": "México",
    "South Africa": "África do Sul",
    "South Korea": "Coreia do Sul",
    "Czech Republic": "Rep. Checa",
    "Canada": "Canadá",
    "Bosnia & Herzegovina": "Bósnia",
    "Bosnia and Herzegovina": "Bósnia",
    "Qatar": "Catar",
    "Switzerland": "Suíça",
    "USA": "EUA",
    "United States": "EUA",
    "Paraguay": "Paraguai",
    "Brazil": "Brasil",
    "Morocco": "Marrocos",
    "Haiti": "Haiti",
    "Scotland": "Escócia",
    "Australia": "Austrália",
    "Turkey": "Turquia",
    "Germany": "Alemanha",
    "Curacao": "Curaçao",
    "Curaçao": "Curaçao",
    "Ivory Coast": "Costa Marfim",
    "Cote d'Ivoire": "Costa Marfim",
    "Côte d'Ivoire": "Costa Marfim",
    "Ecuador": "Equador",
    "Netherlands": "Holanda",
    "Japan": "Japão",
    "Sweden": "Suécia",
    "Tunisia": "Tunísia",
    "Belgium": "Bélgica",
    "Egypt": "Egito",
    "Iran": "Irão",
    "New Zealand": "Nova Zelândia",
    "Spain": "Espanha",
    "Cape Verde": "Cabo Verde",
    "Saudi Arabia": "Ar. Saudita",
    "Uruguay": "Uruguai",
    "France": "França",
    "Senegal": "Senegal",
    "Iraq": "Iraque",
    "Norway": "Noruega",
    "Argentina": "Argentina",
    "Algeria": "Argélia",
    "Austria": "Áustria",
    "Jordan": "Jordânia",
    "Portugal": "Portugal",
    "DR Congo": "Congo",
    "Congo DR": "Congo",
    "Uzbekistan": "Uzbequistão",
    "Colombia": "Colômbia",
    "England": "Inglaterra",
    "Croatia": "Croácia",
    "Ghana": "Gana",
    "Panama": "Panamá",
}


def fetch_json():
    req = urllib.request.Request(JSON_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pt_name(en_name):
    return TEAM_MAP.get(en_name.strip(), en_name.strip())


def build_results(data):
    """Devolve dict {(team1_pt, team2_pt): (score1, score2)} para jogos com resultado final."""
    results = {}
    for match in data.get("matches", []):
        score = match.get("score", {})
        ft = score.get("ft")
        if not ft or len(ft) != 2:
            continue
        t1 = pt_name(match["team1"])
        t2 = pt_name(match["team2"])
        results[(t1, t2)] = (ft[0], ft[1])
    return results


def update_html(html, results):
    """Para cada bloco .match, se encontrar as duas equipas em results, preenche os value=."""

    # Padrão: captura o bloco match com nomes das equipas e os dois inputs de score
    pattern = re.compile(
        r'(<div class="match[^"]*"><span class="match-time">[^<]*</span>'
        r'<span class="match-teams">(?:🇵🇹\s*)?([^<]+?)\s*<span class="vs">vs</span>\s*'
        r'(?:🇵🇹\s*)?([^<]+?)</span>'
        r'<div class="match-right"><div class="score-area">'
        r'<input class="score-box" type="number" min="0" max="99"(?:\s+value="\d+")?>'
        r'<span class="score-sep">–</span>'
        r'<input class="score-box" type="number" min="0" max="99"(?:\s+value="\d+")?>)'
    )

    def repl(m):
        full_prefix = m.group(1)
        team1 = m.group(2).strip()
        team2 = m.group(3).strip()

        key = (team1, team2)
        rev_key = (team2, team1)

        if key in results:
            s1, s2 = results[key]
        elif rev_key in results:
            s2, s1 = results[rev_key]
        else:
            return m.group(0)  # sem resultado, não altera

        # Reconstruir o trecho com os valores
        new_block = full_prefix
        # Substitui os dois <input ...> no full_prefix
        new_inputs = (
            f'<input class="score-box" type="number" min="0" max="99" value="{s1}">'
            f'<span class="score-sep">–</span>'
            f'<input class="score-box" type="number" min="0" max="99" value="{s2}">'
        )

        # Remove a parte dos inputs antigos do prefix e adiciona os novos
        idx = new_block.find('<input class="score-box"')
        head = new_block[:idx]
        new_block = head + new_inputs
        return new_block

    return pattern.sub(repl, html)


def compute_standings(results, groups):
    """Calcula J,V,E,D,GM,GS,DG,Pts por equipa a partir dos resultados."""
    stats = {}

    def ensure(team):
        if team not in stats:
            stats[team] = {"J": 0, "V": 0, "E": 0, "D": 0, "GM": 0, "GS": 0}

    for (t1, t2), (s1, s2) in results.items():
        ensure(t1)
        ensure(t2)
        stats[t1]["J"] += 1
        stats[t2]["J"] += 1
        stats[t1]["GM"] += s1
        stats[t1]["GS"] += s2
        stats[t2]["GM"] += s2
        stats[t2]["GS"] += s1
        if s1 > s2:
            stats[t1]["V"] += 1
            stats[t2]["D"] += 1
        elif s2 > s1:
            stats[t2]["V"] += 1
            stats[t1]["D"] += 1
        else:
            stats[t1]["E"] += 1
            stats[t2]["E"] += 1

    standings = {}
    for team, s in stats.items():
        dg = s["GM"] - s["GS"]
        pts = s["V"] * 3 + s["E"]
        standings[team] = [s["J"], s["V"], s["E"], s["D"], s["GM"], s["GS"], dg, pts]

    return standings


def update_standings_js(html, standings):
    """Substitui o bloco standingsData no <script> por um novo gerado a partir dos resultados."""

    lines = []
    for team, vals in sorted(standings.items()):
        vals_str = ",".join(str(v) for v in vals)
        # Escapa nomes com caracteres especiais (não devia haver, mas por segurança)
        lines.append(f"  '{team}':".ljust(20) + f"[{vals_str}],")

    new_block = "const standingsData = {\n" + "\n".join(lines) + "\n};"

    pattern = re.compile(r"const standingsData = \{.*?\n\};", re.DOTALL)
    if pattern.search(html):
        html = pattern.sub(new_block, html, count=1)
    return html


def main():
    print("A obter dados do openfootball/worldcup.json...")
    data = fetch_json()

    results = build_results(data)
    print(f"Encontrados {len(results)} jogos com resultado final.")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    html = update_html(html, results)

    standings = compute_standings(results, None)
    html = update_standings_js(html, standings)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("index.html atualizado com sucesso.")


if __name__ == "__main__":
    main()
