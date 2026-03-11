ACK_DIR := ackfuss-4.4.1

.PHONY: all build integration-test clean

all: build integration-test

build:
	$(MAKE) -C $(ACK_DIR)/src

integration-test: build
	python3 $(ACK_DIR)/tests_integration_mud.py

clean:
	$(MAKE) -C $(ACK_DIR)/src clean
