# Data and software guide

**Manuscript:** Three-Dimensional Geotechnical Site Characterization from Sparse Co-Located Measurements via Common-Deviation Component Decomposition

This package provides the field measurements, validation partitions, synthetic reference fields, a standalone synthetic field generator, reconstruction settings, and the ASSD-BCS software installer.

## 1. Contents

| File or folder | Contents |
|---|---|
| [CaseSamplingData.xlsx](CaseSamplingData.xlsx) | The 18 paired sampling measurements from the field case and column definitions |
| [ValidationPartitions.xlsx](ValidationPartitions.xlsx) | The initial split, repeated cross validation, and borehole holdouts |
| [Experimental_settings.md](Experimental_settings.md) | Summary of experimental settings and validation procedures |
| `Case_sampling_data/` | Field-case sampling measurements and column definitions in CSV format |
| `Validation/` | Three CSV files for the initial split, repeated cross validation, and borehole holdouts |
| `Synthetic_data/` | Generator, dependency versions, geometry, sampling coordinates, sampled values, and ten synthetic reference field pairs |
| `Software/` | ASSD-BCS 1.2 Windows installer |

The spreadsheets and corresponding CSV files contain the same data. Numeric cells retain their stored precision even when their display is rounded.

## 2. Field-case sampling measurements and validation partitions

The field-case sampling dataset contains **18 paired measurements from 11 boreholes**. Samples are numbered **1–18** in `sample_no` throughout the data and validation files. `borehole_no` identifies the 11 borehole groups. Samples with the same borehole number belong to the same borehole.

- Coordinates are in metres. Local coordinates equal absolute coordinates minus `(3056732.92, 376863.93, 1916.66)`.
- `water_content_percent` stores water content in percent. For example, `33.7` means 33.7%. The corresponding absolute errors are expressed in percentage points.
- `void_ratio` stores the original dimensionless void ratio. For example, `1.106` means 1.106. No further factor of ten is needed for these distributed observations.
- `soil_unit` gives the layer code and English soil name, such as `2-1 Clay` and `2-3 Clay with rock fragments`. The layer codes are retained.

The **initial split** uses samples **1–15 for training** and **16–18 for validation**. It is listed in `Validation/initial_split.csv`.

**Repeated sixfold cross validation** uses five repetitions and 30 splits in total. Each split contains 15 training samples and three validation samples. Every sample is withheld once per repetition. The split seed is `2026101504`. The partitions are recorded in `Validation/repeated_cv_30_splits.csv`. These are sample-level partitions. The MAE is calculated from the 18 held-out predictions in each repetition, then averaged across repetitions.

**Leave-one-borehole-out validation** has 11 folds. All observations from one borehole are withheld together in each fold. The partitions are recorded in `Validation/borehole_leave_one_out_11_splits.csv`. The overall MAE is pooled over all 18 held-out observations.

In the split-list files, `training_sample_nos` and `validation_sample_nos` contain sample numbers separated by semicolons. All methods use the same recorded partitions. Reconstruction and validation settings are given in [Experimental_settings.md](Experimental_settings.md).

## 3. Synthetic reference fields and generator

The ten synthetic field pairs are numbered **1–10**. Files are named `field_01.npz` through `field_10.npz`. These are the ten selected demonstration pairs used in the synthetic experiment. The experimental design is described in [Experimental_settings.md](Experimental_settings.md).

The full domain has `101 × 101 × 61 = 622,261` nodes at 1 m spacing. All pairs use the same 27 sampling coordinates. The evaluation mask identifies the `472,017` nodes within the sampling-point bounding box. The generator implements the spatial trends and correlated Gaussian residuals using residual standard deviations of `(7, 1.9)`, residual correlation `0.85`, and an exponential covariance length scale of `50 m`. No measurement noise is added.

`Synthetic_data/geometry.npz` contains:

| Array | Shape | Meaning |
|---|---|---|
| `coordinates_m` | `(622261, 3)` | Full-grid coordinates in metres |
| `sampling_coordinates_m` | `(27, 3)` | Fixed sampling coordinates |
| `evaluation_mask` | `(622261,)` | Boolean mask identifying the evaluation region |

Each `Synthetic_data/fields/field_<NN>.npz`, where `NN` is the two-digit pair number from `01` to `10`, contains:

| Array | Shape | Meaning |
|---|---|---|
| `truth` | `(622261, 2)` | Full-grid reference values of Parameters 1 and 2 |
| `measurements` | `(27, 2)` | Parameter values at the sampling coordinates |
| `gaussian_seeds` | `(2,)` | Seeds of the two independent Gaussian fields |

Rows use C order, with **c3 changing fastest, then c2, then c1**. A reference-field column can be reshaped using `reshape(101, 101, 61, order="C")`. Evaluation values are obtained with `truth[evaluation_mask]`.

`sampling_coordinates.csv`, `measurements_10_pairs.csv`, and `field_seeds.csv` provide the sampling coordinates, sampled values, and seed configuration in CSV format. The `field_no` column identifies pairs 1–10 throughout these files. `gaussian_seed_1` and `gaussian_seed_2` preserve the random seeds, and `seed_key` is used by the field generator. These seed values are separate from the pair numbers. The synthetic parameters retain their own numerical scales. The field-case void-ratio conversion does not apply to them.

To regenerate the reference fields, open the `Synthetic_data` directory and run:

```text
python -m pip install -r requirements.txt
python generate_synthetic_fields.py --output regenerated_all_ten
```

The generator command produces all ten pairs. The generator reads the fixed seeds for each pair from `field_seeds.csv` and uses GSTools `RandMeth` with 4,096 modes. It checks these seeds against `SeedSequence([2026101030, seed_key, 1])`. Changing a pair number does not replace its seed configuration. It refuses to overwrite existing output files. The dependency versions are specified in `requirements.txt`.

## 4. ASSD-BCS software

**Official software page:**

[Professor Yu Wang's Bayesian Compressive Sampling/Sensing software page](https://sites.google.com/site/yuwangcityu/software-download/bayesian-compressive-samplingsensing-bcs?authuser=0)

**Download link provided on that page:**

[ASSD-BCS 1.2 Windows installer](https://drive.google.com/file/d/1oiQvUR3CQxwmb6Bg936A5-d1aFOztyYb/view?usp=sharing)

The installer is supplied as `Software/ASSD-BCS-1.2-win64.msi` (download date: 18 October 2026).

The official page associates the software with:

Lyu, B., Hu, Y., and Wang, Y. (2023). Data-driven development of three-dimensional subsurface models from sparse measurements using Bayesian compressive sampling (BCS): A benchmarking study. [https://doi.org/10.1061/AJRUA6.RUENG-935](https://doi.org/10.1061/AJRUA6.RUENG-935).

The ASSD-BCS software can be used for univariate BCS reconstruction. The proposed CDC-BCS method builds on univariate BCS by introducing logarithmic transformation and common-deviation component decomposition.
