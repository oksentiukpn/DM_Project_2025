"""
HLA input function
"""

def get_hla_dict(path: str) -> dict:
    """
    Reads a path file and returns a dictionary of where key is HLAid and value is alele .
    """
    hla_dict = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "AlleleID,Allele":
                break
        for line in f:
            line = line.strip().split(",")
            hla_id = line[0]
            alele = line[1]
            hla_dict[hla_id] = alele

    return hla_dict


print(get_hla_dict("hla_example.txt"))
