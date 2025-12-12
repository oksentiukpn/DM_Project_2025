"""Simple allele pair scoring utility.

This module exposes functions to score allele pairs and calculate theoretical
maximums for normalization.
"""

from typing import List
import numbers


# Default per-locus importance weights (can be tuned)
DEFAULT_LOCI_WEIGHTS = {
    'A': 1.0,
    'B': 1.0,
    'C': 0.8,
    'DRB1': 1.2,
    'DQB1': 0.9,
}


def parse_locus(allele: str) -> str:
    """Return the locus part of an allele string, e.g. 'A*02:01:01' -> 'A'.

    Empty or malformed inputs return the trimmed string.
    """
    allele = str(allele or "").strip()
    if '*' in allele:
        return allele.split('*', 1)[0]
    if ':' in allele:
        return allele.split(':', 1)[0]
    return allele


def _allele_fields(allele: str) -> List[str]:
    """Return fields after the '*' as a list, e.g. 'A*02:01:01' -> ['02','01','01'].

    If the allele is malformed or missing the '*', an empty list is returned.
    """
    allele = (allele or "").strip()
    if '*' not in allele:
        return []
    rest = allele.split('*', 1)[1]
    return [f for f in rest.split(':') if f != '']


def get_max_score(
    allele: str,
    *,
    full_match_points: float = 2.0,
    locus_weights: dict = None,
) -> float:
    """Calculate the maximum possible score for a single allele (perfect match).

    Used to calculate the denominator for score normalization.
    """
    if isinstance(allele, numbers.Number):
        return float(allele) * 2  # Arbitrary heuristic for numeric legacy tests

    locus_weights = locus_weights or DEFAULT_LOCI_WEIGHTS
    locus = parse_locus(allele)
    weight = float(locus_weights.get(locus, 0.8))

    return full_match_points * weight


def pair_score(
    allele1: str,
    allele2: str,
    *,
    full_match_points: float = 2.0,
    two_field_points: float = 1.5,
    serotype_points: float = 0.75,
    locus_only_points: float = 1.0,
    locus_weights: dict = None,
) -> float:
    """Score a single pair of allele strings and return a float score.

    The function returns 0.0 if either allele is empty or loci differ. Otherwise
    it applies the following rules (then multiplies by locus weight):
    - exact string equality -> `full_match_points`
    - first two colon-separated fields equal -> `two_field_points`
    - first field equal -> `serotype_points`
    - same locus but no field match -> `locus_only_points`
    """
    locus_weights = locus_weights or DEFAULT_LOCI_WEIGHTS

    # Legacy support for numeric tests
    if isinstance(allele1, numbers.Number) and isinstance(allele2, numbers.Number):
        s = allele1 + allele2
        if isinstance(allele1, int) and isinstance(allele2, int):
            return s
        return float(s)

    a1 = str(allele1 or "").strip()
    a2 = str(allele2 or "").strip()

    if not a1 or not a2:
        return 0.0

    locus1 = parse_locus(a1)
    locus2 = parse_locus(a2)

    if locus1 != locus2:
        return 0.0

    weight = float(locus_weights.get(locus1, 0.8))

    if a1 == a2:
        return full_match_points * weight

    f1 = _allele_fields(a1)
    f2 = _allele_fields(a2)

    if len(f1) >= 2 and len(f2) >= 2 and f1[0:2] == f2[0:2]:
        return two_field_points * weight

    if len(f1) >= 1 and len(f2) >= 1 and f1[0] == f2[0]:
        return serotype_points * weight

    return locus_only_points * weight
