# etl_celery_pipeline

#How to run
# D:\etl_celery_pipeline>docker compose up -d

# below are use of each docker
etl_celery_pipeline 
etl_redis = redis:8.2.3-alpine
etl_celery_worker_gmail	 = etl_celery_pipeline-celery_worker_gmail
etl_celery_worker_db_saver = etl_celery_pipeline-celery_worker_db_saver
etl_celery_worker_parser = etl_celery_pipeline-celery_worker_parser
etl_celery_beat = etl_celery_pipeline-celery_beat
