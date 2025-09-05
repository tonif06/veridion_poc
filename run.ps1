Param(
    [string]$InputPath = "data/presales_data_sample.csv",
    [string]$OutputPath = "output"
)
python src/poc_entity_resolution.py --input $InputPath --output $OutputPath