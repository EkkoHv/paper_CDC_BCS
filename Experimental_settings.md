# Experimental settings

This note summarizes the main experimental settings. Data files, generation instructions, and software access are described in [README.md](README.md).

## 1. Synthetic fields

The package contains ten synthetic parameter-field pairs numbered 1–10. Each pair uses 27 co-located sampling points in a 100 × 100 × 60 m domain, discretized on a 101 × 101 × 61 grid with 1 m spacing.

The fields combine spatial trends with correlated Gaussian residuals. The residual standard deviations are 7 and 1.9, the correlation coefficient is 0.85, and the exponential covariance length scale is 50 m. No measurement noise is added. The generation formulas, fixed seeds, and dependency versions are supplied in [Synthetic_data](Synthetic_data/).

## 2. Reconstruction settings

CDC-BCS reconstructs common and deviation components in the logarithmic domain using a shared discrete cosine transform dictionary. Univariate BCS reconstructs each parameter independently in the original parameter domain. OMP selects the basis functions, which remain fixed during posterior sampling.

| Experiment | CDC-BCS OMP tolerance | Univariate BCS OMP tolerance |
|---|---:|---:|
| Synthetic method comparison | 0.02 | 0.02 |
| Synthetic ablation | 0.02 | 0.02 |
| Field case | 0.011 | 0.01 |

The synthetic candidate dictionary contains 18 atoms. Synthetic BCS sampling initially uses four chains, with 4,000 burn-in iterations and 2,000 retained draws per chain at a thinning interval of five. Sampling is extended when needed to meet R-hat below 1.05 and bulk effective sample size of at least 100.

The comparison methods include Co-BCS, ordinary kriging, cokriging, and inverse distance weighting. The three-dimensional Co-BCS implementation uses the same DCT dictionary, transfers the secondary-field coefficient distribution to the primary-field prior, and uses Gibbs sampling.

## 3. Field-case data and settings

The case contains 18 paired measurements from 11 boreholes. Coordinates are in metres, water content is in percent, and void ratio is dimensionless. The local coordinate origin and column definitions are provided in [CaseSamplingData.xlsx](CaseSamplingData.xlsx).

CDC-BCS and Univariate BCS use grids of 22 × 34 × 24 and 21 × 34 × 24 nodes, respectively, both with spacing of (8, 8, 1) m. Each uses one chain with 500 burn-in iterations and 500 retained draws at a thinning interval of 20. These settings remain fixed across validation partitions. CDC-BCS realization bounds use the training minimum divided by 1.35 and the training maximum multiplied by 1.35.

The implementation internally rescales synthetic Parameter 2 by 1/10 and field-case void ratio by 10, then returns outputs to the supplied data scales. Distributed observations require no additional conversion.

## 4. Validation

The partitions are provided in [ValidationPartitions.xlsx](ValidationPartitions.xlsx).

- Initial field comparison: 15 training samples and three validation samples.
- Repeated cross validation: five repetitions of six folds, each with 15 training samples and three validation samples.
- Borehole holdout: 11 folds, withholding all observations from one borehole per fold.

Both parameters remain paired in every split. Comparison methods use the same partitions, and fitting and parameter selection use only the training data.
