.PHONY: run test lint install uninstall
run:        ## run from source
	PYTHONPATH=src python3 -m numpadbind
test:
	python3 -m pytest -q
lint:
	python3 -m pyflakes src tests
install:
	./scripts/install.sh
uninstall:
	./scripts/uninstall.sh
