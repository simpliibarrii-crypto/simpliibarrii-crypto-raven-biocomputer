import pytest

from raven_biocomputer.tools import (
    fasta_summary,
    find_motif,
    reverse_complement,
    sequence_stats,
    translate_dna,
)


def test_sequence_stats() -> None:
    result = sequence_stats({"sequence": "ACGTNN"})
    assert result["length"] == 6
    assert result["gc_fraction"] == 0.5
    assert result["counts"]["N"] == 2


def test_reverse_complement() -> None:
    assert reverse_complement({"sequence": "ATGC"})["sequence"] == "GCAT"


def test_overlapping_motif_positions() -> None:
    assert find_motif({"sequence": "ATATAT", "motif": "ATA"})["positions_zero_based"] == [0, 2]


def test_translate_dna() -> None:
    result = translate_dna({"sequence": "ATGGCC", "frame": 0})
    assert result["protein"] == "MA"


def test_fasta_summary() -> None:
    result = fasta_summary({"fasta": ">one\nACGT\n>two desc\nGGCC"})
    assert result["record_count"] == 2
    assert result["total_bases"] == 8


def test_invalid_base_is_rejected() -> None:
    with pytest.raises(ValueError, match="only A, C, G, T, N"):
        sequence_stats({"sequence": "ACGU"})
