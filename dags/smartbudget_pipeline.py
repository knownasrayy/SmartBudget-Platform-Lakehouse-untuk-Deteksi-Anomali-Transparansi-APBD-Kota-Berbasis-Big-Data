from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'smartbudget',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Absolut Path ke Proyek
PROJECT_PATH = "C:/Users/rayha/OneDrive/Documents/SEMESTER 4/2. Big Data & Lake House/SmartBudget Platform Lakehouse untuk Deteksi Anomali & Transparansi APBD Kota"

with DAG(
    'smartbudget_pyspark_pipeline',
    default_args=default_args,
    description='Orkestrasi ETL dan Machine Learning SmartBudget menggunakan PySpark & Delta Lake',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['lakehouse', 'apbd', 'pyspark', 'mllib'],
) as dag:

    # Task 1: Silver Transformation (Membersihkan Data Bronze)
    silver_transform = BashOperator(
        task_id='silver_transform',
        bash_command=f"cd '{PROJECT_PATH}' && powershell.exe -File run_pyspark.ps1 src/lakehouse/silver_transform.py",
    )

    # Task 2: Gold Transformation (Agregasi Data untuk Dashboard)
    gold_transform = BashOperator(
        task_id='gold_transform',
        bash_command=f"cd '{PROJECT_PATH}' && powershell.exe -File run_pyspark.ps1 src/lakehouse/gold_transform.py",
    )

    # Task 3: Machine Learning Anomaly Detection (K-Means Skoring)
    anomaly_detection = BashOperator(
        task_id='anomaly_detection',
        bash_command=f"cd '{PROJECT_PATH}' && powershell.exe -File run_pyspark.ps1 src/ml_engine/anomaly_detector.py",
    )

    # Menentukan Flow (Dependencies)
    # Pipeline: Bronze -> Silver -> (Gold Aggregation & MLlib Anomaly Detection)
    silver_transform >> [gold_transform, anomaly_detection]
