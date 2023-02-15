# import sys
# from pathlib import Path

# from PySide2 import  QtWidgets
# import FreeCADGui as Gui
# import civiltools_rc

# civiltools_path = Path(__file__).absolute().parent.parent.parent


# class Form(QtWidgets.QWidget):
#     def __init__(self, etabs_model):
#         super(Form, self).__init__()
#         self.form = Gui.PySideUic.loadUi(str(civiltools_path / 'widgets' / 'tools' / 'offset.ui'))
#         unit = etabs_model.get_current_unit()[1]
#         self.form.distance.setSuffix(f' {unit}')
#         self.etabs = etabs_model

#     def accept(self):
#         distance = self.form.distance.value()
#         neg = self.form.negative.isChecked()
#         self.etabs.frame_obj.offset_frame(distance, neg)

#     def reject(self):
#         Gui.Control.closeDialog()
from PySide2.QtWidgets import  QMessageBox

def expand_load_sets(etabs):
    ret = etabs.area.expand_uniform_load_sets_and_apply_to_model()
    if ret:
        QMessageBox.information(None, 'Successful', 'All load sets expanded successfully.')
    else:
        QMessageBox.warning(None, 'Failed', "Load sets did not expanded!")

