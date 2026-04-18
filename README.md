# Philadelphia Murals vs Crime Rates

A data science research project examining whether two community-based environmental interventions — the **Philadelphia Mural Arts Program** and the **Pennsylvania Horticultural Society's LandCare vacant lot greening program** — are associated with measurable reductions in neighborhood crime rates across Philadelphia's 159 neighborhoods over an 18-year period (2006–2024).

---

## Research Question

> Do Philadelphia neighborhoods with higher mural density and LandCare greening exhibit lower crime rates, and did these interventions causally reduce crime after implementation?

---

## Project Structure

```
PHILLY_MURALS_VS_CRIME_RATES/
│
├── main.ipynb                          # Main analysis notebook
├── scrape_murals.py                    # Mural data scraper (Mural Arts Philadelphia)
├── scrape_crimes.py                    # Crime data scraper (OpenDataPhilly / Carto API)
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
│
├── data/
│   ├── maps/
│   │   ├── neighborhoods.geojson       # Philadelphia neighborhood boundaries (159)
│   │   └── streets.geojson             # Major street centerlines
│   ├── murals/
│   │   ├── philadelphia_murals_raw.geojson   # Raw scraped mural data
│   │   └── philadelphia_murals.geojson       # Cleaned mural data
│   ├── greenspace/
│   │   ├── landcare.geojson            # PHS LandCare vacant lot parcels
│   │   └── ppr_program_sites.geojson   # PPR active community sites
│   ├── crime/
│   │   └── philly_crime.csv            # PPD incident data 2006–2024 (3.3M rows)
│   └── processed/
│       └── neighborhood_features_complete.csv  # Final feature matrix (159 x 18)
│
└── outputs/
    ├── map_murals_only.png
    ├── map_greenspace_only.png
    ├── map_city_only.png
    ├── map_all_interventions.png
    ├── map_crime_rates.png
    ├── map_hex_density.png
    ├── map_kmeans_clusters.png
    ├── kmeans_cluster_selection.png
    ├── kmeans_crime_by_cluster.png
    ├── did_event_study_3row.png
    ├── viz_rf_feature_importance.png
    ├── viz_nb_coefficients.png
    ├── viz_morans_i.png
    └── viz_spatial_lag_rho.png
```

---

## Datasets

| Dataset | Source | Records | Description |
|---|---|---|---|
| Mural Arts Philadelphia | muralarts.org (scraped) | 1,092 murals | Location and creation year of official murals |
| LandCare Program | OpenDataPhilly | 12,183 parcels | PHS-maintained greened vacant lots |
| PPR Program Sites | OpenDataPhilly | 169 sites | Active community sites (rec centers, playgrounds, pools) |
| Crime Incidents | OpenDataPhilly / Carto | 3.28M incidents | PPD Part I & II incidents, 2006–2024 |
| Neighborhoods | OpenDataPhilly | 159 polygons | Philadelphia neighborhood boundaries |
| Streets | OpenDataPhilly | — | Major street centerlines |

---

## Methodology

The project uses a five-method analytical framework that separates spatial description from causal inference:

| # | Method | Purpose |
|---|---|---|
| 1 | Negative Binomial Regression | Where are interventions and crime concentrated? |
| 2 | Random Forest Regression | Which features best predict crime? |
| 3 | Spatial Lag Regression | How does crime spread spatially? |
| 4 | K-Means Clustering | What neighborhood profiles exist? |
| 5 | Difference-in-Differences | Did interventions actually reduce crime? |

### Four Model Variants

Each regression method is run four times with different feature sets:

| Model | Features | Purpose |
|---|---|---|
| A | `mural_density` | Baseline — isolates mural effect |
| B | `landcare_density`, `ppr_site_density` | Greenspace-only comparison |
| C | A + B combined | Tests additive effect |
| D | C + `mural_x_landcare` interaction | Tests synergy effect |

### Three Response Variables

- `crime_rate_total` — all incidents per km²
- `crime_rate_property` — theft, burglary, vandalism per km²
- `crime_rate_violent` — assault, robbery, homicide, weapons per km²

---

## Key Findings

- Both programs are deployed in Philadelphia's highest-crime, highest-vacancy areas — **selection bias** is present in all cross-sectional analysis and does not imply causation
- The **interaction term** (mural × LandCare co-presence) is negative and significant across Negative Binomial and Spatial Lag models — suggesting a synergistic crime suppression effect in neighborhoods where both programs operate simultaneously
- **Moran's I ≈ 0.56** — strong spatial autocorrelation confirmed; high-crime neighborhoods cluster geographically
- **Difference-in-Differences** (Method 5) provides causal evidence:
  - Murals: total crime −89/km² (p<0.001), property crime −23/km² (p=0.001), violent crime −10/km² (p=0.004)
  - LandCare: total crime −78/km² (p=0.007), violent crime −23/km² (p<0.001), property crime ns
  - Combined: total crime −62/km² (p=0.029), property crime +17/km² (revitalization effect), violent crime −9/km² (marginal)
- **K-Means clustering** (k=3) identifies three distinct neighborhood typologies: Low Intervention (128), High LandCare/High Need (11), High Mural/High Density (20)

---

## Setup & Installation

### Requirements

Python 3.10+ recommended.

Install all dependencies:

```bash
pip install geopandas pandas numpy matplotlib seaborn requests shapely libpysal spreg esda splot scikit-learn statsmodels h3
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

### Data Collection

Mural data is scraped from the Mural Arts Philadelphia website:

```bash
python scrape_murals.py
```

Crime data is downloaded from the OpenDataPhilly Carto API (2006–2024):

```bash
python scrape_crimes.py
```

> **Note:** The crime CSV is approximately 890MB. Download time will vary depending on your connection speed. The scraper pulls one year at a time to avoid API timeouts.

All other datasets (neighborhoods, streets, LandCare, PPR sites) are downloaded directly inside the notebook via their OpenDataPhilly API URLs.

### Running the Notebook

```bash
jupyter notebook main.ipynb
```

Run all cells top to bottom. Total runtime is approximately 10–15 minutes on a standard laptop, with the crime spatial join and model fitting being the most time-intensive steps.

---

## Theoretical Framework

The analysis is grounded in two established criminological frameworks:

- **Broken Windows Theory** (Wilson & Kelling, 1982) — visible signs of disorder invite further crime; visible order and community investment should deter it
- **Crime Prevention Through Environmental Design (CPTED)** (Jeffery, 1971; Newman, 1972) — well-maintained, purposeful environments reduce criminal opportunity through natural surveillance and territorial reinforcement

---

## Key References

- Branas, C.C. et al. (2018). Citywide cluster randomized trial to restore blighted vacant land and its effects on violence, crime, and fear. *PNAS*, 115(12), 2946–2951.
- Moritz, M. (2024). Murals and crime in Philadelphia. Presented at Penn Grad Talks, University of Pennsylvania.
- Jeong, H. & Hu, Y. (2025). The role of public murals in street vitality. *Cities*, 163.
- Wilson, J.Q. & Kelling, G.L. (1982). Broken windows. *The Atlantic Monthly*, 249(3), 29–38.
- Macdonald, J. et al. (2022). Reducing crime by remediating vacant lots. *Journal of Experimental Criminology*, 18, 639–664.

---

## Limitations

- Cross-sectional analysis (Methods 1–4) cannot establish causality due to selection bias
- LandCare dataset reflects currently maintained lots only — decommissioned lots are not recorded
- Socioeconomic controls (income, unemployment, vacancy rates) were not included in the feature matrix
- 159 neighborhoods is a small sample for machine learning methods — results should be interpreted with appropriate caution
- Study period (2006–2024) includes major confounding events (opioid crisis, COVID-19, gentrification)

---

## Course Context

This project was completed as part of the **H9DAI — Master of Science in Artificial Intelligence** program. The analytical design, research questions, and interpretation were developed by the student; code was built collaboratively using AI-assisted development tools.

---

## License

This project uses publicly available data from OpenDataPhilly and Mural Arts Philadelphia. All data is used for academic research purposes only.
