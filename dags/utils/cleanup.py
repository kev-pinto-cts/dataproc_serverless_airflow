from airflow.utils.db import provide_session
from airflow.models import XCom


@provide_session
def cleanup_xcom(session=None, **kwargs):
    dag = kwargs['dag']
    dag_id = dag.dag_id
    # It will delete all xcom of the dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()

