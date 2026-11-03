PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
.PHONY: setup data calibrate backend frontend build test evaluate e2e
setup:
	python3.13 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt
	cd frontend && npm install
calibrate:
	$(PYTHON) -m benchmarks.calibrate_runtime
data:
	$(PYTHON) -m benchmarks.generate_cases
backend:
	$(PYTHON) -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
frontend:
	cd frontend && npm run dev
build:
	cd frontend && npm run build
test:
	$(PYTEST) tests/test_physics_and_defects.py tests/test_verifier.py tests/test_investigation_loop.py tests/test_scientific_audit.py tests/test_demonstration.py tests/test_demonstration_public.py -v
evaluate:
	$(PYTHON) -m benchmarks.evaluate
e2e:
	bash scripts/verify_e2e.sh

.PHONY: demonstration-data demonstration-evaluate
demonstration-data:
	$(PYTHON) -m demonstrations.generate --partition development
demonstration-evaluate:
	$(PYTHON) -m demonstrations.evaluate --partition development
