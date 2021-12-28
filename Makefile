.PHONY=all test

# Force make to run targets sequentially
.NOTPARALLEL:

# Tests (directories) to run
TESTS=$(wildcard ./tests*/unit-tests/*)
# Edit this during dev to run just one test
#TESTS=./tests/unit-tests/a-test

all: test

test:
	$(info Run tests)
	echo "Run all tests: $(TESTS)"
	@for test in $(TESTS); do echo "Running test $$test" && cd $$test && make; done

clean:
	$(info Clean tests)
	echo "Clean all tests: $(TESTS)"
	@for test in $(TESTS); do echo "Cleaning test $$test" && cd $$test && make clean; done
