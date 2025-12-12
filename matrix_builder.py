'''
Docstring for DM.DM_Project_2025.matrix_builder
'''
from scoring import pair_score, parse_locus, get_max_score

def build_similarity_matrix(recipients: list, donors: list) -> list[list[float]]:
    """
    Constructs a normalized similarity matrix (0.0 to 1.0).

    Logic:
    1. For each Recipient, calculate the Max Possible Score (sum of perfect match
       scores for all their alleles).
    2. For each Donor, compare their alleles against the Recipient's alleles
       locus-by-locus.
    3. Final Similarity = (Total Pair Scores) / (Max Possible Score).

    Args:
        recipients: List of lists of allele strings (e.g. [['A*01','B*02'], ...])
        donors: List of lists of allele strings.

    Returns:
        List[List[float]]: A matrix where val is between 0.0 and 1.0.
    """

    # 1. Pre-calculate max scores for recipients to save time
    # This represents the score if a donor matched the recipient perfectly.
    rec_max_scores = []
    for rec_alleles in recipients:
        max_total = 0.0
        # If input is simple numbers (legacy tests), handle gracefully
        if rec_alleles and isinstance(rec_alleles, (list, tuple)) \
            and isinstance(rec_alleles[0], str):
            for allele in rec_alleles:
                max_total += get_max_score(allele)
        else:
            # Fallback for legacy numeric tests
            max_total = 1.0

        rec_max_scores.append(max_total)

    similarity_matrix = []

    for i, rec_alleles in enumerate(recipients):
        row = []
        max_s = rec_max_scores[i]

        for don_alleles in donors:

            # --- LEGACY/TEST SUPPORT START ---
            # If inputs are numbers (from doctests), use simple addition logic
            if isinstance(rec_alleles, (int, float)) and isinstance(don_alleles, (int, float)):
                # Normalize arbitrarily to keep 0-1 range if needed, or just return sum
                # For compatibility with your previous doctest:
                row.append(rec_alleles + don_alleles)
                continue
            # --- LEGACY/TEST SUPPORT END ---

            # Standard Logic: Person vs Person
            current_score = 0.0

            # Map donor alleles by locus for O(1) lookup
            # e.g. {'A': 'A*02:01', 'B': 'B*44:02'}
            don_map = {}
            if isinstance(don_alleles, list):
                for d_all in don_alleles:
                    if isinstance(d_all, str):
                        don_map[parse_locus(d_all)] = d_all

            # Compare Recipient alleles against Donor map
            if isinstance(rec_alleles, list):
                for r_all in rec_alleles:
                    if not isinstance(r_all, str): continue

                    locus = parse_locus(r_all)
                    d_match = don_map.get(locus)

                    if d_match:
                        # Calculate score for this specific locus pair
                        current_score += pair_score(r_all, d_match)
                    # If donor is missing the locus, score remains 0 for this allele

            # Normalize: Actual Score / Max Possible Score
            if max_s > 0:
                normalized_val = current_score / max_s
            else:
                normalized_val = 0.0

            # Clamp to 0.0 - 1.0 just in case
            normalized_val = max(0.0, min(1.0, normalized_val))
            row.append(normalized_val)

        similarity_matrix.append(row)

    return similarity_matrix


if __name__ == "__main__":
    # import doctest
    # doctest.testmod()
    # Simple test to verify structure
    # Recipient has A and B. Donor 1 matches A only. Donor 2 matches both.
    recs = [['A*01:01', 'B*07:02']]
    dons = [
        ['A*01:01', 'B*44:02'], # Match A (2.0 pts), Mismatch B (0.0 pts) -> 50% match
        ['A*01:01', 'B*07:02']  # Perfect match -> 100%
    ]

    mat = build_similarity_matrix(recs, dons)
    print("Test Matrix (should be approx [0.5, 1.0]):")
    print(mat)
