DIST_DIR = dist

all: test
	python setup.py build
	python -m pip wheel --disable-pip-version-check . --no-deps --wheel-dir=$(DIST_DIR)

test:
	@python -m coverage run --source=. -m unittest $${TESTCASE:-discover}
	@python -m coverage report -m 

demo:
	python demo/demo.py

clean:
	rm -rf $(DIST_DIR) build/ nanomyth.egg-info

.PHONY: demo
