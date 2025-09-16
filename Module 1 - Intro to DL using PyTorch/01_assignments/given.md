# Assignment 1

## Given

In this project, we provide a water quality dataset from the Central Pollution Control Board
(CPCB). You will use this dataset to predict water quality.

Access to clean water is a fundamental necessity, yet water quality can vary significantly based
on environmental, geographical, and human factors. The dataset includes water quality
monitoring data from across India, with chemical and physical parameters measured at various
locations over different years (2019, 2020, 2021, 2022).

The dataset contains the following columns:

Well_ID, State, District, Block, Village: Geographical identifiers of water sampling locations.

Latitude, Longitude: Spatial coordinates for precise mapping.

Year: The year in which the sample was recorded.

Water Quality Indicators: pH, Electrical Conductivity (EC), Carbonates (CO3), Bicarbonates
(HCO3), Chlorides (CI), Sulfates (SO4), Nitrates (NO3), Total Hardness (TH), Calcium (Ca),
Magnesium (Mg), Sodium (Na), Potassium (K), Fluoride (F), Total Dissolved Solids (TDS).

Target Variables:

Water Quality Index (WQI): A numerical representation of overall water quality derived from
chemical and physical parameters.

Water Quality Classification: A categorical label indicating the quality of water (e.g., Good, Poor,
Unsuitable for Drinking).

## Deliverables

In this project, your task is to build Deep Learning Neural Networks to predict the following:

Water Quality Index (WQI)

Water Quality Classification

You can download the dataset from the attachment provided and build the models using that.
Once the models are built, calculate metrics such as the R2 score for regression and accuracy/F1
score for classification, and submit your ipynb file for evaluation.