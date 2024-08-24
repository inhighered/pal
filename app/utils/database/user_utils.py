from app.utils.database.models import (
    User,
)

from app.utils.database.db_utils import (
    with_connection,
)

from psycopg import Connection

from logging import getLogger
_logger = getLogger(__name__)

# ---------------- User Queries ----------------- 


@with_connection
def get_user_from_ip(conn: Connection, user_ip: str) -> User:
    sql = f"""SELECT 
        session_id,
        user_ip,
        timestamp
    FROM 
        app.users
    WHERE 
        user_ip = %s
    ORDER BY timestamp DESC 
    LIMIT 1
    """
    cur = conn.cursor()
    cur.execute(sql, (user_ip, ))
    results_tuple = cur.fetchone()

    _logger.info(f"User results: {results_tuple} \n For User IP: {user_ip}")

    user = User(str(results_tuple[0]), str(results_tuple[1]), timestamp = results_tuple[2])
    
    return user


