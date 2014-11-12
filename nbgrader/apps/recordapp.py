from IPython.config.loader import Config
from IPython.utils.traitlets import Unicode, List, Type, DottedObjectName
from nbgrader.apps.customnbconvertapp import CustomNbConvertApp
from nbgrader.apps.customnbconvertapp import aliases as base_aliases
from nbgrader.apps.customnbconvertapp import flags as base_flags
from nbgrader.preprocessors import FindStudentID, RecordGrades
from IPython.nbconvert.writers import WriterBase


aliases = {}
aliases.update(base_aliases)
aliases.update({
    'student-id': 'RecordApp.student_id',
    'regexp': 'FindStudentID.regexp',
    'assignment': 'RecordGrades.assignment_id',
})

flags = {}
flags.update(base_flags)
flags.update({
})

examples = """
nbgrader record assignment.ipynb
nbgrader record autograded/*.ipynb
"""


class NullWriter(WriterBase):
    def write(self, output, resources, **kw):
        pass


class RecordApp(CustomNbConvertApp):

    name = Unicode(u'nbgrader-record')
    description = Unicode(u'Record scores from a graded notebook in a database')
    aliases = aliases
    flags = flags
    examples = examples
    
    def init_writer(self):
        self._writer_class_changed(None, self.writer_class, self.writer_class)
        self.writer = NullWriter(parent=self)

    student_id = Unicode(u'', config=True)

    # The classes added here determine how configuration will be documented
    classes = List()

    def _classes_default(self):
        """This has to be in a method, for TerminalIPythonApp to be available."""
        classes = super(RecordApp, self)._classes_default()
        classes.extend([
            FindStudentID,
            RecordGrades
        ])
        return classes

    def _export_format_default(self):
        return 'notebook'

    def build_extra_config(self):
        self.extra_config = Config()
        self.extra_config.Exporter.preprocessors = [
            'nbgrader.preprocessors.FindStudentID',
            'nbgrader.preprocessors.RecordGrades'
        ]
        self.config.merge(self.extra_config)
