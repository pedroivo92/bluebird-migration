from datetime import datetime
import pytz
from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text, select, update
from settings import *

class MigrationRepository:

    def __init__(self):
        self.engine = create_engine(DATABASE_CONNECTION_URL, pool_recycle=30, pool_pre_ping=True)
    
    def get_pending_migrations(self):
        self.database_conn = self.engine.connect()
        items = None
        try:
            query = "mg.id_globo, mg.current_email_address, mg.id_status, " \
                    "mg.customer_id, mg.cart_id, ps.id_stage " \
                    "from integratordb.migration as mg " \
                    "left join integratordb.process as ps on mg.id_globo = ps.id_migration " \
                    f"where id_status = {3} and cart_id is null "
    
            data = self.database_conn.execute(select(text(query)))
            items = data.fetchmany(10)

            return items
        except Exception as e:
            raise e 
        finally:
            self.database_conn.close()

    def update_migration_process(self, item, id_stage, error = None):
        self.database_conn = self.engine.connect()
        try:
            if error:
                error = error.replace("'", "")

            query = "insert into integratordb.process (id_migration, id_stage, error_description, reprocess) values " \
                    f"('{item['id_globo']}', {id_stage}, '{error}', 0) on duplicate key update " \
                    f"id_stage = {id_stage}, error_description = '{error}', reprocess = 0"

            self.database_conn.execute(text(query))
        except Exception as e:
            raise e
        finally:
            self.database_conn.close()

    def update_reprocess_status(self, item):
        self.database_conn = self.engine.connect()
        try:
            query = "update integratordb.process " \
                    f"set reprocess = 0 " \
                    f"where id_migration = '{item['id_globo']}'"

            self.database_conn.execute(text(query))
        except Exception as e:
            raise e
        finally:
            self.database_conn.close()

    def delete_process_registry(self, item):
        self.database_conn = self.engine.connect()
        try:
            query = f"DELETE FROM integratordb.process WHERE id_migration = '{item['id_globo']}'"
            self.database_conn.execute(text(query))
            
        except Exception as e:
            raise e
        finally:
            self.database_conn.close()

    def update_plan_informations(self, item, cart_id):
        self.database_conn = self.engine.connect()
        try:
            query = "update integratordb.migration " \
                    f"set cart_id = '{cart_id}' " \
                    f"where id_globo = '{item['id_globo']}'"

            self.database_conn.execute(text(query))
        except Exception as e:
            raise e
        finally:
            self.database_conn.close()
    
    def close_connections(self):
        self.engine.dispose()
