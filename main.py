"""Gera o GIF de terminal (tema SQL / PostgreSQL) do topo do README.

Usa https://github.com/x0rzavi/github-readme-terminal (pacote `gifos`).
Roda pelo workflow .github/workflows/update-readme.yml. O conteudo e
estatico (nao consulta API), entao nao precisa de GITHUB_TOKEN.

Fluxo do GIF:
  1. "boot"  -> logs do servidor PostgreSQL subindo
  2. "login" -> psql conectando no banco `profile`
  3. "query" -> SELECT * FROM arthur.profile; em modo expandido (\\x)

O script troca apenas o bloco entre START/END_SECTION:terminal do README.
"""

import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import gifos

USERNAME = "arthurgvv"
FULL_NAME = "Arthur Goncalves"
DB_NAME = "profile"
PG_VERSION = "16.4"

TIMEZONE = ZoneInfo("America/Sao_Paulo")

README = Path(__file__).with_name("README.md")
START = "<!--START_SECTION:terminal-->"
END = "<!--END_SECTION:terminal-->"

# Cores ANSI
R = "\x1b[0m"
C_KEY = "\x1b[96m"   # ciano  -> nome da coluna
C_VAL = "\x1b[93m"   # amarelo -> valor
C_OK = "\x1b[92m"    # verde
C_SQL = "\x1b[94m"   # azul   -> palavras-chave SQL
C_DIM = "\x1b[90m"   # cinza  -> bordas / comentarios
C_LOG = "\x1b[95m"   # magenta -> nivel do log

PROMPT = f"\x1b[0;92m{DB_NAME}\x1b[0m=# "
SHELL = f"\x1b[0;91m{USERNAME}\x1b[0m@\x1b[0;93mdata-lake\x1b[0m:~$ "

TYPING = 2
BEAT = 8
HOLD_FINAL = 450  # ~30s parado no final (15 FPS)

ROW_H = 18
YPAD = 15
CONTENT_ROWS = 25

# Colunas do "registro" exibido no SELECT (sem acentos: a fonte do gifos
# nem sempre renderiza caracteres acentuados).
PROFILE = [
    ("name", "Arthur Goncalves"),
    ("age", "25"),
    ("location", "Belo Horizonte, MG - Brasil"),
    ("education", "Eng. de Software @ PUC Minas (5o periodo)"),
    ("role", "Data Engineer (em formacao)"),
    ("languages", "SQL, Python, PySpark"),
    ("platform", "Databricks"),
    ("architecture", "Medallion: Bronze > Silver > Gold"),
    ("focus", "ETL, Modelagem, Ingestao de dados"),
    ("dev", "Java, JavaScript, React, Vue, Node.js, C"),
    ("tools", "Docker, Git, GitHub, pgAdmin"),
    ("linkedin", "in/arthur-goncalves-62b15232a"),
    ("portfolio", "arthurgoncalves.vercel.app"),
]


def log(level: str, msg: str) -> str:
    return f"{C_DIM}[2026]{R} {C_LOG}{level}:{R}  {msg}"


def boot_sequence(t: gifos.Terminal) -> None:
    """Servidor PostgreSQL subindo - o 'boot' do perfil."""
    t.toggle_show_cursor(False)
    t.gen_text(f"{C_SQL}PostgreSQL {PG_VERSION}{R} - {FULL_NAME} Data Server", 1)
    t.gen_text(f"{C_DIM}pg_ctl: starting server process...{R}", 2, count=BEAT)
    t.gen_text(log("LOG", f"starting PostgreSQL {PG_VERSION} on x86_64-linux"), 4)
    t.gen_text(log("LOG", "listening on IPv4 address \"0.0.0.0\", port 5432"), 5)
    for i in range(0, 4096, 683):
        t.delete_row(7)
        t.gen_text(log("LOG", f"loading shared_buffers: {i}MB"), 7, contin=True)
    t.delete_row(7)
    t.gen_text(
        log("LOG", f"loading shared_buffers: 4096MB {C_OK}OK{R}"), 7, count=4, contin=True
    )
    t.gen_text(log("LOG", "schemas: bronze, silver, gold ... OK"), 8, count=4)
    t.gen_text(
        log("LOG", f"database system is {C_OK}ready to accept connections{R}"),
        9,
        count=BEAT,
    )
    t.gen_text("", 11, count=BEAT, contin=True)


def login_sequence(t: gifos.Terminal, now: str) -> None:
    t.clear_frame()
    t.gen_text(SHELL, 1)
    t.toggle_show_cursor(True)
    t.gen_typing_text(
        f"psql -h github.com -U {USERNAME} -d {DB_NAME}", 1, contin=True, speed=TYPING
    )
    t.toggle_show_cursor(False)
    t.gen_text(f"Password for user {USERNAME}: ", 2, count=BEAT)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*********", 2, contin=True, speed=TYPING)
    t.toggle_show_cursor(False)
    t.gen_text(f"psql ({PG_VERSION}) - last login: {now}", 3)
    t.gen_text(f'Type "help" for help.', 4, count=BEAT)


def query_sequence(t: gifos.Terminal) -> None:
    """SELECT no 'cartao de visita', no formato expandido do psql."""
    t.clear_frame()
    t.gen_prompt(1)
    t.clone_frame(BEAT)
    t.toggle_show_cursor(True)
    t.gen_typing_text("\\x", 1, contin=True, speed=TYPING)
    t.toggle_show_cursor(False)
    t.gen_text("Expanded display is on.", 2, count=BEAT)

    t.gen_prompt(3)
    t.toggle_show_cursor(True)
    t.gen_typing_text(
        f"{C_SQL}SELECT{R} * {C_SQL}FROM{R} arthur.profile;",
        3,
        contin=True,
        speed=TYPING,
    )
    t.toggle_show_cursor(False)

    width = max(len(k) for k, _ in PROFILE) + 1
    lines = [f"{C_DIM}-[ RECORD 1 ]{'-' * (width - 12)}+{'-' * 42}{R}"]
    for key, value in PROFILE:
        lines.append(f"{C_KEY}{key.ljust(width)}{R}{C_DIM}|{R} {C_VAL}{value}{R}")
    lines.append("")
    lines.append("(1 row)")
    t.gen_text("\n".join(lines), 4, count=BEAT)

    t.toggle_show_cursor(True)
    t.gen_prompt(t.curr_row + 1)
    t.gen_typing_text(
        f"{C_DIM}-- Building reliable, scalable data pipelines.{R}",
        t.curr_row,
        contin=True,
        speed=TYPING,
    )
    t.gen_text("", t.curr_row, count=HOLD_FINAL, contin=True)


def update_readme() -> None:
    """Troca SO o bloco entre os marcadores, preservando o resto do README."""
    content = README.read_text(encoding="utf-8")
    block = f"""{START}
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="./output.gif">
    <source media="(prefers-color-scheme: light)" srcset="./output.gif">
    <img alt="{FULL_NAME} - terminal SQL" src="./output.gif">
</picture>

<br>
{END}"""

    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)
    if not pattern.search(content):
        raise SystemExit(
            f"ERRO: marcadores {START} / {END} nao encontrados no README.md."
        )
    README.write_text(pattern.sub(lambda _: block, content), encoding="utf-8")
    print("INFO: bloco do terminal atualizado no README.md")


def main() -> None:
    now_dt = datetime.now(TIMEZONE)
    now = now_dt.strftime("%a %b %d %H:%M %Y")

    height = YPAD * 2 + CONTENT_ROWS * ROW_H
    t = gifos.Terminal(750, height, 15, YPAD)
    t.set_prompt(PROMPT)

    boot_sequence(t)
    login_sequence(t, now)
    query_sequence(t)

    t.gen_gif()
    update_readme()


if __name__ == "__main__":
    main()
