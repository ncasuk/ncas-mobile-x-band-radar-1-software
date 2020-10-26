import psycopg2
from .base_handler import BaseHandler

class DataBaseHandler(BaseHandler):

    def __init__(self, connection_info, error_types, table_name='results'):
        """ 
        Constructs an instace of the database handler.
        
        :param connection_info: (str) Connection string in the psycopg2 format,
        "dbname=<db_name> user=<user_name> password=<password>".
        :param error_types: (list) List of the string names of the types of errors that can occur.
        :param table_name: (str) Optional string for the name of the table created (default 'results')
        """

        self.error_types = error_types
        self.conn = psycopg2.connect(connection_info)
        self.cur = self.conn.cursor()
        self.table_name = table_name
        self._create_table()

    def _create_table(self):
        """
         Creates a table called <self.table_name> with primary key id varchar(255) and 
        result varchar(255)
         """

        self.cur.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name}' \
             '(id varchar(255) PRIMARY KEY, result varchar(255) NOT NULL);')
        self.conn.commit()

    def _delete_table(self):
        """ 
        Drops the database table 
        """

        self.cur.execute(f"DROP TABLE {self.table_name};")
        self.conn.commit()

    def get_result(self, identifier):
        """ 
        Selects the result of the job with the id passed and returns it 
        
        :param identifier: (str) Id of the job result
        :return: String result of job 
        """

        query = f"SELECT result FROM {self.table_name} " \
        f"WHERE id='{identifier}';"
        self.cur.execute(query)
        if self.cur.rowcount > 0:
            return self.cur.fetchone()[0]
        return None

    def get_all_results(self):
        """ 
        :return: Dictionary with job ids as keys and results as values
        """

        query = f"SELECT * FROM {self.table_name}"
        self.cur.execute(query)
        result_dict = {}
        for (name, result) in self.cur:
            result_dict[name] = result
        return result_dict

    def get_successful_runs(self):
        """ 
        :return: List of job ids which ran successfully
        """

        query = f"SELECT id FROM {self.table_name} " \
                "WHERE result='success';"
        self.cur.execute(query)
        return [name[0] for name in self.cur]

    def get_failed_runs(self):
        """
        :return: Dictionary with error types as keys and lists of job ids as values
        """

        query = f"SELECT id, result FROM {self.table_name} " \
                "WHERE result<>'success';"
        self.cur.execute(query)
        failures = dict([(key, []) for key in self.error_types])
        for (name, result) in self.cur:
            failures[result].append(name)
        return failures

    def delete_result(self, identifier):
        """ 
        Deletes job id and result from the database
        
        :param identifier: (str) Id of the job results
        """

        query = f"DELETE FROM {self.table_name} " \
                f"WHERE id='{identifier}';"
        self.cur.execute(query)
        self.conn.commit()

    def delete_all_results(self):
        """
        Deletes all entries in the database
        """

        self.cur.execute(f"DELETE FROM {self.table_name};")
        self.conn.commit()

    def ran_succesfully(self, identifier):
        """ 
        :param identifier: (str) Id of the job result 
        :return: Boolean on if job ran successfully
        """

        query = f"SELECT result FROM {self.table_name} " \
        f"WHERE id='{identifier}';"
        self.cur.execute(query)
        result = self.cur.fetchone()
        if result is not None:
            return result[0] == 'success'
        return False

    def count_results(self):
        """
        :return: Int number of jobs that have been run
        """

        self.cur.execute(f"SELECT COUNT(*) FROM {self.table_name};")
        return self.cur.fetchone()[0]

    def count_successes(self):
        """
        :return: Int number of jobs that have ran successfully
        """

        query = f"SELECT COUNT(*) FROM {self.table_name} " \
                "WHERE result='success';"
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def count_failures(self):
        """
        :return: Int number of jobs that have failed
        """

        query = f"SELECT COUNT(*) FROM {self.table_name} " \
                "WHERE result<>'success';"
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def insert_success(self, identifier):
        """
        Inserts a value into the table with a given id and the result 'success'
        
        :param identifier: (str) Id of the job result
        """

        query = f"INSERT INTO {self.table_name} " \
                f"VALUES ('{identifier}', 'success');"
        self.cur.execute(query)
        self.conn.commit()

    def insert_failure(self, identifier, error_type):
        """
        Inserts a value into the table with a given id and the result te given error type
        
        :param identifier: (str) Id of the job result
        :param error_type: (str) Erroneous result of the job, from the error_types list
        """
        
        query = f"INSERT INTO {self.table_name} " \
                f"VALUES ('{identifier}', '{error_type}');"
        self.cur.execute(query)
        self.conn.commit()

    def close(self):
        """
        Close connection with the database
        """

        self.cur.close()
        self.conn.close()
