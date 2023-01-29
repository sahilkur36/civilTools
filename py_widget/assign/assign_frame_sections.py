from pathlib import Path

from PySide2 import  QtWidgets
import FreeCADGui as Gui
import civiltools_rc

civiltools_path = Path(__file__).absolute().parent.parent.parent


class Form(QtWidgets.QWidget):
    def __init__(self, etabs_model):
        super(Form, self).__init__()
        self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'assign' / 'assign_frame_sections.ui'))
        self.etabs = etabs_model
        self.fill_stories()
        self.beam_names = self.etabs.frame_obj.concrete_section_names('Beam')
        self.column_names = self.etabs.frame_obj.concrete_section_names('Column')
        self.other_names = self.etabs.frame_obj.other_sections(self.beam_names + self.column_names)
        self.fill_sections()
        self.create_connections()

    def fill_stories(self):
        stories = self.etabs.SapModel.Story.GetNameList()[1]
        self.form.stories.addItems(stories)
        self.select_all_stories()

    def fill_sections(self):
        self.form.sections.clear()
        if self.form.all_sections.isChecked():
            self.form.sections.addItems(self.other_names)
        elif self.form.beams.isChecked():
            self.form.sections.addItems(self.beam_names)
        elif self.form.columns.isChecked():
            self.form.sections.addItems(self.column_names)

    def select_all_stories(self):
        for i in range(self.form.stories.count()):
            item = self.form.stories.item(i)
            item.setSelected(True)

    def create_connections(self):
        self.form.all_sections.clicked.connect(self.fill_sections)
        self.form.beams.clicked.connect(self.fill_sections)
        self.form.columns.clicked.connect(self.fill_sections)
        self.form.filter_line.textChanged.connect(self.filter_sections)

    def filter_sections(self):
        text = self.form.filter_line.text()
        for i in range(self.form.sections.count()):
            item = self.form.sections.item(i)
            item.setHidden(not (item.text().__contains__(text)))

    def accept(self):
        self.etabs.unlock_model()
        stories = [item.text() for item in self.form.stories.selectedItems()]
        sec_name = self.form.sections.currentItem().text()
        sec_type = 'other'
        if self.form.beams.isChecked():
            sec_type = 'beam'
        elif self.form.columns.isChecked():
            sec_type = 'column'
        self.etabs.frame_obj.assign_sections_stories(
            sec_name = sec_name,
            stories = stories,
            frame_names = None,
            sec_type = sec_type,
            )

    def reject(self):
        Gui.Control.closeDialog()
