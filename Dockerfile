# syntax=docker/dockerfile:1

FROM continuumio/miniconda3:24.1.2-0

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# copy environment file
COPY environment.yaml .
# Create the conda environment
RUN conda env create -f environment.yaml && \
    conda clean --all --yes

# Set environment variable
ENV CONDA_ENV=vm2

# Make RUN commands use the new environment:
SHELL ["bash", "-lc"]

# Copy application code
COPY core/ core/ 
COPY projects/ projects/ 
COPY r_c_model/ r_c_model/ 
COPY ui/ ui/ 

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

ENV VM2_DATA_DIR=/app/data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8050 || exit 1

# Activate conda environment and run the application
ENTRYPOINT ["conda", "run", "-n", "vm2", "--no-capture-output"]
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "8050", "ui/app.py"]
