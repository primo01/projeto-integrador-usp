from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import (
    EmrCreateJobFlowOperator,
    EmrAddStepsOperator,
    EmrTerminateJobFlowOperator,
)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Spark step que será adicionado DEPOIS que o cluster for criado
SPARK_STEPS = [
    {
        'Name': 'RunTaxiDataGolden',
        'ActionOnFailure': 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'cluster',
                's3://taxi-raw-grupo-5/scripts/gold_taxi_data.py'
            ],
        },
    }
]

# Configuração do cluster EMR
JOB_FLOW_OVERRIDES = {
    'Name': 'TaxiDataGolden',
    'ReleaseLabel': 'emr-6.15.0',
    'Applications': [{'Name': 'Spark'}],
    'Instances': {
        'InstanceGroups': [
            {
                'Name': 'Master',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'MASTER',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
            },
            {
                'Name': 'Workers',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 2,
            }
        ],
        'KeepJobFlowAliveWhenNoSteps': True,  # mantém o cluster vivo até terminarmos os steps
        'TerminationProtected': False,
    },
    'JobFlowRole': 'EMR_EC2_DefaultRole',
    'ServiceRole': 'EMR_DefaultRole',
    'LogUri': 's3://taxi-raw-grupo-5/logs/',
}

with DAG(
    'emr_taxi_data_golden_v2',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Executa processamento de dados de táxi no EMR com PySpark (monitorado)',
    tags=['emr', 'pyspark', 'taxi'],
) as dag:

    # 1. Criação do cluster
    create_cluster = EmrCreateJobFlowOperator(
        task_id='create_cluster',
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id='aws_default',
        region_name='us-east-1',
    )

    # 2. Adiciona o step de execução do script
    add_step = EmrAddStepsOperator(
        task_id='add_step',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value') }}",
        steps=SPARK_STEPS,
        aws_conn_id='aws_default',
    )

    # 3. Monitora o step até terminar
    step_sensor = EmrStepSensor(
        task_id='watch_step',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_step', key='return_value')[0] }}",
        aws_conn_id='aws_default',
    )

    # 4. Termina o cluster
    terminate_cluster = EmrTerminateJobFlowOperator(
        task_id='terminate_cluster',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_cluster', key='return_value') }}",
        aws_conn_id='aws_default',
    )

    create_cluster >> add_step >> step_sensor >> terminate_cluster