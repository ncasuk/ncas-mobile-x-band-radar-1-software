import glob
import os
import functools
from .base_handler import BaseHandler
from convert import SETTINGS


class FileSystemHandler(BaseHandler):

    def __init__(self, n_facets, sep, error_types):
        """ 
        Constructs an instace of the file system handler.
        
        :param n_facets: (int) Number of directories used to define a job id
        :param sep: (str) Character used to separate facet names in a job id 
        :param error_types: (list) List of the string names of the types of errors that can occur.
        """

        # self.current_dir = os.getcwd()
        self.error_types = error_types
        self.n_facets = n_facets
        self.sep = sep
        # self.success_dir = SETTINGS.SUCCESS_DIR.format(current_directory=self.current_dir)
        # self.failure_dir = SETTINGS.FAILURE_DIR.format(current_directory=self.current_dir)
        self.success_dir = SETTINGS.SUCCESS_DIR
        self.failure_dir = SETTINGS.FAILURE_DIR

        
    def validate(func):
        """
        Decorator to check an identifier is of the correct format
        """

        @functools.wraps(func)
        def validate_identifier(*args, **kwargs):
            identifier = args[1] # Assumes identifier is second argument
            if os.sep in identifier:
                raise ValueError
            return func(*args, **kwargs)
        return validate_identifier

    def _path_to_identifier(self, path):
        """
        Given a full path to a result returns its job id
        
        :param path: (str) Path to result file
        :return: Job id
        """

        # Getting the last n_facets number of items in the path and joining
        # them to create the relative identifier
        path_arr = path.split(os.sep)
        identifier = self.sep.join(path_arr[-self.n_facets:])
        return identifier

    def _identifier_to_path(self, identifier, result):
        """
        Given an identifier and a result, return a full path to its result file
        
        :param identifier: (str) Id of the job result
        :param result: (str) Result of the job
        :return: Path to result file
        """

        id_path = identifier.replace(self.sep, os.sep)
        if result == 'success':
            return os.path.join(self.success_dir, id_path)
        else:
            return os.path.join(self.failure_dir, result, id_path)

    @validate
    def get_result(self, identifier):
        """ 
        Finds the result of the job with the id passed and returns it 
        
        :param identifier: (str) Id of the job result
        :return: String result of job 
        """

        path = self._identifier_to_path(identifier, 'success')
        if os.path.exists(path):
            return 'success'
        
        for error in self.error_types:
            path = self._identifier_to_path(identifier, error)
            if os.path.exists(path):
                return error

        return None

    def get_all_results(self):
        """ 
        :return: Dictionary with job ids as keys and results as values
        """

        results = {}
        for identifier in self.get_successful_runs():
            results[identifier] = 'success'

        error_dict = self.get_failed_runs()
        for (error_type, identifiers) in error_dict.items():
            for identifier in identifiers:
                results[identifier] = error_type

        return results

    def get_successful_runs(self):
        """ 
        :return: List of job ids which ran successfully
        """

        glob_pattern = os.path.join(self.success_dir, os.sep.join(['*' for _ in range(self.n_facets)]))
        files = glob.glob(glob_pattern)
        return [self._path_to_identifier(fname) for fname in files]


    def get_failed_runs(self):
        """
        :return: Dictionary with error types as keys and lists of job ids as values
        """

        failures = {}
        for error_type in self.error_types:
            glob_pattern = os.path.join(self.failure_dir, error_type, os.sep.join(['*' for _ in range(self.n_facets)]))
            files = glob.glob(glob_pattern)
            failures[error_type] = [self._path_to_identifier(fname) for fname in files]
        
        return failures

    @validate
    def delete_result(self, identifier):
        """ 
        Deletes result file from the file system given its identifier
        
        :param identifier: (str) Id of the job result
        """

        path = self._identifier_to_path(identifier, 'success')
        if os.path.exists(path):
            os.unlink(path)
        
        for error in self.error_types:
            path = self._identifier_to_path(identifier, error)
            if os.path.exists(path):
                os.unlink(path)

    def delete_all_results(self):
        """
        Deletes all result files in the file system
        """

        success_pattern = os.path.join(self.success_dir, os.sep.join(['*' for _ in range(self.n_facets)]))
        failure_pattern = os.path.join(self.failure_dir, os.sep.join(['*' for _ in range(self.n_facets + 1)])) # +1 to account for failure type
        success_files = glob.glob(success_pattern)
        failure_files = glob.glob(failure_pattern)

        for success_file in success_files:
            os.unlink(success_file)

        for failure_file in failure_files:
            os.unlink(failure_file)

    @validate
    def ran_succesfully(self, identifier):
        """ 
        :param identifier: (str) Id of the job result 
        :return: Boolean on if job ran successfully
        """

        path = self._identifier_to_path(identifier, 'success')
        return os.path.exists(path)

    def count_results(self):
        """
        :return: Int number of jobs that have been run
        """

        return len(self.get_all_results())

    def count_successes(self):
        """
        :return: Int number of jobs that have ran successfully
        """

        return len(self.get_successful_runs())

    def count_failures(self):
        """
        :return: Int number of jobs that have failed
        """

        size = 0
        error_dict = self.get_failed_runs()
        for error in error_dict.keys():
            size += len(error_dict[error])
        return size

    @validate
    def insert_success(self, identifier):
        """
        Creates a successful result file with the identifier passed
        
        :param identifier: (str) Id of the job result
        """

        path = self._identifier_to_path(identifier, 'success')
        dr = os.path.dirname(path)

        if not os.path.isdir(dr):
            os.makedirs(dr)
        open(path, 'w') #empty success file

    @validate
    def insert_failure(self, identifier, error_type):
        """
        Creates a result file using the identifier and error type passed
        
        :param identifier: (str) Id of the job result
        :param error_type: (str) Erroneous result of the job, from the error_types list
        """

        path = self._identifier_to_path(identifier, error_type)
        dr = os.path.dirname(path)

        if not os.path.isdir(dr):
            os.makedirs(dr)
        with open(path, 'w') as writer:
            writer.write(f'{error_type} has occured!')
