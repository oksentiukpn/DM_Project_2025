#!/usr/bin/env python3
"""Command-line entry for HLA donor-recipient matching.

Usage: python main.py recipients.csv donors.csv --output out.html --format html --min-accept 60 --verbose

Outputs either a CSV matrix (values or empty for rejected pairs) or an HTML
table with colored cells: green for accepted similarity entries, red for rows
with no accepted values.
"""
import argparse
import json
import io
import csv
import sys
from typing import List, Tuple, Optional

from matrix_builder import build_similarity_matrix
from matching import convert_similarity, remove_not_accepted, match


def read_people(path: str) -> Tuple[List[str], List[List[str]]]:
    ids: List[str] = []
    alleles_list: List[List[str]] = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r and any(c.strip() for c in r)]
        if not rows:
            return ids, alleles_list
        header = rows[0]
        start = 0
        if any(h.lower() in ('id', 'recipient', 'donor', 'name') for h in header):
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


def write_matrix_csv(path: Optional[str], rec_ids: List[str], don_ids: List[str], sim: List[List[float]], result: List[int], min_accept: float):
    out = open(path, 'w', newline='', encoding='utf-8') if path else sys.stdout
    writer = csv.writer(out)
    # header: empty corner + donor ids
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


def write_matrix_html(path: Optional[str], rec_ids: List[str], don_ids: List[str], sim: List[List[float]], result: List[int], min_accept: float):
    threshold = min_accept / 100.0
    out = open(path, 'w', encoding='utf-8') if path else sys.stdout
    out.write('<!doctype html>\n<html><head><meta charset="utf-8"><title>HLA Similarity Matrix</title>\n')
    out.write('<style>table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px;text-align:center} .good{background:#c8e6c9} .badrow{background:#ffcdd2}</style>\n')
    out.write('</head><body>\n')
    out.write('<table>\n')
    # header
    out.write('<tr><th></th>')
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


def main(argv=None):
    p = argparse.ArgumentParser(description='HLA donor-recipient matching')
    p.add_argument('recipients', help='CSV file with recipients')
    p.add_argument('donors', help='CSV file with donors')
    p.add_argument('--min-accept', type=float, default=60.0, help='Minimum acceptance threshold in percent (default: 60)')
    p.add_argument('--verbose', action='store_true', help='Verbose output')
    p.add_argument('--output', '-o', help='Output path (defaults to stdout)')
    p.add_argument('--format', choices=['csv', 'html'], default='csv', help='Output format for matrix (csv or html). CSV cannot contain colors; use HTML for colored view')
    args = p.parse_args(argv)

    rec_ids, recs = read_people(args.recipients)
    don_ids, dons = read_people(args.donors)

    if args.verbose:
        print(f"Loaded {len(recs)} recipients and {len(dons)} donors", file=sys.stderr)

    if len(dons) < len(recs):
        print("Error: number of donors must be >= number of recipients.", file=sys.stderr)
        return 2

    similarity = build_similarity_matrix(recs, dons)
    if args.verbose:
        print(f"Built similarity matrix: {len(similarity)}x{len(similarity[0])}", file=sys.stderr)

    # Compute cost/filter/match so each recipient gets at most one donor
    cost = convert_similarity(similarity)
    filtered = remove_not_accepted(cost, min_accept=int(args.min_accept))
    result = match(filtered)

    # Write matrix output (only assigned donor cell per recipient will be filled)
    if args.format == 'csv':
        write_matrix_csv(args.output, rec_ids, don_ids, similarity, result, args.min_accept)
    else:
        write_matrix_html(args.output, rec_ids, don_ids, similarity, result, args.min_accept)

    if args.verbose:
        print(f"Wrote matrix to {args.output or 'stdout'} (format={args.format})", file=sys.stderr)

    # Also produce CSV text for in-site download/viewing
    def matrix_to_csv_string(rec_ids, don_ids, sim, result, min_accept):
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

    csv_text = matrix_to_csv_string(rec_ids, don_ids, similarity, result, args.min_accept)

    # Build compact assignment CSV: recipient,assigned_donor,similarity
    def assignment_csv_string(rec_ids, don_ids, sim, result, min_accept):
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

    assign_csv_text = assignment_csv_string(rec_ids, don_ids, similarity, result, args.min_accept)

    # If HTML was requested and an output path given, also write CSV beside it
    if args.output and args.format == 'html':
        try:
            base = args.output.rsplit('.', 1)[0]
            csv_path = base + '.csv'
            with open(csv_path, 'w', encoding='utf-8', newline='') as fh:
                fh.write(csv_text)
            if args.verbose:
                print(f"Wrote CSV to {csv_path}", file=sys.stderr)
        except Exception:
            pass

    # Emit JSON with result and CSV to stdout for API consumption
    print(json.dumps({"result": result, "csv_matrix": csv_text, "csv_assignment": assign_csv_text}))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
