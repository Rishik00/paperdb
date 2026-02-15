# PaperDB
A simple CLI for rendering a Google Sheets paper database into Markdown. I had a simple problem - i have a papershelf and I wanted a local copy of it in my obsidian setup for offline access. So i made this. 

## Status
Done. Not much to add. I built it in a day to solve a single problem. I did use LLMs to format the code nicely and add docstrings, but I did the core searching and wrote the initial solution.

## Build
- Install `uv` (if not already installed) and run `uv build` to produce the wheel/egg artifacts that appear under `dist/`.

## Usage
- Run `paperdb --help` to view available commands, options, and example invocation guidance.
- You can do `paperdb init` and input the google sheets ID (make sure it's public first and copy the last bit of the link).
- You can do `paperdb fetch` after `paperdb init` to get all thw rows nd columns from your google sheets. 
- Once built, invoke the installed entry point for your table via `paperdb` to export Markdown output from your Google Sheets source.
