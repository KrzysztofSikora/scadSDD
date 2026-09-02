.PHONY: setup build validate test lint typecheck render view all clean \
	rifle-build rifle-validate rifle-render rifle-all rifle-clean rifle-view \
	planter-build planter-validate planter-render planter-all planter-clean planter-view

VENV_PYTHON := .venv/bin/python
VENV_PYTEST := .venv/bin/pytest
VENV_RUFF := .venv/bin/ruff
VENV_MYPY := .venv/bin/mypy

setup:
	bash scripts/setup.sh

build:
	bash scripts/build.sh

validate:
	bash scripts/validate.sh

test:
	$(VENV_PYTEST) tests/ -v

lint:
	$(VENV_RUFF) check src tests

typecheck:
	$(VENV_MYPY) src

render:
	bash scripts/render.sh

view:
	bash scripts/view.sh

all:
	$(VENV_PYTHON) -m cad_project.cli all

clean:
	bash scripts/clean.sh

# --- Magnetic rifle barrel mount (independent second model) -----------------

rifle-build:
	$(VENV_PYTHON) -m cad_project.rifle_mount.cli build

rifle-validate:
	$(VENV_PYTHON) -m cad_project.rifle_mount.cli validate

rifle-render:
	$(VENV_PYTHON) -m cad_project.rifle_mount.cli render

rifle-all:
	$(VENV_PYTHON) -m cad_project.rifle_mount.cli all

rifle-clean:
	$(VENV_PYTHON) -m cad_project.rifle_mount.cli clean

rifle-view:
	bash scripts/view.sh output/rifle-mount/step/base.step output/rifle-mount/step/arm.step

# --- Premium self-watering planter (independent third model) ---------------

planter-build:
	$(VENV_PYTHON) -m cad_project.planter.cli build

planter-validate:
	$(VENV_PYTHON) -m cad_project.planter.cli validate

planter-render:
	$(VENV_PYTHON) -m cad_project.planter.cli render

planter-all:
	$(VENV_PYTHON) -m cad_project.planter.cli all

planter-clean:
	$(VENV_PYTHON) -m cad_project.planter.cli clean

planter-view:
	bash scripts/view.sh output/planter/step/insert.step output/planter/step/reservoir.step
