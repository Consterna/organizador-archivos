"""
Módulo de interfaz de consola y estilos con colores ANSI.
"""

import sys
import os

# Configurar stdout y stderr para UTF-8 en Windows para admitir caracteres y emojis
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Habilitar soporte de colores ANSI en terminales de Windows
if sys.platform == "win32":
    try:
        os.system("")
    except Exception:
        pass


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}====================================================
 [📁] ORGANIZADOR INTELIGENTE DE ARCHIVOS v1.0
===================================================={Colors.RESET}
"""
    print(banner)


def success(msg: str):
    print(f"{Colors.GREEN}[✓] {msg}{Colors.RESET}")


def info(msg: str):
    print(f"{Colors.BLUE}[i] {msg}{Colors.RESET}")


def warning(msg: str):
    print(f"{Colors.YELLOW}[!] {msg}{Colors.RESET}")


def error(msg: str):
    print(f"{Colors.RED}[x] {msg}{Colors.RESET}")


def header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.HEADER}--- {msg} ---{Colors.RESET}")
