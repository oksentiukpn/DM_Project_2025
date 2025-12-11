from matrix_builder import build_similarity_matrix
from matching import convert_similarity, remove_not_accepted, match


def test_small_matching_pipeline():
    # Controlled small example
    recipients = [
        ["A*02:01", "B*07:02"],
        ["A*01:01", "B*08:01"],
        ["C*03:04", "DRB1*15:01"],
    ]
    donors = [
        ["A*02:01", "B*35:01"],
        ["A*01:01", "B*08:01"],
        ["C*03:04", "DRB1*15:01"],
        ["A*03:01", "B*07:02"],
    ]

    sim = build_similarity_matrix(recipients, donors)
    cost = convert_similarity(sim)
    filtered = remove_not_accepted(cost, min_accept=0)  # allow all for test
    result = match(filtered)

    # Should return assignment for each recipient (length == recipients)
    assert len(result) == len(recipients)
    # Donors used at most once
    used = [d for d in result if d != -1]
    assert len(used) == len(set(used))
