
class BaseHandler(object):
    """ Ineterface class to define base methods for a result handler
    class which deals with the output of job results """

    def get_result(self, identifier):
        """ Returns a result given its identifier """
        raise NotImplementedError

    def get_all_results(self):
        """ Returns a dictionary of all ensembles 
        and their respective result """
        raise NotImplementedError

    def get_successful_runs(self):
        """ Returns a list of the names of all 
        successful runs """
        raise NotImplementedError

    def get_failed_runs(self):
        """ Returns a dictionary of error types and
        lists of jobs which result in them """
        raise NotImplementedError

    def delete_result(self, identifier):
        """ Deletes a result given its identifier """
        raise NotImplementedError

    def delete_all_results(self):
        """ Deletes all results """
        raise NotImplementedError

    def ran_succesfully(self, identifier):
        """ Returns true / false on whether the result with this
        identifier is successful """
        raise NotImplementedError

    def count_results(self):
        """ Returns the number of results """
        raise NotImplementedError

    def count_successes(self):
        """ Returns the number of successful results """
        raise NotImplementedError

    def count_failures(self):
        """ Returns the number of failed results """
        raise NotImplementedError

    def insert_success(self, identifier):
        """ Adds a successful result """
        raise NotImplementedError

    def insert_failure(self, identifier, error_type):
        """ Adds a failed result """
        raise NotImplementedError

    def close(self):
        """ Optional method for implementations that
        need to close a conection (e.g a database). 
        Runs 'pass' by default """
        pass
