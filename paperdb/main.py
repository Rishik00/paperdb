#!/usr/bin/env python3
"""
paperdb.py

One-time setup:
  paperdb init --sheet-id <ID> --out "<path>/PaperDB.md"

Then always:
  paperdb fetch

Deps:
  pip install pandas tabulate rich
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


# -----------------------------
# Config storage
# -----------------------------

def config_path() -> Path:
    # ~/.paperdb/config.json
    return Path.home() / ".paperdb" / "config.json"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        raise FileNotFoundError(
            "No config found. Run:\n"
            "  paperdb init --sheet-id <ID> --out <path/to/PaperDB.md>"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(cfg: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


# -----------------------------
# Sheets -> DataFrame
# -----------------------------

def make_csv_url(sheet_id: str, gid: str | None = None) -> str:
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid is not None:
        url += f"&gid={gid}"
    return url


def fetch_sheet_df(sheet_id: str, gid: str | None = None) -> pd.DataFrame:
    url = make_csv_url(sheet_id, gid=gid)
    df = pd.read_csv(url)

    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    df = df.fillna("No")

    # strip whitespace for string columns only
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    return df


def df_to_markdown(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)

def write_markdown(md: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")


def preview_df_rich(df: pd.DataFrame, max_rows: int = 10) -> None:
    preview = df.head(max_rows)

    table = Table(title=f"PaperDB Preview (showing {len(preview)}/{len(df)} rows)")
    for col in preview.columns:
        table.add_column(str(col), overflow="fold")

    for _, row in preview.iterrows():
        table.add_row(*[str(x) for x in row.values.tolist()])

    console.print(table)


# -----------------------------
# Commands
# -----------------------------

def cmd_init(sheet_id: str, out: str, gid: str | None) -> None:
    out_path = Path(out).expanduser().resolve()

    cfg = {
        "sheet_id": sheet_id,
        "out": str(out_path),
        "gid": gid
    }
    save_config(cfg)

    console.print(Panel.fit("paperdb init", style="bold cyan"))
    console.print("[green]Saved config:[/green]")
    console.print(json.dumps(cfg, indent=2))


def cmd_fetch(preview_rows: int) -> None:
    cfg = load_config()

    sheet_id = cfg["sheet_id"]
    out_path = Path(cfg["out"]).expanduser().resolve()
    gid = cfg.get("gid", None)

    console.print(Panel.fit("paperdb fetch", style="bold cyan"))
    console.print(f"[bold]Sheet ID:[/bold] {sheet_id}")
    console.print(f"[bold]Output:[/bold] {out_path}")
    if gid is not None:
        console.print(f"[bold]GID:[/bold] {gid}")

    console.print("\n[bold]Fetching sheet...[/bold]")
    df = fetch_sheet_df(sheet_id=sheet_id, gid=gid)

    console.print("[green]Fetched successfully.[/green]")
    console.print(f"[bold]Shape:[/bold] {df.shape[0]} rows × {df.shape[1]} cols\n")

    preview_df_rich(df, max_rows=preview_rows)

    console.print("\n[bold]Rendering markdown...[/bold]")
    md = df_to_markdown(df)

    console.print("[bold]Writing file...[/bold]")
    write_markdown(md, out_path)

    console.print(f"\n[green]Done.[/green] Updated: [bold]{out_path}[/bold]")


def cmd_show_config() -> None:
    cfg = load_config()
    console.print(Panel.fit("paperdb config", style="bold cyan"))
    console.print(json.dumps(cfg, indent=2))


def cmd_reset() -> None:
    path = config_path()
    if path.exists():
        path.unlink()
        console.print("[green]Deleted config.[/green]")
    else:
        console.print("[yellow]No config found.[/yellow]")


# -----------------------------
# CLI
# -----------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="paperdb", description="Google Sheets -> Markdown Paper DB")

    sub = p.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Save sheet id + output path (one-time)")
    init.add_argument("--sheet-id", required=True, help="Google Sheet ID")
    init.add_argument("--out", required=True, help="Output markdown file path")
    init.add_argument("--gid", default=None, help="Worksheet gid (optional)")

    fetch = sub.add_parser("fetch", help="Fetch and update markdown file (uses saved config)")
    fetch.add_argument("--preview-rows", type=int, default=10, help="Rows to preview in terminal")

    show = sub.add_parser("config", help="Show current config")

    reset = sub.add_parser("reset", help="Delete saved config")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "init":
        cmd_init(sheet_id=args.sheet_id, out=args.out, gid=args.gid)
    elif args.cmd == "fetch":
        cmd_fetch(preview_rows=args.preview_rows)
    elif args.cmd == "config":
        cmd_show_config()
    elif args.cmd == "reset":
        cmd_reset()
    else:
        raise SystemExit(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
