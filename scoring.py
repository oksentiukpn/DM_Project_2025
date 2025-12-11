'''
Docstring for DM.DM_Project_2025.scoring
'''
from typing import Sequence, Tuple, List


def _parse_locus(allele: str) -> str:
    allele = (allele or "").strip()
    if '*' in allele:
        return allele.split('*', 1)[0]
    if ':' in allele:
        return allele.split(':', 1)[0]
    return allele


def _allele_fields(allele: str) -> List[str]:
    """Return fields after the '*' as a list, e.g. 'A*02:01:01' -> ['02','01','01'].
    Empty strings or malformed alleles return empty list.
    """
    allele = (allele or "").strip()
    if '*' not in allele:
        return []
    rest = allele.split('*', 1)[1]
    return [f for f in rest.split(':') if f != '']


# Default per-locus importance weights (can be tuned)
DEFAULT_LOCI_WEIGHTS = {
    'A': 1.0,
    'B': 1.0,
    'C': 0.8,
    'DRB1': 1.2,
    'DQB1': 0.9,
}


def pair_score(recipient: Sequence[str], donor: Sequence[str], *,
            full_match_points: float = 2.0,
            two_field_points: float = 1.5,
            serotype_points: float = 0.75,
            locus_only_points: float = 1.0,
            locus_weights: dict = None) -> Tuple[float, float, float]:
    """Enhanced pair scoring with allele hierarchy and locus weighting.

    Returns (points_obtained, max_points, normalized_score).

    Rules (per recipient allele):
    - exact (all available fields match) -> `full_match_points`
    - two-field match (first two fields after '*') -> `two_field_points`
    - serotype-style match (first field equal) -> `serotype_points`
    - same locus but no field match -> `locus_only_points`

    Each per-allele score is multiplied by the locus weight. The max points
    is the sum of `full_match_points * locus_weight` for each recipient
    allele (this reflects maximum achievable per-recipient allele).
    """
    locus_weights = locus_weights or DEFAULT_LOCI_WEIGHTS

    rec = [str(a).strip() for a in recipient]
    don = [str(a).strip() for a in donor]

    used = [False] * len(don)
    total_points = 0.0
    max_points = 0.0

    for r in rec:
        if not r:
            continue
        locus = _parse_locus(r)
        weight = float(locus_weights.get(locus, 0.8))
        max_points += full_match_points * weight

        best_j = -1
        best_score = 0.0

        r_fields = _allele_fields(r)
        for j, d in enumerate(don):
            if used[j] or not d:
                continue
            d_locus = _parse_locus(d)
            if d_locus != locus:
                continue

            # compute match level
            d_fields = _allele_fields(d)
            # exact (all available fields equal)
            if r == d:
                s = full_match_points * weight
            else:
                # two-field match: first two fields exist and equal
                if len(r_fields) >= 2 and len(d_fields) >= 2 and r_fields[0:2] == d_fields[0:2]:
                    s = two_field_points * weight
                # serotype-style: first field equal
                elif len(r_fields) >= 1 and len(d_fields) >= 1 and r_fields[0] == d_fields[0]:
                    s = serotype_points * weight
                else:
                    # same locus but no field match
                    s = locus_only_points * weight

            if s > best_score:
                best_score = s
                best_j = j

        if best_j != -1 and best_score > 0:
            used[best_j] = True
            total_points += best_score

    normalized = (total_points / max_points) if max_points > 0 else 0.0
    return (total_points, max_points, normalized)


__all__ = ["pair_score"]
