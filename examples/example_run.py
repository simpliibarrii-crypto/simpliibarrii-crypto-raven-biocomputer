from raven_biocomputer import BioComputer

computer = BioComputer(workspace_root="runs")
receipt = computer.execute(
    task="Inspect a demonstration DNA sequence before downstream analysis.",
    tool="sequence_stats",
    payload={"sequence": "ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"},
)
print(receipt)
