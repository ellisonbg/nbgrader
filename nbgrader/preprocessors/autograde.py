from IPython.nbconvert.preprocessors import Preprocessor
from IPython.utils.traitlets import Unicode, Integer
from nbgrader import utils
from nbgrader.api import Gradebook


class AutoGrade(Preprocessor):
    """Preprocessor for saving out the autograder grades into a MongoDB"""

    def _add_score(self, cell, resources):
        """Graders can override the autograder grades, and may need to
        manually grade written solutions anyway. This function adds
        score information to the database if it doesn't exist. It does
        NOT override the 'score' field, as this is the manual score
        that might have been provided by a grader.

        """
        points = float(cell.metadata['nbgrader']['points'])

        # If it's a code cell and it threw an error, then they get
        # zero points, otherwise they get max_score points. If it's a
        # text cell, we can't autograde it.
        if cell.cell_type == 'code':
            autoscore = points
            for output in cell.outputs:
                if output.output_type == 'pyerr':
                    autoscore = 0.0
                    break
            self.log.info('grade_id: %s = %r/%r' % \
                (cell.metadata['nbgrader']['grade_id'], autoscore, points))
        else:
            autoscore = 0.0
        cell.metadata['nbgrader']['autoscore']=autoscore
        cell.metadata['nbgrader']['score']=autoscore

    def _fix_metadat(self, cell, resources):
        """Fix problematic metadata."""
        if 'grader_id' in cell.metadata['nbgrader']:
            del cell.metadata['nbgrader']['grader_id']
        if isinstance(cell.metadata['nbgrader']['points'], (str, unicode)):
            old = cell.metadata['nbgrader']['points']
            cell.metadata['nbgrader']['points'] = float(old)

    def preprocess_cell(self, cell, resources, cell_index):
        # if it's a grade cell, the add a grade
        if utils.is_grade(cell):
            self._fix_metadat(cell, resources)
            self._add_score(cell, resources)

        return cell, resources
