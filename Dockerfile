# Use official Python lightweight image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Create and set working directory
WORKDIR /app

# Install system dependencies (required for some math/plot libs, avoiding PyQt6 display errors in headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies first (for docker layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip
# Filter out PyQt6 from headless container if necessary, or just install everything
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port for Streamlit Dashboard
EXPOSE 8501

# Default command: Run the Interactive Dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
