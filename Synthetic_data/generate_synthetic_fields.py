"""Generate the ten positive synthetic field pairs supplied with this dataset.

This standalone data generator contains no BCS or modified BCS implementation.
Run: python generate_synthetic_fields.py --field-nos 4 --output regenerated
Omit --field-nos to generate all ten pairs. Existing outputs are never replaced.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

FIELD_NOS = tuple(range(1, 11))
MASTER_SEED = 2026101030


def load_seed_table(path):
    """Read the fixed random seeds associated with published pair numbers."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    table = {}
    for row in records:
        field_no = int(row["field_no"])
        if field_no not in FIELD_NOS or field_no in table:
            raise ValueError("Pair numbers must occur exactly once from 1 to 10.")
        seeds = np.array([int(row["gaussian_seed_1"]), int(row["gaussian_seed_2"])], dtype=np.uint32)
        expected = np.random.SeedSequence([MASTER_SEED, int(row["seed_key"]), 1]).generate_state(2)
        if not np.array_equal(seeds, expected):
            raise ValueError(f"Inconsistent seed configuration for pair {field_no}.")
        table[field_no] = seeds
    if set(table) != set(FIELD_NOS):
        raise ValueError("Seed configuration must contain all ten pairs.")
    return table


def geometry(sample_file: Path):
    """C order: c3 changes fastest, then c2, then c1. Coordinates are metres."""
    axes = (np.arange(101.0), np.arange(101.0), np.arange(61.0))
    xyz = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1).reshape(-1, 3)
    with sample_file.open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    samples = np.array([[float(row[k]) for k in ("c1_m", "c2_m", "c3_m")] for row in records])
    if samples.shape != (27, 3):
        raise ValueError("Exactly 27 sampling coordinates are required.")
    mask = np.all((xyz >= samples.min(0)) & (xyz <= samples.max(0)), axis=1)
    assert xyz.shape == (622261, 3) and int(mask.sum()) == 472017
    return xyz, samples, mask


def values_from_gaussian(coords, gaussian):
    """Polynomial trends plus correlated Gaussian residuals, in delivered units."""
    xi, eta, zeta = ((coords - [50.0, 50.0, 30.0]) / [50.0, 50.0, 30.0]).T
    trend_1 = 40.0 + 5.0 * zeta + 3.0 * (xi**2 - 1.0 / 3.0) + 2.0 * xi * eta
    trend_2 = 10.0 + 1.2 * zeta + 0.8 * (eta**2 - 1.0 / 3.0) - 0.4 * xi * zeta
    residual_2 = 0.85 * gaussian[:, 0] + np.sqrt(1.0 - 0.85**2) * gaussian[:, 1]
    return np.column_stack((trend_1 + 7.0 * gaussian[:, 0], trend_2 + 1.9 * residual_2))


def generate(field_no, xyz, samples, seed_table):
    import gstools as gs

    seeds = seed_table[int(field_no)]
    coords = np.vstack((xyz, samples))
    covariance = gs.Exponential(dim=3, var=1.0, len_scale=50.0)
    gaussian = np.column_stack([
        gs.SRF(covariance, generator="RandMeth", mode_no=4096, seed=int(seed))(
            coords.T, mesh_type="unstructured", store=False
        ) for seed in seeds
    ])
    values = values_from_gaussian(coords, gaussian)
    # These selected realizations are positive without clipping or offsetting.
    if not np.isfinite(values).all() or not np.all(values > 0):
        raise ValueError("A generated value is invalid or nonpositive. No correction was applied.")
    return values[:-len(samples)], values[-len(samples):], seeds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-nos", type=int, nargs="+", choices=FIELD_NOS, default=FIELD_NOS)
    parser.add_argument("--output", type=Path, default=Path("regenerated"))
    parser.add_argument("--sample-file", type=Path, default=Path(__file__).with_name("sampling_coordinates.csv"))
    parser.add_argument("--seed-file", type=Path, default=Path(__file__).with_name("field_seeds.csv"))
    args = parser.parse_args()
    seed_table = load_seed_table(args.seed_file)
    paths = [args.output / "geometry.npz"] + [args.output / f"field_{i:02d}.npz" for i in args.field_nos]
    if any(path.exists() for path in paths):
        raise FileExistsError("Choose a new output directory. Existing data will not be overwritten.")
    args.output.mkdir(parents=True, exist_ok=True)
    xyz, samples, mask = geometry(args.sample_file)
    np.savez_compressed(paths[0], coordinates_m=xyz, sampling_coordinates_m=samples, evaluation_mask=mask)
    for field_no in args.field_nos:
        truth, measured, seeds = generate(field_no, xyz, samples, seed_table)
        np.savez_compressed(args.output / f"field_{field_no:02d}.npz", truth=truth, measurements=measured, gaussian_seeds=seeds)
        print(json.dumps({"field_no": field_no, "gaussian_seeds": seeds.tolist(), "minimum": truth.min(0).tolist()}), flush=True)


if __name__ == "__main__":
    main()
