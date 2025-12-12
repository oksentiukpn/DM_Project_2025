#!/usr/bin/env python3
"""Command-line entry for HLA donor-recipient matching.

Usage:
python main.py recipients.csv donors.csv --output out.html --format html --min-accept 60 --verbose
"""
import argparse
import json
import io
import csv
import sys
import time
import os
from typing import List, Tuple, Optional, Any
from matrix_builder import build_similarity_matrix
from matching import convert_similarity, remove_not_accepted, match

# ANSI Colors constants
HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Enable colors on Windows 10+
if os.name == 'nt':
    os.system('color')


def print_banner(verbose: bool):
    '''
    Docstring for print_banner

    :param verbose: Description
    :type verbose: bool
    '''
    if not verbose:
        return None
    print(f"\n{BOLD}{BLUE}╔{'═'*58}╗{ENDC}")
    print(f"{BOLD}{BLUE}║{HEADER}   HLA DONOR-RECIPIENT MATCHING SYSTEM                    \
{BLUE}║{ENDC}")
    print(f"{BOLD}{BLUE}╚{'═'*58}╝{ENDC}\n")


def log_info(msg: str, verbose: bool):
    '''
    Docstring for log_info

    :param msg: Description
    :type msg: str
    :param verbose: Description
    :type verbose: bool
    '''
    if verbose:
        print(f"{BLUE} ℹ {ENDC} {msg}")


def log_success(msg: str, verbose: bool):
    '''
    Docstring for log_success

    :param msg: Description
    :type msg: str
    :param verbose: Description
    :type verbose: bool
    '''
    if verbose:
        print(f"{GREEN} ✔ {ENDC} {msg}")


def log_warn(msg: str):
    '''
    Docstring for log_warn

    :param msg: Description
    :type msg: str
    '''
    # Always print warnings to stderr
    print(f"{WARNING} ⚠ {msg}{ENDC}", file=sys.stderr)


def log_error(msg: str):
    '''
    Docstring for log_error

    :param msg: Description
    :type msg: str
    '''
    # Always print errors to stderr
    print(f"\n{FAIL} ✖ FATAL ERROR: {msg}{ENDC}\n", file=sys.stderr)


def print_section(title: str, verbose: bool):
    '''
    Docstring for print_section

    :param title: Description
    :type title: str
    :param verbose: Description
    :type verbose: bool
    '''
    if verbose:
        print(f"\n{BOLD}{CYAN}── {title.upper()} {'─'*(60-len(title)-4)}{ENDC}")


def print_table(headers: List[str], rows: List[List[Any]], verbose: bool, indent=2):
    '''
    Docstring for print_table

    :param headers: Description
    :type headers: List[str]
    :param rows: Description
    :type rows: List[List[Any]]
    :param verbose: Description
    :type verbose: bool
    :param indent: Description
    '''
    if not verbose or not rows:
        return None

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Add padding
    col_widths = [w + 2 for w in col_widths]

    # Format string
    row_fmt = "  " * indent + "".join([f"{{:<{w}}}" for w in col_widths])

    # Draw
    print(f"{DIM}" + row_fmt.format(*headers) + f"{ENDC}")
    print("  " * indent + "".join(["-" * (w-1) + " " for w in col_widths]))

    for row in rows[:10]: # Limit preview to 10 rows
        clean_row = [str(c) for c in row]
        # Ensure row length matches headers to avoid format errors
        if len(clean_row) == len(headers):
            print(row_fmt.format(*clean_row))

    if len(rows) > 10:
        print("  " * indent + f"{DIM}... and {len(rows)-10} more rows ...{ENDC}")
    print()


def run_with_timer(description: str, func, verbose: bool, *args, **kwargs):
    """Executes a function and tracks time if verbose is True."""
    if verbose:
        sys.stdout.write(f"{BLUE} ⧗ {ENDC} {description}... ")
        sys.stdout.flush()

    t0 = time.time()
    try:
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        if verbose:
            print(f"{GREEN}DONE{ENDC} ({elapsed:.3f}s)")
        return result
    except Exception as e:
        elapsed = time.time() - t0
        if verbose:
            print(f"{FAIL}FAILED{ENDC} ({elapsed:.3f}s)")
        raise e

# ==========================================
#            CORE LOGIC
# ==========================================

def read_people(path: str) -> Tuple[List[str], List[List[str]]]:
    '''Reads a CSV file with people (recipients or donors).'''
    ids: List[str] = []
    alleles_list: List[List[str]] = []

    if not os.path.exists(path):
        return ids, alleles_list

    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r and any(c.strip() for c in r)]
        if not rows:
            return ids, alleles_list
        header = rows[0]
        start = 0
        if any(h.lower() in ('recipient','donors') for h in header):
            start = 1

        for row in rows[start:]:
            if not row:
                continue
            rid = row[0].strip()
            if len(row) == 1:
                alleles = []
            elif len(row) == 2 and (';' in row[1] or ',' not in row[1]):
                alleles = [a.strip() for a in row[1].replace(',', ';').split(';') if a.strip()]
            else:
                alleles = [c.strip() for c in row[1:] if c.strip()]

            ids.append(rid)
            alleles_list.append(alleles)
    return ids, alleles_list


def write_matrix_csv(path: Optional[str], rec_ids: List[str], don_ids: List[str], \
                   sim: List[List[float]], result: List[int], min_accept: float):
    '''
    Docstring for write_matrix_csv

    :param path: Description
    :type path: Optional[str]
    :param rec_ids: Description
    :type rec_ids: List[str]
    :param don_ids: Description
    :type don_ids: List[str]
    :param sim: Description
    :type sim: List[List[float]]
    :param result: Description
    :type result: List[int]
    :param min_accept: Description
    :type min_accept: float
    '''
    out = open(path, 'w', newline='', encoding='utf-8') if path else sys.stdout
    writer = csv.writer(out)
    writer.writerow([''] + don_ids)
    threshold = min_accept / 100.0
    for i, rid in enumerate(rec_ids):
        row = [''] * len(don_ids)
        assigned = result[i] if i < len(result) else -1
        if assigned != -1 and 0 <= assigned < len(don_ids):
            val = sim[i][assigned]
            if val is not None and val >= threshold:
                row[assigned] = f"{val:.6f}"
        writer.writerow([rid] + row)
    if path:
        out.close()


def write_matrix_html(path: Optional[str], rec_ids: List[str], don_ids: List[str], \
                    sim: List[List[float]], result: List[int], min_accept: float):
    '''
    Docstring for write_matrix_html

    :param path: Description
    :type path: Optional[str]
    :param rec_ids: Description
    :type rec_ids: List[str]
    :param don_ids: Description
    :type don_ids: List[str]
    :param sim: Description
    :type sim: List[List[float]]
    :param result: Description
    :type result: List[int]
    :param min_accept: Description
    :type min_accept: float
    '''
    threshold = min_accept / 100.0
    out = open(path, 'w', encoding='utf-8') if path else sys.stdout
    out.write('<!doctype html>\n<html><head><meta charset="utf-8">')
    out.write('<title>HLA Similarity Matrix</title>\n')
    out.write('<style>body{font-family:sans-serif; padding:20px;} \
table{border-collapse:collapse; width:100%;} ')
    out.write('td,th{border:1px solid #ddd;padding:8px;text-align:center} ')
    out.write('th{background-color:#f2f2f2;} tr:hover{background-color:#f5f5f5;} ')
    out.write('.good{background:#c8e6c9; color:#2e7d32; font-weight:bold;} ')
    out.write('.badrow{background:#ffebee; color:#c62828;}</style>\n')
    out.write('</head><body>\n')
    out.write('<h2>HLA Similarity Matrix</h2>')
    out.write('<table>\n')

    # header
    out.write('<tr><th>Recipient / Donor</th>')
    for d in don_ids:
        out.write(f'<th>{d}</th>')
    out.write('</tr>\n')

    for i, r in enumerate(rec_ids):
        assigned = result[i] if i < len(result) else -1
        accepted_any = False
        if assigned != -1 and 0 <= assigned < len(don_ids):
            v = sim[i][assigned]
            if v is not None and v >= threshold:
                accepted_any = True

        row_class = '' if accepted_any else ' class="badrow"'
        out.write(f'<tr{row_class}><th>{r}</th>')
        for j in range(len(don_ids)):
            if assigned == j and accepted_any:
                out.write(f'<td class="good">{sim[i][j]:.4f}</td>')
            else:
                out.write('<td></td>')
        out.write('</tr>\n')

    out.write('</table>\n</body></html>')
    if path:
        out.close()


def generate_csv_string(rec_ids, don_ids, sim, result, min_accept):
    '''
    Docstring for generate_csv_string

    :param rec_ids: Description
    :param don_ids: Description
    :param sim: Description
    :param result: Description
    :param min_accept: Description
    '''
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([''] + don_ids)
    threshold = min_accept / 100.0
    for i, rid in enumerate(rec_ids):
        row = [''] * len(don_ids)
        assigned = result[i] if i < len(result) else -1
        if assigned != -1 and 0 <= assigned < len(don_ids):
            val = sim[i][assigned]
            if val is not None and val >= threshold:
                row[assigned] = f"{val:.6f}"
        writer.writerow([rid] + row)
    return buf.getvalue()


def generate_assignment_csv_string(rec_ids, don_ids, sim, result, min_accept):
    '''
    Docstring for generate_assignment_csv_string

    :param rec_ids: Description
    :param don_ids: Description
    :param sim: Description
    :param result: Description
    :param min_accept: Description
    :return: Description
    :rtype: str
    '''
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['recipient', 'assigned_donor', 'similarity'])
    threshold = min_accept / 100.0
    for i, rid in enumerate(rec_ids):
        assigned = result[i] if i < len(result) else -1
        if assigned != -1 and 0 <= assigned < len(don_ids):
            val = sim[i][assigned]
            if val is not None and val >= threshold:
                writer.writerow([rid, don_ids[assigned], f"{val:.6f}"])
            else:
                writer.writerow([rid, '', ''])
        else:
            writer.writerow([rid, '', ''])
    return buf.getvalue()


def main(argv=None):
    '''
    Docstring for main

    :param argv: Description
    '''
    start_total_time = time.perf_counter()

    p = argparse.ArgumentParser(description='HLA donor-recipient matching')
    p.add_argument('recipients', help='CSV file with recipients')
    p.add_argument('donors', help='CSV file with donors')
    p.add_argument('--min-accept', type=float, default=60.0, \
                   help='Minimum acceptance threshold in percent (default: 60)')
    p.add_argument('--verbose', action='store_true', help='Verbose output with UI')
    p.add_argument('--output', '-o', help='Output path (defaults to stdout)')
    p.add_argument('--format', choices=['csv', 'html'], default='csv', \
                   help='Output format for matrix (csv or html)')
    args = p.parse_args(argv)

    verbose = args.verbose

    # Initialize UI
    print_banner(verbose)

    # 1. Loading Data
    print_section("Initialization", verbose)

    if not os.path.exists(args.recipients):
        log_error(f"Recipient file not found: {args.recipients}")
        return 1
    if not os.path.exists(args.donors):
        log_error(f"Donor file not found: {args.donors}")
        return 1

    # Read Data with Timer Wrappers
    rec_ids, recs = run_with_timer(f"Reading {os.path.basename(args.recipients)}",
                                  read_people, verbose, args.recipients)

    don_ids, dons = run_with_timer(f"Reading {os.path.basename(args.donors)}",
                                  read_people, verbose, args.donors)

    log_success(f"Loaded {BOLD}{len(recs)}{ENDC} recipients and {BOLD}{len(dons)}\
{ENDC} donors", verbose)

    # Preview Data
    if verbose and len(recs) > 0:
        log_info("Recipient Data Preview:", verbose)
        preview_data = [[rid, len(recs[i]), ", ".join(recs[i][:3]) + \
                         ("..." if len(recs[i])>3 else "")]
                        for i, rid in enumerate(rec_ids)]
        print_table(["ID", "Allele Count", "Alleles (Sample)"], preview_data, verbose)

    # Logic Checks
    if len(dons) < len(recs):
        log_error(f"Configuration Invalid: Number of donors \
({len(dons)}) must be >= number of recipients ({len(recs)}).")
        return 2

    # 2. Computation
    print_section("Processing", verbose)

    similarity = run_with_timer("Building Similarity Matrix",
                               build_similarity_matrix, verbose, recs, dons)

    # Wrap the matching process in a simple function to time the whole block
    def compute_match_wrapper(sim_matrix, minimum_acceptance):
        c = convert_similarity(sim_matrix)
        f = remove_not_accepted(c, min_accept=int(minimum_acceptance))
        return match(f)

    result = run_with_timer("Computing Optimal Matching",
                           compute_match_wrapper, verbose, similarity, args.min_accept)

    # 3. Results & Stats
    print_section("Results", verbose)

    # Calculate statistics
    threshold = args.min_accept / 100.0
    matches_found = 0
    total_score = 0.0

    summary_rows = []

    for i, rid in enumerate(rec_ids):
        assigned = result[i] if i < len(result) else -1

        status = "Unmatched"
        score_str = "0.00%"
        donor_name = "-"

        if assigned != -1 and 0 <= assigned < len(don_ids):
            val = similarity[i][assigned]
            if val is not None and val >= threshold:
                matches_found += 1
                total_score += val
                status = "Matched"
                score_str = f"{val*100:.1f}%"
                donor_name = don_ids[assigned]
            else:
                status = "Below Threshold"

        summary_rows.append([rid, donor_name, status, score_str])

    # Print Stats
    avg_score = (total_score / matches_found * 100) if matches_found > 0 else 0
    match_rate = (matches_found / len(rec_ids)) * 100

    # We print summary statistics regardless of verbose, but style them nicely
    print(f"  {BOLD}Match Rate:{ENDC} {match_rate:.1f}% ({matches_found}/{len(rec_ids)})")
    print(f"  {BOLD}Avg Score :{ENDC} {avg_score:.1f}% (of matched pairs)")
    print("")

    if verbose:
        log_info("Assignment Preview:", verbose)
        print_table(["Recipient", "Assigned Donor", "Status", "Similarity"], summary_rows, verbose)

    # 4. Output Generation
    print_section("Output Generation", verbose)

    # Write matrix output
    if args.format == 'csv':
        write_matrix_csv(args.output, rec_ids, don_ids, similarity, result, args.min_accept)
    else:
        write_matrix_html(args.output, rec_ids, don_ids, similarity, result, args.min_accept)

    log_success(f"Matrix saved to: {BOLD}{args.output or 'stdout'}{ENDC}", verbose)

    # Generate CSV strings
    csv_text = generate_csv_string(rec_ids, don_ids, similarity, result, args.min_accept)
    assign_csv_text = generate_assignment_csv_string(rec_ids, don_ids, similarity, \
                                                    result, args.min_accept)

    # If HTML was requested and output path given, write CSV beside it
    if args.output and args.format == 'html':
        try:
            base = args.output.rsplit('.', 1)[0]
            csv_path = base + '.csv'
            with open(csv_path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(csv_text)
            log_success(f"Raw CSV saved to: {BOLD}{csv_path}{ENDC}", verbose)
        except FileNotFoundError as e:
            log_warn(f"Could not save side-car CSV: {e}")

    # Final JSON output
    json_output = json.dumps({"result": result, "csv_matrix": csv_text, \
                              "csv_assignment": assign_csv_text})

    # If not outputting to file, and not verbose, print JSON to stdout (standard pipe behavior)
    if not args.output and not verbose:
        print(json_output)
    elif args.output:
        # If output is file, we can print JSON safely
        print(json_output)

    if verbose:
        elapsed_total = time.perf_counter() - start_total_time
        print(f"\n{DIM}Total execution time: {elapsed_total:.4f}s{ENDC}\n")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
