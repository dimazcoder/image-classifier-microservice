NAME=image_classifier
VERSION=latest

DEV_IMAGE = $(NAME)_dev:$(VERSION)
DEV_CONTAINER = $(NAME)_dev
DEV_PORTS = 7776:7776

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "Makefile for Image Classifier"
	@echo ""
	@echo "Usage:"
	@echo "  make start-dev       Clear, Build and Run the development environment"
	@echo "  make build-dev       Build the development environment"
	@echo "  make run-dev         Run the development environment"
	@echo "  make clear-dev       Clear the development environment"
	@echo ""

# Start targets
.PHONY: start-dev
start-dev: clear-dev build-dev run-dev

# Build targets
.PHONY: build-dev
build-dev:
	@echo "Building development environment..."
	docker build -t $(DEV_IMAGE) -f Dockerfile .

# Run targets
.PHONY: run-dev
run-dev:
	@echo "Running development environment..."
	docker run --restart=always --name $(DEV_CONTAINER) -v $(PWD):/app -p $(DEV_PORTS) $(DEV_IMAGE)

# Clear targets
.PHONY: clear-dev
clear-dev:
	@echo "Clearing development environment..."
	-docker stop $(DEV_CONTAINER)
	-docker rm $(DEV_CONTAINER)
	-docker rmi $(DEV_IMAGE)
