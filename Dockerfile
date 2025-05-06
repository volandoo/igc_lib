FROM python:3.10-slim

WORKDIR /app

# Copy only requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies with pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the rest of the project files
COPY . /app/

# Create tracks directory
RUN mkdir -p /app/tracks

# Set the volume for tracks
VOLUME /app/tracks

# Set the entrypoint
EXPOSE 8000

ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
