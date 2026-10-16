# Document Search Utility

A lightweight, recursive document-search utility written in Python 3 for searching text within PDFs, Microsoft Word documents, and other text-based files.

Designed for macOS, Debian, Ubuntu, and other Unix-like operating systems, with an emphasis on **efficient system resource usage, minimal dependencies, and detailed diagnostic output**.

## Features

- Recursive directory searching
- PDF text extraction using Poppler (`pdftotext`)
- Microsoft Word `.docx` document searching
- Support for common text-based file formats
- Case-insensitive keyword and phrase matching
- Configurable file-size limits
- Maximum search-result limits
- Three verbosity levels for monitoring operations
- Separate standard output and diagnostic logging
- Read-only processing of source documents
- No database or persistent search index required

## Supported File Formats

| Extension | Description | Extraction method |
|---|---|---|
| `.pdf` | Portable Document Format | Poppler `pdftotext` |
| `.docx` | Microsoft Word | Python standard library |
| `.txt` | Plain text | Text decoding |
| `.md` | Markdown | Text decoding |
| `.csv` | Comma-separated values | Text decoding |
| `.tsv` | Tab-separated values | Text decoding |
| `.json` | JSON | Text decoding |
| `.xml` | XML | Text decoding |
| `.html`, `.htm` | HTML source | Text decoding |
| `.log` | Log files | Text decoding |
| `.py` | Python source code | Text decoding |

**Note:** Scanned PDFs containing images instead of selectable text require OCR, which is not included in this version.

## Requirements

- Python 3
- Poppler utilities for PDF searching
- macOS or Linux

The initial version does not require a database server or third-party Python packages.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/document-search.git
cd document-search
```

Replace `YOUR_USERNAME` with your GitHub username after publishing the repository.

### 2. Install Poppler

**macOS (Homebrew):**

```bash
brew install poppler
```

**Debian / Ubuntu:**

```bash
sudo apt update
sudo apt install poppler-utils
```

Verify that the PDF extractor is available:

```bash
pdftotext -v
```

### 3. Verify Python

```bash
python3 --version
```

## Usage

### Basic recursive search

Search a directory and all its subdirectories for a phrase:

```bash
python3 document_search.py \
  ~/Documents \
  "memory allocation"
```

The program examines supported files and prints matching lines with document paths.

### Enable verbosity

Three levels of diagnostic output are supported.

| Level | Argument | Description |
|---|---|---|
| Default | None | Search results and summary |
| Information | `-v` | Files processed and elapsed time |
| Detailed | `-vv` | Skipped files, match locations, per-file totals |
| Debug | `-vvv` | Additional progress reports during text extraction |

Example:

```bash
python3 document_search.py \
  ~/Documents \
  "page replacement" \
  -vv
```

### Limit file sizes

Skip files larger than 50 MiB:

```bash
python3 document_search.py \
  ~/Documents \
  "operating systems" \
  --max-mb 50
```

This helps avoid unnecessarily processing very large documents.

### Limit search results

Stop after 100 matching lines:

```bash
python3 document_search.py \
  ~/Documents \
  "algorithm" \
  --max-results 100
```

### Combine options

```bash
python3 document_search.py \
  ~/Documents \
  "virtual memory" \
  --max-mb 50 \
  --max-results 100 \
  -vvv
```

## Example Output

Illustrative output:

```text
documents/chapter1.pdf:12: Virtual memory allows...
documents/chapter3.docx:8: Virtual memory management...
documents/notes.txt:25: Virtual memory uses...

Files checked: 3
Matching lines: 3
Skipped: 0
Errors: 0
```

Line numbers refer to extracted text and may not correspond exactly to PDF page numbers or document layout.

## Diagnostic Logging

Diagnostic messages are written to standard error (`stderr`), while search results are written to standard output (`stdout`).

This allows results and logs to be saved independently.

```bash
python3 document_search.py \
  ~/Documents \
  "memory allocation" \
  -vvv \
  > search_results.txt \
  2> search_debug.log
```

The resulting files are:

- `search_results.txt`: Search matches and summary output.
- `search_debug.log`: Diagnostic information and progress reporting.

To capture both output streams in one file:

```bash
python3 document_search.py \
  ~/Documents \
  "memory allocation" \
  -vvv \
  > complete_search.log 2>&1
```

## Resource Management

The utility is designed to minimize unnecessary resource consumption.

### Memory

Documents are processed individually rather than loaded into a single collection.

Text extraction is performed incrementally where supported.

### Disk Storage

No permanent search database or index is required.

PDF extraction uses Poppler, avoiding the need to save permanent converted copies of each PDF.

### CPU

Searches run on demand.

OCR is intentionally excluded from the initial implementation because it can be computationally expensive.

### File Size Limits

Use `--max-mb` to exclude exceptionally large files.

File-size limits are safeguards, not strict process memory limits. PDF decompression and text extraction may consume more memory than the compressed file occupies on disk.

### Verbosity

For large document collections, use `-v` for routine monitoring and `-vv` or `-vvv` when troubleshooting.

## Current Limitations

- Scanned PDFs require a separate OCR solution.
- Legacy `.doc` documents are not supported.
- Searches do not use a persistent index.
- Repeated searches require documents to be processed again.
- Search results are based on extracted text rather than visual page layout.
- Very large or malformed documents may require additional resource controls.
<!--
## Planned Enhancements

Potential future improvements include:

- SQLite FTS5 full-text indexing
- Incremental indexing based on file modification times
- SHA-256 checksum-based change detection
- Optional OCR with Tesseract
- PDF page-number reporting
- Regular expression searching
- JSON and CSV result export
- CPU and memory usage statistics
- Configurable directory exclusions
- More detailed performance reporting
-->
## References

Apache Software Foundation. (n.d.). *Apache Tika*. https://tika.apache.org/

Poppler Developers. (n.d.). *Poppler*. https://poppler.freedesktop.org/

Python Software Foundation. (n.d.). *Python 3 documentation*. https://docs.python.org/3/

SQLite Consortium. (n.d.). *SQLite FTS5 extension*. https://www.sqlite.org/fts5.html

ChatGPT Link *ChatGPT* https://chatgpt.com/share/6acd4552-4bd4-83e9-8c35-df57787f8a1f
## License

No license has been assigned yet. Add a `LICENSE` file to specify the terms under which others may use, modify, and distribute this project.
