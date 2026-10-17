FROM python:3.12-slim
RUN pip install --no-cache-dir "psycopg[binary]==3.2.10" "oracledb==3.3.0" "PyYAML==6.0.2"
WORKDIR /repo
ENTRYPOINT ["python", "-I", "/repo/grading/grade.py"]
