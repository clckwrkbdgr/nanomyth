DIST_DIR = dist

all: build

build: test
	python setup.py build
	python -m pip wheel --disable-pip-version-check . --no-deps --wheel-dir=$(DIST_DIR)

test:
	@python -m coverage run --source=. -m unittest $${TESTCASE:-discover}
	@python -m coverage report -m 

demo:
	@python demo/demo.py

autodemo:
	@python -m coverage run --source=. \
		--omit=setup.py,nanomyth/math/**.py,nanomyth/game/**.py,nanomyth/utils/**.py,nanomyth/view/utils/test/**.py \
		demo/demo.py auto $(AUTODEMOARGS)
	@python -m coverage report -m || true

clean:
	rm -rf $(DIST_DIR) build/ nanomyth.egg-info

.PHONY: demo autodemo
