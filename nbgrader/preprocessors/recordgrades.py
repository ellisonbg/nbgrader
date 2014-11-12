from IPython.nbconvert.preprocessors import Preprocessor
from IPython.utils.traitlets import Unicode, Integer
from nbgrader import utils
from nbgrader.api import Gradebook
import numpy as np


class RecordGrades(Preprocessor):
    """Preprocessor for saving out the autograder grades into a MongoDB"""

    db_name = Unicode("gradebook", config=True, help="Database name")
    db_host = Unicode("localhost", config=True, help="Hostname for the database")
    db_port = Integer(27017, config=True, help="Port for the database",allow_none=True)

    assignment_id = Unicode(u'assignment', config=True, help="Assignment ID")

    def preprocess(self, nb, resources):
        # connect to the mongo database
        self.gradebook = Gradebook(self.db_name, host=self.db_host, port=self.db_port)
        self.student = self.gradebook.find_student(
            student_id=resources['nbgrader']['student_id'])
        self.assignment = self.gradebook.find_assignment(
            assignment_id=self.assignment_id)
        self.notebook = self.gradebook.find_or_create_notebook(
            notebook_id=resources['unique_key'],
            student=self.student,
            assignment=self.assignment)

        # process the cells
        nb, resources = super(RecordGrades, self).preprocess(nb, resources)

        return nb, resources

    def _add_score(self, cell, resources):
        """Graders can override the autograder grades, and may need to
        manually grade written solutions anyway. This function adds
        score information to the database if it doesn't exist. It does
        NOT override the 'score' field, as this is the manual score
        that might have been provided by a grader.

        """
        # these are the fields by which we will identify the score
        # information
        grade = self.gradebook.find_or_create_grade(
            notebook=self.notebook,
            grade_id=cell.metadata['nbgrader']['grade_id'])

        grade.max_score = float(cell.metadata['nbgrader'].get('points', np.nan))
        grade.score = float(cell.metadata['nbgrader'].get('score', np.nan))
        grade.autoscore = float(cell.metadata['nbgrader'].get('autoscore', np.nan))
        self.log.info('grade_id=%s; points=%r; autoscore=%r; score=%r;' % \
                (cell.metadata['nbgrader']['grade_id'], grade.max_score,
                 grade.autoscore, grade.score))
        self.gradebook.update_grade(grade)

    def preprocess_cell(self, cell, resources, cell_index):
        # if it's a grade cell, the add a grade
        if utils.is_grade(cell):
            self._add_score(cell, resources)

        return cell, resources
