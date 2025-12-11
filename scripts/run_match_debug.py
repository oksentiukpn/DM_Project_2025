import random
import sys
from pathlib import Path
# Ensure repo root is on sys.path so `tests` package can be imported when
# running the script directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.hlainput import get_hla_dict
from scoring.scoring import pair_score
from matrix_builder import build_similarity_matrix
from matching import convert_similarity, remove_not_accepted, match

allele_dict = get_hla_dict("data/Allelelist.txt")
alleles = list(allele_dict.values())
random.seed(42)
recipients = [random.sample(alleles, 2) for _ in range(10)]
donors     = [random.sample(alleles, 2) for _ in range(15)]

similarity = build_similarity_matrix(recipients, donors)
print('similarity dims:', len(similarity), len(similarity[0]))

cost = convert_similarity(similarity)
print('cost dims:', len(cost), len(cost[0]))

filtered = remove_not_accepted(cost)
print('filtered dims:', len(filtered), len(filtered[0]))

result = match(filtered)
print('result len:', len(result))
print('recipients len:', len(recipients))
print('result:', result)

# Show mapping of recipients to donors when not -1
for i, d in enumerate(result[:len(recipients)]):
    print(i, '->', d)
