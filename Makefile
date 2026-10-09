.PHONY: update validate report test build serve

update:
	python3 scripts/update.py

validate:
	python3 scripts/validate.py

report:
	python3 scripts/report.py

test:
	python3 -m unittest discover -s tests -v

build: validate
	python3 scripts/build_site.py

serve: build
	python3 -m http.server 4173 --directory dist

