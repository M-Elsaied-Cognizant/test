FROM ctsinazacrpd1c02.azurecr.io/devcontainers/python:3.11

WORKDIR /src

EXPOSE 8080
 
COPY src /src
 
RUN pip3 install -r requirements.txt

# NEUROSAN
# RUN pip install --no-cache-dir requirements-wheels/*.whl

RUN chmod +x /src/main.py
 
RUN groupadd --g 5000 appuser && \
    useradd -r -u 5000 -g appuser appuser
USER appuser
 
# CMD ["python", "/src/main.py"]

CMD ["pyagent", "run", "python", "/src/main.py"]
