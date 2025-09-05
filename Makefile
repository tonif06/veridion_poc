.PHONY: run clean env

INPUT?=data/presales_data_sample.csv
OUTPUT?=output

run:
	python src/poc_entity_resolution.py --input $(INPUT) --output $(OUTPUT)

clean:
	rm -f $(OUTPUT)/*.csv

env:
	python -V
	pip show pandas || pip install pandas

json:
	python src/start_json.py --config config/config.json
