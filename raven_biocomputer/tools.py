from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

ToolFunction = Callable[[Mapping[str, Any]], dict[str, Any]]
_DNA_RE = re.compile(r"^[ACGTN]*$")
_COMPLEMENT = str.maketrans("ACGTN", "TGCAN")

_CODONS = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def _clean_dna(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("sequence must be a string")
    sequence = re.sub(r"\s+", "", value).upper()
    if not sequence:
        raise ValueError("sequence cannot be empty")
    if not _DNA_RE.fullmatch(sequence):
        raise ValueError("sequence may contain only A, C, G, T, N and whitespace")
    return sequence


def sequence_stats(payload: Mapping[str, Any]) -> dict[str, Any]:
    sequence = _clean_dna(payload.get("sequence"))
    counts = Counter(sequence)
    informative = len(sequence) - counts.get("N", 0)
    gc = counts.get("G", 0) + counts.get("C", 0)
    return {
        "length": len(sequence),
        "counts": {base: counts.get(base, 0) for base in "ACGTN"},
        "gc_fraction": round(gc / informative, 6) if informative else None,
        "ambiguous_fraction": round(counts.get("N", 0) / len(sequence), 6),
    }


def reverse_complement(payload: Mapping[str, Any]) -> dict[str, Any]:
    sequence = _clean_dna(payload.get("sequence"))
    return {"sequence": sequence.translate(_COMPLEMENT)[::-1], "length": len(sequence)}


def find_motif(payload: Mapping[str, Any]) -> dict[str, Any]:
    sequence = _clean_dna(payload.get("sequence"))
    motif = _clean_dna(payload.get("motif"))
    positions: list[int] = []
    start = 0
    while True:
        index = sequence.find(motif, start)
        if index < 0:
            break
        positions.append(index)
        start = index + 1
    return {"motif": motif, "positions_zero_based": positions, "count": len(positions)}


def translate_dna(payload: Mapping[str, Any]) -> dict[str, Any]:
    sequence = _clean_dna(payload.get("sequence"))
    frame = int(payload.get("frame", 0))
    if frame not in (0, 1, 2):
        raise ValueError("frame must be 0, 1, or 2")
    coding = sequence[frame:]
    amino_acids = []
    for index in range(0, len(coding) - 2, 3):
        codon = coding[index : index + 3]
        amino_acids.append("X" if "N" in codon else _CODONS[codon])
    return {
        "protein": "".join(amino_acids),
        "frame": frame,
        "translated_codons": len(amino_acids),
        "trailing_bases": len(coding) % 3,
    }


def fasta_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    text = payload.get("fasta")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("fasta must be a non-empty string")

    records: list[dict[str, Any]] = []
    header: str | None = None
    parts: list[str] = []

    def flush() -> None:
        nonlocal header, parts
        if header is None:
            return
        sequence = _clean_dna("".join(parts))
        stats = sequence_stats({"sequence": sequence})
        records.append({"id": header.split()[0], "description": header, **stats})

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            flush()
            header = line[1:].strip()
            if not header:
                raise ValueError("FASTA header cannot be empty")
            parts = []
        else:
            if header is None:
                raise ValueError("FASTA sequence appeared before a header")
            parts.append(line)
    flush()
    if not records:
        raise ValueError("no FASTA records found")
    return {
        "record_count": len(records),
        "total_bases": sum(record["length"] for record in records),
        "records": records,
    }


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    function: ToolFunction
    input_example: dict[str, Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self.register(ToolSpec("sequence_stats", "Count DNA bases and calculate GC and ambiguity fractions.", sequence_stats, {"sequence": "ACGTACGTNN"}))
        self.register(ToolSpec("reverse_complement", "Return the reverse complement of a DNA sequence.", reverse_complement, {"sequence": "ATGCCG"}))
        self.register(ToolSpec("find_motif", "Find overlapping motif positions in a DNA sequence.", find_motif, {"sequence": "ATATAT", "motif": "ATA"}))
        self.register(ToolSpec("translate_dna", "Translate a DNA sequence in reading frame 0, 1, or 2.", translate_dna, {"sequence": "ATGGCCATTGTAATGGGCCGCTGA", "frame": 0}))
        self.register(ToolSpec("fasta_summary", "Summarize one or more DNA FASTA records.", fasta_summary, {"fasta": ">sample\nACGTACGT"}))

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def list(self) -> list[dict[str, Any]]:
        return [{"name": spec.name, "description": spec.description, "input_example": spec.input_example} for spec in self._tools.values()]

    def run(self, name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        try:
            spec = self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc
        return spec.function(payload)
