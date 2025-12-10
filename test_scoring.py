import random

from tests.hlainput import get_hla_dict
from scoring.scoring import pair_score
from matrix_builder import build_similarity_matrix
from matching import convert_similarity, remove_not_accepted, match


def test_random_matching_pipeline():

    allele_dict = get_hla_dict("data/Allelelist.txt")
    alleles = list(allele_dict.values())


    random.seed(42)

    recipients = [random.sample(alleles, 2) for _ in range(10)]
    donors     = [random.sample(alleles, 2) for _ in range(15)]


    similarity = build_similarity_matrix(recipients, donors)


    cost = convert_similarity(similarity)


    filtered = remove_not_accepted(cost)


    result = match(filtered)


    assert len(result) == len(recipients)


    used_donors = [d for d in result if d != -1]
    assert len(used_donors) == len(set(used_donors))


    for d in used_donors:
        assert 0 <= d < len(donors)
