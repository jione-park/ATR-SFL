.PHONY: check-docs docker-build docker-shell

check-docs:
	python3 scripts/validate_docs.py

docker-build:
	docker build -f docker/Dockerfile -t hermes-research .

docker-shell:
	docker compose -f docker/compose.gpu.yml run --rm research bash
