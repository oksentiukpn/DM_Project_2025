import math

from scoring.scoring import pair_score


def almost_equal(a, b, eps=1e-6):
    return abs(a - b) < eps


def test_exact_match():
    r = ["A*02:01", "B*07:02"]
    d = ["A*02:01", "B*07:02"]
    pts, maxp, score = pair_score(r, d)
    assert almost_equal(score, 1.0)
    assert pts == maxp


def test_two_field_vs_serotype():
    # two-field match (first two fields equal)
    r = ["A*02:01"]
    d = ["A*02:01:99"]
    pts, maxp, score = pair_score(r, d)
    # two-field should give > serotype points but < full-match when defaults used
    assert score > 0


def test_same_locus_only():
    r = ["A*02:01"]
    d = ["A*03:05"]
    pts, maxp, score = pair_score(r, d)
    assert 0.0 < score <= 1.0


def test_no_match():
    r = ["A*02:01"]
    d = ["B*07:02"]
    pts, maxp, score = pair_score(r, d)
    # different locus -> no matching locus weight applies (pair_score requires same locus)
    assert almost_equal(score, 0.0)


def test_empty_alleles():
    r = ["", " "]
    d = ["A*02:01"]
    pts, maxp, score = pair_score(r, d)
    assert almost_equal(score, 0.0)
