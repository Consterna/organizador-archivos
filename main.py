#!/usr/bin/env python3
"""
Organizador Inteligente de Archivos
Punto de entrada principal del CLI interactivo y automatizado.
"""

import argparse
import sys
from pathlib import Path
from organizer.config import ConfigManager
from organizer.engine import OrganizerEngine, FilePlan
from organizer.history import HistoryManager
from organizer.sandbox import create_sandbox
from organizer.ui import Colors, print_banner, success, info, warning, error, header


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_SANDBOX_DIR = BASE_DIR / "sandbox_test"


def display_plan(plans: list[FilePlan], target_dir: Path):
    if not plans:
        warning(f"No se encontraron archivos para organizar.")
        return

    header(f"Plan de Organización ({len(plans)} archivos detectados)")
    
    # Agrupar por categoría
    by_cat = {}
    for p in plans:
        by_cat.setdefault(p.category, []).append(p)

    for cat, items in sorted(by_cat.items()):
        print(f"\n[{cat}] ({len(items)} archivos):")
        for item in items:
            if item.destination is None:
                print(f"   * {item.source.name}  ->  {Colors.RED}[SE ELIMINARÁ - DUPLICADO EXACTO]{Colors.RESET}")
            else:
                dup_tag = f" {Colors.YELLOW}[Duplicado detectado]{Colors.RESET}" if item.is_duplicate else ""
                try:
                    rel_dest = item.destination.relative_to(target_dir)
                except ValueError:
                    rel_dest = item.destination
                print(f"   * {item.source.name}  ->  {Colors.GREEN}{rel_dest}{Colors.RESET}{dup_tag}")

    print(f"\n{Colors.BOLD}Resumen:{Colors.RESET} {len(plans)} archivos listos para organizar en {len(by_cat)} categorías.\n")


def cmd_simulate(source_dir: Path, target_dir: Path, config: ConfigManager, mode: str):
    info(f"Escaneando directorio: {source_dir.resolve()} (Modo: {mode})")
    info(f"Destino principal: {target_dir.resolve()}")
    engine = OrganizerEngine(source_dir, target_dir, config, mode=mode)
    plans = engine.plan()
    display_plan(plans, target_dir)
    return plans


def cmd_organize(source_dir: Path, target_dir: Path, config: ConfigManager, mode: str, confirm_prompt: bool = True):
    engine = OrganizerEngine(source_dir, target_dir, config, mode=mode)
    plans = engine.plan()
    
    if not plans:
        warning(f"No hay archivos para mover en {source_dir}")
        return

    display_plan(plans, target_dir)
    if confirm_prompt:
        confirm = input(f"{Colors.YELLOW}¿Deseas proceder con el movimiento de estos {len(plans)} archivos? (s/n): {Colors.RESET}").strip().lower()
        if confirm not in ["s", "si", "y", "yes"]:
            info("Operación cancelada por el usuario.")
            return

    succ, err, session_id = engine.execute(plans)
    if succ > 0:
        success(f"Se organizaron exitosamente {succ} archivos.")
        info(f"ID de sesión guardado para Undo: {session_id}")
    if err > 0:
        error(f"Ocurrieron errores con {err} archivos:")
        for p in plans:
            if p.status.startswith("ERROR"):
                print(f"   - {Colors.RED}{p.source.name}{Colors.RESET}: {p.status}")


def cmd_undo(target_dir: Path):
    history_mgr = HistoryManager(target_dir)
    ok, msg, count = history_mgr.undo_last_session()
    if ok:
        success(msg)
    else:
        warning(msg)


def cmd_create_sandbox(sandbox_dir: Path):
    count = create_sandbox(sandbox_dir)
    success(f"Entorno Sandbox creado en: {sandbox_dir.resolve()}")
    info(f"Se crearon {count} archivos de prueba variados para experimentar con seguridad.")


def cmd_show_config(config: ConfigManager):
    header("Reglas y Categorías Actuales")
    for cat, exts in config.data.get("categories", {}).items():
        print(f"  {Colors.CYAN}{cat:15}{Colors.RESET} : {', '.join(exts)}")
    print(f"\n  {Colors.YELLOW}Archivos ignorados{Colors.RESET}: {', '.join(config.data.get('ignored_names', []))}")
    print(f"  {Colors.YELLOW}Extensiones ignoradas{Colors.RESET}: {', '.join(config.data.get('ignored_extensions', []))}")
    print(f"  {Colors.YELLOW}Categoría por defecto{Colors.RESET}: {config.data.get('default_category', 'Otros')}\n")


def interactive_menu():
    print_banner()
    config = ConfigManager(DEFAULT_CONFIG_PATH)
    
    current_source = Path(config.data.get("source_directory", str(DEFAULT_SANDBOX_DIR)))
    current_target = Path(config.data.get("target_directory", str(DEFAULT_SANDBOX_DIR)))

    while True:
        src_display = f"{current_source.resolve()}" if current_source.exists() else f"{current_source.resolve()} (no existe)"
        tgt_display = f"{current_target.resolve()}"
        
        print(f"{Colors.BOLD}Carpeta de ORIGEN (dónde busca):{Colors.RESET}  {Colors.BLUE}{src_display}{Colors.RESET}")
        print(f"{Colors.BOLD}Carpeta de DESTINO (dónde mueve):{Colors.RESET} {Colors.GREEN}{tgt_display}{Colors.RESET}")
        print("\nOpciones disponibles:")
        print("  [1] 🔍 Analizar y simular organización (Dry-Run)")
        print("  [2] 🚀 Organizar archivos ahora")
        print("  [3] ↩️ Deshacer última organización (Undo)")
        print("  [4] 🧪 Crear/Restaurar carpeta de prueba (Sandbox)")
        print("  [5] 📂 Cambiar carpeta origen y destino temporalmente")
        print("  [6] 📋 Ver reglas de configuración")
        print("  [0] 🚪 Salir")

        choice = input(f"\n{Colors.BOLD}Selecciona una opción [0-6]: {Colors.RESET}").strip()

        if choice == "1":
            if not current_source.exists():
                warning("La carpeta origen no existe.")
            else:
                cmd_simulate(current_source, current_target, config, mode="by_category")
        elif choice == "2":
            if not current_source.exists():
                warning("La carpeta origen no existe.")
            else:
                cmd_organize(current_source, current_target, config, mode="by_category")
        elif choice == "3":
            cmd_undo(current_target)
        elif choice == "4":
            cmd_create_sandbox(DEFAULT_SANDBOX_DIR)
            current_source = DEFAULT_SANDBOX_DIR
            current_target = DEFAULT_SANDBOX_DIR
        elif choice == "5":
            new_src = input("Ingresa la ruta completa de la carpeta de ORIGEN: ").strip('"\' ')
            new_tgt = input("Ingresa la ruta completa de la carpeta de DESTINO: ").strip('"\' ')
            if new_src:
                current_source = Path(new_src)
            if new_tgt:
                current_target = Path(new_tgt)
            success("Rutas actualizadas temporalmente.")
        elif choice == "6":
            cmd_show_config(config)
        elif choice == "0":
            info("¡Hasta luego!")
            break
        else:
            warning("Opción no válida. Ingresa un número del 0 al 6.")
        
        input(f"\n{Colors.DIM}Presiona Enter para continuar...{Colors.RESET}")
        print("\n" + "-" * 50 + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Organizador Inteligente de Archivos")
    parser.add_argument("--source", "-s", type=str, help="Ruta de la carpeta a escanear (origen)")
    parser.add_argument("--target", "-t", type=str, help="Ruta de la carpeta principal de destino")
    parser.add_argument("--dry-run", action="store_true", help="Simula los movimientos sin realizarlos")
    parser.add_argument("--run", action="store_true", help="Ejecuta la organización directamente")
    parser.add_argument("--undo", action="store_true", help="Revierte la última organización realizada")
    parser.add_argument("--sandbox", action="store_true", help="Crea carpeta de prueba con archivos demo")
    parser.add_argument("--yes", "-y", action="store_true", help="Omitir solicitud de confirmación")
    parser.add_argument("--mode", choices=["by_category", "by_date", "by_category_and_date"], default="by_category", help="Estrategia de organización")
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG_PATH), help="Ruta a archivo config.json personalizado")
    return parser.parse_args()


def main():
    args = parse_args()
    config = ConfigManager(Path(args.config))

    # Si no se pasaron argumentos de acción, ejecutar menú interactivo
    if not (args.dry_run or args.run or args.undo or args.sandbox):
        interactive_menu()
        return

    src = Path(args.source) if args.source else Path(config.data.get("source_directory", str(DEFAULT_SANDBOX_DIR)))
    tgt = Path(args.target) if args.target else Path(config.data.get("target_directory", str(DEFAULT_SANDBOX_DIR)))

    if args.sandbox:
        cmd_create_sandbox(DEFAULT_SANDBOX_DIR)
        return

    if args.undo:
        cmd_undo(tgt)
        return

    if args.dry_run:
        cmd_simulate(src, tgt, config, mode=args.mode)
        return

    if args.run:
        cmd_organize(src, tgt, config, mode=args.mode, confirm_prompt=not args.yes)
        return


if __name__ == "__main__":
    main()
