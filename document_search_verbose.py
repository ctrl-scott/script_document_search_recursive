#!/usr/bin/env python3
"""Lightweight, read-only recursive search of PDF, DOCX and text files."""
import argparse
import time
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TEXT_EXTS = {'.txt', '.md', '.csv', '.tsv', '.json', '.xml', '.html', '.htm', '.log', '.py'}
SUPPORTED = TEXT_EXTS | {'.pdf', '.docx'}
W_TEXT = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'
W_PARA = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'


def docx_lines(path):
    with zipfile.ZipFile(path) as archive:
        with archive.open('word/document.xml') as source:
            for _, elem in ET.iterparse(source, events=('end',)):
                if elem.tag == W_PARA:
                    yield ''.join(t.text or '' for t in elem.iter(W_TEXT))
                    elem.clear()


def text_lines(path):
    with path.open('r', encoding='utf-8', errors='replace') as stream:
        yield from stream


def pdf_lines(path):
    # Poppler emits extracted UTF-8 text to stdout; no temporary document copy.
    proc = subprocess.Popen(
        ['pdftotext', '-enc', 'UTF-8', str(path), '-'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, encoding='utf-8', errors='replace',
    )
    try:
        yield from proc.stdout
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=5)
    if proc.returncode != 0 and proc.returncode != -15:
        raise RuntimeError(f'pdftotext failed with exit code {proc.returncode}')


def files_under(root):
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = sorted(d for d in subdirs if not (Path(directory) / d).is_symlink())
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.suffix.lower() in SUPPORTED and not path.is_symlink():
                yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('keyword', help='Case-insensitive literal text to search for')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase diagnostic detail: -v file progress, -vv skips/matches, -vvv per-line progress')
    parser.add_argument('--max-mb', type=float, default=50, help='Maximum file size in MiB (default: 50)')
    parser.add_argument('--max-results', type=int, default=100, help='Stop after this many matching lines (default: 100)')
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error('directory must exist')
    if not args.keyword.strip() or args.max_mb <= 0 or args.max_results <= 0:
        parser.error('keyword must not be blank; numeric limits must be positive')
    if shutil.which('pdftotext') is None:
        print('NOTE: pdftotext is not installed; PDFs will be skipped.', file=sys.stderr)
    started = time.monotonic()
    checked = matched = skipped = errors = inspected_lines = 0
    discovered = 0

    def log(level, message):
        if args.verbose >= level:
            print(f'[INFO {time.monotonic()-started:8.2f}s] {message}', file=sys.stderr, flush=True)

    log(1, f'Searching {args.directory.resolve()} | phrase={args.keyword!r} | max file={args.max_mb:g} MiB | max matches={args.max_results}')
    needle = args.keyword.casefold()
    for path in files_under(args.directory):
        discovered += 1
        try:
            size = path.stat().st_size
            if size > args.max_mb * 1024 * 1024:
                skipped += 1
                log(2, f'SKIP (size {size / 1048576:.2f} MiB): {path}')
                continue
            if path.suffix.lower() == '.pdf':
                if shutil.which('pdftotext') is None:
                    skipped += 1
                    log(2, f'SKIP (pdftotext missing): {path}')
                    continue
                lines = pdf_lines(path)
            elif path.suffix.lower() == '.docx':
                lines = docx_lines(path)
            else:
                lines = text_lines(path)
            checked += 1
            log(1, f'CHECK [{checked}] {path} ({size / 1048576:.2f} MiB)')
            file_hits = 0
            for number, line in enumerate(lines, start=1):
                inspected_lines += 1
                if args.verbose >= 3 and number % 1000 == 0:
                    log(3, f'  READ {path}: {number:,} extracted lines')
                if needle in line.casefold():
                    file_hits += 1
                    log(2, f'  MATCH at extracted line {number}: {path}')
                    print(f'{path}:{number}: {line.strip()[:240]}')
                    matched += 1
                    if matched >= args.max_results:
                        lines.close()
                        print(f'Stopped at result limit ({matched}).', file=sys.stderr)
                        print(f'Files checked: {checked}; skipped: {skipped}; errors: {errors}', file=sys.stderr)
                        log(1, f'Finished (limit reached): {discovered} discovered, {inspected_lines:,} lines examined, {time.monotonic()-started:.2f}s elapsed')
                        return 0
            log(2, f'DONE {path}: {file_hits} matching lines')
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, RuntimeError, subprocess.TimeoutExpired) as exc:
            errors += 1
            print(f'WARNING: {path}: {exc}', file=sys.stderr)
            log(1, f'ERROR while processing {path}')
    print(f'Files checked: {checked}; matching lines: {matched}; skipped: {skipped}; errors: {errors}', file=sys.stderr)
    log(1, f'Finished: {discovered} discovered, {inspected_lines:,} lines examined, {time.monotonic()-started:.2f}s elapsed')
    return 0

if __name__ == '__main__':
    sys.exit(main())
