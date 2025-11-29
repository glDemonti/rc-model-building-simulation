# syntax=docker/dockerfile:1

From continuumio/miniconda3

# Set working directory
WORKDIR /app

# copy environment file
COPY environment.yaml .
# Create the conda environment
RUN conda env create -f environment.yaml && \
    conda clean --all --yes

# Set environment variable
ENV CONDA_ENV=vm2

# Make RUN commands use the new environment:
SHELL ["bash", "-lc"]

# Install dependencies
COPY core/ core/ 
COPY projects/ projects/ 
COPY r_c_model/ r_c_model/ 
COPY ui/ ui/ 

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Create data directory
ENV VM2_DATA_DIR=/app/data

# Expose port
EXPOSE 8050

# Run the application
CMD ["bash", "-lc", "conda run -n ${CONDA_ENV} shiny run --host 0.0.0.0 --port 8050 ui/app.py"]
