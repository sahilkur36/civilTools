import json

from PySide2 import QtCore

def save(json_file, widget):
	new_d = {}
	# comboboxes
	for key in (
		'ostan',
		'city',
		'risk_level',
		'soil_type',
		'importance_factor',
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.currentText()")
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		't_an_x',
		't_an_y',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.value()")
	# Checkboxes
	for key in (
		'top_story_for_height_checkbox',
		'infill',
		):
		if hasattr(widget, key):
			exec(f"new_d['{key}'] = widget.{key}.isChecked()")

	from building import RuTable
	system, lateral, i, n = get_treeview_item_prop(widget.x_treeview)
	new_d['x_system'] = [i, n]
	new_d['x_system_name'] = system
	new_d['x_lateral_name'] = lateral
	new_d['cdx'] = RuTable.Ru[system][lateral][2]
	system, lateral, i, n = get_treeview_item_prop(widget.y_treeview)
	new_d['y_system'] = [i, n]
	new_d['y_system_name'] = system
	new_d['y_lateral_name'] = lateral
	new_d['cdy'] = RuTable.Ru[system][lateral][2]
	d = {}
	if json_file.exists():
		with open(json_file, 'r', encoding='utf-8') as f:
			d = json.load(f)
	d.update(new_d)
	with open(json_file, 'w', encoding='utf-8') as f:
		json.dump(d, f)

def get_treeview_item_prop(view):
	indexes = view.selectedIndexes()
	if not len(indexes):
		return
	index = indexes[0]
	if index.isValid():
		data = index.internalPointer()._data
		if len(data) == 1:
			return
		lateral = data[0]
		lateral = lateral.split('-')[1]
		lateral = lateral.lstrip(' ')
		system = index.parent().data()
		system = system.split('-')[1]
		system = system.lstrip(' ')
		if hasattr(index, 'parent'):
			i = index.parent().row()
			n = index.row()
		return system, lateral, i, n
	
def save_analytical_periods(json_file, tx, ty):
	with open(json_file, 'r') as f:
		d = json.load(f)
	d['t_an_x'] = tx
	d['t_an_y'] = ty
	with open(json_file, 'w') as f:
		json.dump(d, f)

def get_analytical_periods(json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)
	tx = d.get('t_an_x', 2)
	ty = d.get('t_an_y', 2)
	return tx, ty

def save_cd(json_file, cdx, cdy):
	with open(json_file, 'r') as f:
		d = json.load(f)
	d['cdx'] = cdx
	d['cdy'] = cdy
	with open(json_file, 'w') as f:
		json.dump(d, f)

def get_cd(json_file):
	with open(json_file, 'r') as f:
		d = json.load(f)
	cdx = d.get('cdx')
	cdy = d.get('cdy')
	return cdx, cdy

def load(json_file, widget=None):
	d = {}
	if json_file.exists():
		with open(json_file, 'r', encoding='utf-8') as f:
			d = json.load(f)
	if widget is None:
		return d
	keys = d.keys()
	for key in (
		'ostan',
		'city',
		'risk_level',
		'soil_type',
		'importance_factor',
		'bot_x_combo',
		'top_x_combo',
		'top_story_for_height',
		):
		if key in keys and hasattr(widget, key):
			exec(f"index = widget.{key}.findText(d['{key}'])")
			exec(f"widget.{key}.setCurrentIndex(index)")
		elif key in ('ostan', 'city'):
			exec(f"index = widget.{key}.findText('قم')")
			exec(f"widget.{key}.setCurrentIndex(index)")

	# Checkboxes
	key = 'top_story_for_height_checkbox'
	if key in keys and hasattr(widget, key):
		checked = d.get(key, True)
		widget.top_story_for_height_checkbox.setChecked(checked)
		widget.top_story_for_height.setEnabled(checked)
	key = 'infill'
	if key in keys and hasattr(widget, key):
		widget.infill.setChecked(d[key])
	# Spinboxes
	for key in (
		'height_x',
		'no_of_story_x',
		't_an_x',
		't_an_y',
		):
		if key in keys and hasattr(widget, key):
			exec(f"widget.{key}.setValue(d['{key}'])")
	# TreeViewes
	x_item = d.get('x_system', [2, 1])
	y_item = d.get('y_system', [2, 1])
	select_treeview_item(widget.x_treeview, *x_item)
	select_treeview_item(widget.y_treeview, *y_item)
	return d

def select_treeview_item(view, i, n):
	root_index = view.model().index(i, 0, QtCore.QModelIndex())
	child_index = view.model().index(n, 0, root_index)
	view.clearSelection()
	view.setCurrentIndex(child_index)
	view.setExpanded(child_index, True)