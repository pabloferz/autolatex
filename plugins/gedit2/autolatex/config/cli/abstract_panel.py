#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autolatex/config/cli/figure_assignment_panel.py
# Copyright (C) 2013  Stephane Galland <galland@arakhne.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

#---------------------------------
# IMPORTS
#---------------------------------

# Include the Glib, Gtk and Gedit libraries
from gi.repository import GObject, Gtk
# AutoLaTeX internal libs
from ...utils import utils
from ...widgets import inherit_button

#---------------------------------
# CLASS Panel
#---------------------------------

# Gtk panel that is managing the configuration of the figure assignments
class AbstractPanel(Gtk.Box):
	__gtype_name__ = "AutoLaTeXAbstractConfigurationPanel"

	def __init__(self, is_document_level, directory, window):
		# Use an intermediate GtkBox to be sure that
		# the child GtkGrid will not be expanded vertically
		Gtk.Box.__init__(self)
		self._is_document_level = is_document_level
		self._directory = directory
		self._window = window
		self._settings = None
		#
		# Create the grid for the panel
		#
		self.set_property('orientation', Gtk.Orientation.VERTICAL)
		self._grid = Gtk.Grid()
		self.pack_start(self._grid, False, False, 0)
		self._grid.set_row_homogeneous(False)
		self._grid.set_column_homogeneous(False)
		self._grid.set_row_spacing(5)
		self._grid.set_column_spacing(5)
		self._grid.set_property('margin', 5)
		self._grid.set_property('vexpand', False)
		self._grid.set_property('hexpand', True)
		self._grid_row = 0
		#
		# Create the panel's widgets
		#
		self._init_widgets()
		#
		# Initialize the content
		#
		self._init_content()
		#
		# Update the state of the widgets
		#
		self.update_widget_states()
		#
		# Connext the signals
		#
		self._connect_signals()

	def _init_widgets(self):
		"""Invoked to fill the given grid with the widgets"""
		raise NotImplementedError("Please implement this method")

	def _init_content(self):
		"""Invoked to initialize the values in the widgets"""
		raise NotImplementedError("Please implement this method")

	def _connect_signals(self):
		"""Invoked to connect methods to the widgets' signals"""
		raise NotImplementedError("Please implement this method")

	def update_widget_states(self):
		"""Invoked to change the states of the widgets"""
		raise NotImplementedError("Please implement this method")

	def save(self):
		"""Invoked when the changes in the panel must be saved"""
		raise NotImplementedError("Please implement this method")

	# Utility function that permits to change the sensitivity
	# of a widget according to a given flag and the "inheriting" flag
	def _update_sentitivity(self, widget, is_sensitive):
		inherit_flag = widget.get_data('autolatex_overriding_configuration_value')
		if inherit_flag:
			inherit_flag = inherit_flag()
			if inherit_flag:
				return inherit_flag.set_widget_sensitivity(is_sensitive)
		widget.set_sensitive(is_sensitive)
		return is_sensitive

	# Utility function that permits to change the overriding of a widget
	def _init_overriding(self, widget, is_overriding):
		inherit_flag = widget.get_data('autolatex_overriding_configuration_value')
		if inherit_flag:
			inherit_flag = inherit_flag()
			if inherit_flag:
				inherit_flag.set_overriding_value(is_overriding)

	# Utility function that permits to get the sensitivity
	# of a widget according to a given flag and the "inheriting" flag
	def _get_sentitivity(self, widget):
		inherit_flag = widget.get_data('autolatex_overriding_configuration_value')
		if inherit_flag:
			inherit_flag = inherit_flag()
			if inherit_flag:
				return inherit_flag.get_widget_sensitivity(widget)
		return widget.get_sensitive()

	# Utility function that permits to get the overriding
	# of a widget according to a given flag and the "inheriting" flag
	def _get_overriding(self, widget):
		inherit_flag = widget.get_data('autolatex_overriding_configuration_value')
		if inherit_flag:
			inherit_flag = inherit_flag()
			if inherit_flag:
				return inherit_flag.get_overriding_value()
		return True

	# Utility function that permits to read the settings.
	def _read_settings(self, section):
		self._settings = utils.backend_get_configuration(
			self._directory,
			'project' if self._is_document_level else 'user',
			section)
		self._settings_section = section

	# Utility function to extract a string value from the settings
	def _get_settings_str(self, key, default_value=None):
		if self._settings and self._settings.has_option(self._settings_section, key):
			return str(self._settings.get(self._settings_section, key))
		else:
			return default_value

	# Utility function to extract a boolean value from the settings
	def _get_settings_bool(self, key, default_value=None):
		if self._settings and self._settings.has_option(self._settings_section, key):
			return bool(self._settings.getboolean(self._settings_section, key))
		else:
			return default_value

	# Utility function to extract an inherited string value from the settings
	def _get_settings_str_inh(self, key, default_value=None):
		return self._get_settings_str(key+'_INHERITED', default_value)

	# Utility function to extract an inherited boolean value from the settings
	def _get_settings_bool_inh(self, key, default_value=None):
		return self._get_settings_bool(key+'_INHERITED', default_value)

	# Utility function to set a string value from the settings
	def _set_settings_str(self, key, value):
		if self._settings:
			if not value:
				value = utils.CONFIG_EMPTY_VALUE
			self._settings.set(self._settings_section, key, value)

	# Utility function to set a boolean value from the settings
	def _set_settings_bool(self, key, value):
		if self._settings:
			if value is None:
				value = utils.CONFIG_EMPTY_VALUE
			else:
				value = ('true' if value else 'false')
			self._settings.set(self._settings_section, key, value)

	# Utility function to reset a section in the settings
	def _reset_settings_section(self, section=None):
		if self._settings:
			if not section:
				section = self._settings_section
			self._settings.remove_section(section)
			self._settings.add_section(section)

	# Utility function to create a label
	def _create_label(self, text, hexpand=False):
		ui_label = Gtk.Label(text)
		ui_label.set_property('hexpand', hexpand)
		ui_label.set_property('vexpand', False)
		ui_label.set_property('halign', Gtk.Align.START)
		ui_label.set_property('valign', Gtk.Align.CENTER)
		return ui_label

	# Utility function to create a row in a grid
	def _insert_row(self, left_widget, right_widget=None, enable_inherit=True):
		if right_widget:
			self._grid.attach(	left_widget,
					0,self._grid_row,1,1) # left, top, width, height
			self._grid.attach(	right_widget, 
					1,self._grid_row,1,1) # left, top, width, height
		else:
			self._grid.attach(	left_widget, 
					0,self._grid_row,2,1) # left, top, width, height
		inheriting_widget = None
		if enable_inherit:
			height = 1
			if isinstance(enable_inherit, (int, long)) and int(enable_inherit)>1:
				height = int(enable_inherit)
			inheriting_widget = inherit_button.InheritButton(self, left_widget, right_widget)
			inheriting_widget.set_property('expand', False)
			inheriting_widget.set_property('halign', Gtk.Align.CENTER)
			inheriting_widget.set_property('valign', Gtk.Align.CENTER)
			self._grid.attach(	inheriting_widget, 
					2,self._grid_row,1,height) # left, top, width, height
		self._grid_row = self._grid_row + 1
		return [ left_widget, right_widget, inheriting_widget ]

	# Utility function to create a row in a grid
	def _create_row(self, label_text, right_widget, enable_inherit=True):
		ui_label = self._create_label(label_text)
		right_widget.set_property('hexpand', True)
		right_widget.set_property('vexpand', False)
		return self._insert_row(ui_label, right_widget, enable_inherit)

	# Utility function to create a row in a grid with a Switch
	def _create_switch(self, label_text, enable_inherit=True):
		widget = Gtk.Switch()
		tab = self._create_row(label_text, widget, enable_inherit)
		widget.set_property('hexpand', False)
		widget.set_property('vexpand', False)
		widget.set_property('halign', Gtk.Align.END)
		widget.set_property('valign', Gtk.Align.CENTER)
		return tab


	# Utility function to create a row in a grid with an Entry
	def _create_entry(self, label_text, enable_inherit=True):
		widget = Gtk.Entry()
		return self._create_row(label_text, widget, enable_inherit)


	# Utility function to create a row in a grid with a ComboText
	def _create_combo(self, label_text, values=None, combo_name=None, enable_inherit=True):
		widget = Gtk.ComboBoxText()
		if combo_name:
			widget.set_name(combo_name)
		if values:
			for value in values:
				widget.append_text(value)
		return self._create_row(label_text, widget, enable_inherit)


	# Utility function to create a scroll panel for the given widget
	def _create_scroll_for(self, widget, width=400, height=400):
		scroll = Gtk.ScrolledWindow()
		scroll.add(widget)
		scroll.set_size_request(width, height)
		scroll.set_policy(
			Gtk.PolicyType.AUTOMATIC,
			Gtk.PolicyType.AUTOMATIC)
		scroll.set_shadow_type(Gtk.ShadowType.IN)
		scroll.set_property('hexpand', True)
		scroll.set_property('vexpand', True)
		return scroll

