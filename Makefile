.PHONY: build run run-debug test clean

# This is the secret key for the API, replace with your own
SECRET-KEY=1234567890

run:
	docker run -p 8000:8000 -e SECRET_KEY=$(SECRET-KEY) igclib

build:
	docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t igclib .
