import psycopg2

connection = psycopg2.connect(
    user='project_20',
    password='ixapmn',
    host='140.117.68.66',
    port='5432',
    dbname='project_20'  # PostgreSQL 的資料庫名稱
)
cursor = connection.cursor()

