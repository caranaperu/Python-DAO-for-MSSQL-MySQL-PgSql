import wx
import wx.core
from wx import *
from wx import DefaultPosition, DefaultSize, WANTS_CHARS, TE_PROCESS_TAB, DefaultValidator
from wx.lib.masked import TextCtrl




class EntryMixin():
    '''A Mixin that provides code common to all Entry classes. The common
    behaviour includes automatically selecting all contents upon receiving
    focus. The 'width' parameter specifies the control's width in terms of
    number of characters rather than pixels. The 'optional' parameter
    specifies if it's ok for there to be no text entered. There is a
    validate() method that can be called to test this. This mixin requires
    client classes to define the method SetTextSelection(self, start, end)
    to visually select text unless the underlying control already has a
    method called SetSelection() that does this. In other words, this is not
    necessary for any control derived from TextCtrl (which has such a
    method) but it is necessary for controls derived from ComboBox (where
    the equivalent method is called SetMark(), not SetSelection()).'''

    def __init__(self, width=15, optional=true):
        pass


class TextEntry(TextCtrl, EntryMixin):
    '''A TextCtrl that selects its contents upon receiving focus. The
    'width' parameter specifies the control's width in terms of number of
    characters rather than pixels. The 'optional' parameter specifies if
    it's ok for there to be no text entered. There is a validate() method
    that can be called to test this.'''

    def __init__(self, parent, id=-1, value='', pos=DefaultPosition, size=DefaultSize,
                 style=WANTS_CHARS | TE_PROCESS_TAB, validator=DefaultValidator, name=TextCtrlNameStr, width=15,
                 optional=true, like=none, trim=true, sethook=none, killfocushook=none):
        pass


class UpperTextEntry(TextEntry):
    '''A TextEntry that makes all input upper case.'''

    def __init__(self, parent, id=-1, value='', pos=DefaultPosition, size=DefaultSize,
                 style=WANTS_CHARS | TE_PROCESS_TAB, validator=DefaultValidator, name=TextCtrlNameStr, width=15,
                 optional=true, like=none, trim=true, sethook=none, killfocushook=none):
        pass


class NumEntry(TextEntry):
    '''A TextEntry for numbers.'''

    def __init__(self, parent, id=-1, value='', pos=DefaultPosition, size=DefaultSize,
                 style=WANTS_CHARS | TE_PROCESS_TAB, validator=none, name=TextCtrlNameStr, width=10, scale=10,
                 precision=0, optional=true):
        pass


class DateEntry(TextEntry):
    '''A TextEntry for dates.'''

    def __init__(self, parent, id=-1, value='', pos=DefaultPosition, size=DefaultSize,
                 style=WANTS_CHARS | TE_PROCESS_TAB, validator=none, name=TextCtrlNameStr, width=10, optional=true,
                 zeroes=false, sethook=none, killfocushook=none):
        pass


class UpperTextCodeEntry(UpperTextEntry, CodeEntryMixin):
    '''An UpperTextEntry for entering values from a code table in the database.
    There is a list of valid values that is built from a database record
    class for a code table. Auto-completion is performed for both names and
    codes (or just codes). When the control contains a valid, existing value
    from the list, pressing the up and down arrows will cycle through the
    list of valid values. The default style is similar to that of the other
    Entry controls defined here. The contents can be restricted to existing
    values or new values can be added at will by the user. It is similar to
    TextEntry in that WANTS_CHARS is in the default style and the text is
    selected when it receives focus. In other words, this is just like
    CodeEntry but using a TextCtrl rather than a ComboBox. This is useful as
    a Grid editor when screen real estate is precious and simplicity is
    needed to speed up data entry.'''

    def __init__(self, parent, tableclass, id=-1, value='', pos=DefaultPosition, size=DefaultSize,
                 style=WANTS_CHARS | TE_PROCESS_TAB, validator=DefaultValidator, name=TextCtrlNameStr, width=5,
                 modifiable=true, optional=true, sethook=none, display='name', filterf=none):
        pass


class EntryGridCellEditor(PyGridCellEditor):
    '''This is a generic wrapper for existing controls so they can be used
    as grid cell editors (e.g. NumEntry, DateEntry). Any built-in
    key-vetoing validators are automatically used. If the control has
    OnKillFocus(), it is called in EndEdit(). If the control has validate(),
    it is called to decide whether or not to save edits back to the table.'''

    def __init__(self, cls, hooks, **kwargs):
        '''Initialize this grid cell editor. cls is the class of the
        underlying control. hooks is a hash of callable hooks that can be
        supplied to provide arbitrary behaviour. The valid keys for the
        hooks hash are: 'beginhook' (called in BeginEdit), 'endhook' (called
        in EndEdit), 'resethook' (called in Reset) and 'validhook' (called
        in EndEdit as a validator). These callable hooks are called with
        this EntryGridCellEditor object as their only argument. kwargs
        contains the arguments to be passed to the control's constructor.'''
        PyGridCellEditor.__init__(self)
        self.cls = cls
        self.hooks = hooks
        self.kwargs = kwargs

    def Clone(self):
        '''Make a clone of this object.'''
        clone = EntryGridCellEditor(self.cls, **self.kwargs)

    def Create(self, parent, id, event_handler):
        '''Called to create the control.'''
        self.ctrl = self.cls(parent, id=id, **self.kwargs)
        self.SetControl(self.ctrl)
        if event_handler is not none:
            self.ctrl.PushEventHandler(event_handler)

    def BeginEdit(self, row, col, grid):
        '''Fetch the value from the table and prepare the control to begin
        editing. Set the focus to the edit control.'''
        self.ctrl.grid = grid
        self.ctrl.grid_cell_editor_row = none
        self.ctrl.grid_cell_editor_col = none
        self.initial_value = grid.GetTable().GetValue(row, col)
        self.ctrl.SetValue(self.initial_value)
        self.ctrl.grid_cell_editor_row = row
        self.ctrl.grid_cell_editor_col = col
        if self.hooks and 'beginhook' in self.hooks:
            self.hooks['beginhook'](self)
        if hasattr(self.ctrl, 'SetInsertionPointEnd'):
            self.ctrl.SetInsertionPointEnd()
        self.ctrl.SetFocus()

    def EndEdit(self, row, col, grid, oldVal=None):  # Note: oldVal (and ApplyEdit()) added in wxPython 2.9.0.1
        '''For versions of wxPython up to 2.8.12.1:
        Complete the editing of the cell. Returns true if the value has
        changed. If necessary, the control may be destroyed. Note that this
        is also called during SaveEditControlValue() which can be called
        at times other than when ending the grid cell edit.

        For versions of wxPython since 2.9.0.1:
        Verify that an edit has changed the value of the cell.
        If it hasn't, return None. If it has, return the string
        version of the new value.

        In either case:
        Call any endhook function and OnKillFocus() method and validhook.'''
        if self.hooks and 'endhook' in self.hooks:
            self.hooks['endhook'](self)
        self.ctrl.grid = none
        self.ctrl.grid_cell_editor_row = none
        self.ctrl.grid_cell_editor_col = none
        if hasattr(self.ctrl, 'OnKillFocus'):
            self.ctrl.OnKillFocus(none)
        validhook = self.hooks['validhook'] if self.hooks and 'validhook' in self.hooks else none
        valid = (not hasattr(self.ctrl, 'validate') or self.ctrl.validate()) and (not validhook or validhook(self))
        # Has the value changed?
        val = self.ctrl.GetValue()
        changed = val != self.initial_value
        # Handle wxPython up to 2.8.12.1
        if oldVal is None:
            if changed:
                if valid:
                    grid.GetTable().SetValue(row, col, val)
                else:
                    CallAfter(grid.SetGridCursor, row, col)
            return changed
        # Handle wxPython since 2.9.0.1
        else:
            if changed:
                if valid:
                    return val
                else:
                    CallAfter(grid.SetGridCursor, row, col)
            return none

    def ApplyEdit(self, row, col, grid):
        '''Apply the change accepted by EndEdit to the grid.
        This is only used by versions of wxPython from 2.9.0.1 onwards.
        For earlier versions, this is done inside EndEdit() above.'''
        val = self.ctrl.GetValue()
        grid.GetTable().SetValue(row, col, val)

    def Reset(self):
        '''Reset the value in the control back to its starting value.'''
        self.ctrl.SetValue(self.initial_value)
        if self.hooks and 'resethook' in self.hooks:
            self.hooks['resethook'](self)
        if hasattr(self.ctrl, 'SetInsertionPointEnd'):
            self.ctrl.SetInsertionPointEnd()


class DataTable(PyGridTableBase):
    '''A class representing a table of data for use with DataGrid.SetTable().'''

    def __init__(self, columns, data, rows=none):
        '''Initialise the data table. Columns is a list of dict object, each
        of which has the following entries:
        - 'header' (mandatory) which contains a string to use as the column header;
        - 'charwidth' (optional) which specifies the width of the column
           as a number of characters;
        - 'pixelwidth' (optional) which specifies the width of the column
           as a number of pixels;
        - 'editor' (mandatory) which contains the class of a data entry control;
        - 'beginhook' (optional) a callable to call in BeginEdit();
        - 'endhook' (optional) a callable to call in EndEdit();
        - 'validhook' (optional) a callable to call in EndEdit() as a validator;
        - 'resethook' (optional) a callable to call in Reset(); and
        - 'kwargs' which contains a dict containing any arguments to the
        passed to the data entry control's constructor.
        Data is the data itself in column-major form (i.e. it's a list of
        columns which are lists of individual cells in the column). I know
        that's not normal but it's the way that the data comes from the
        database records we're using.'''
        PyGridTableBase.__init__(self)
        self._set(columns, data, rows)
        self.deleting_rows = false

    def _set(self, columns, data, rows):
        '''Set the columns, rows and data. Called by self.__init__() and
        DataTable._set().'''
        # Check that all columns have the same number of cells (at least 1 row)
        maxrows = max([len(col) for col in data] + [1])
        for col in range(len(data)):
            numrows = len(data[col])
            if numrows < maxrows:
                data[col].extend(['' for i in range(maxrows - numrows)])
        # Store the table information
        self.columns = columns
        self.data = data
        self.rows = rows

    def GetNumberRows(self):
        '''Return the number of rows.'''
        rows = 0
        for r in range(len(self.data)):
            if len(self.data[r]) > rows:
                rows = len(self.data[r])
        return rows

    def GetNumberCols(self):
        '''Return the number of columns.'''
        return len(self.columns)

    def IsEmptyCell(self, row, col):
        '''Return whether or not the cell at the given row and column
        contains a value.'''
        try:
            return not self.data[col][row]
        except IndexError:
            return true

    def GetValue(self, row, col):
        '''Return the value in the cell at the given row and column.'''
        try:
            return self.data[col][row]
        except IndexError:
            return ''

    def SetValue(self, row, col, val):
        '''Store the value into the cell at the given row and column. If it
        fails because the row or col doesn't exist, new rows or columns will
        be added until it succeeds.'''
        # Add new columns until there are enough
        try:
            column = self.data[col]
        except IndexError:
            while len(self.data) <= col:
                self.data.append(['' for i in range(len(self.data[0]))])
            column = self.data[col]
            self.SetValue(row, col, val)
            msg = GridTableMessage(self, GRIDTABLE_NOTIFY_COLS_APPENDED, 1)
            self.GetView().ProcessTableMessage(msg)
        # Add new rows until there are enough
        try:
            column[row] = val
        except IndexError:
            for c in range(len(self.data)):
                self.data[c].append('')
            self.SetValue(row, col, val)
            msg = GridTableMessage(self, GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
            self.GetView().ProcessTableMessage(msg)

    def GetColLabelValue(self, col):
        '''Return the header string for the given column.'''
        return self.columns[col]['header']

    def GetRowLabelValue(self, row):
        '''Return the label string for the given row.'''
        return self.rows[row] if self.rows and len(self.rows) > row else PyGridTableBase.GetRowLabelValue(self, row)

    def GetTypeName(self, row, col):
        '''Return a 'type' name for the cell at the given row and column.
        This will be the name of the data entry control class following by
        the repr() version of the kwargs for this column. The appropriate
        cell editors are registering using these 'type' strings below in
        DataGrid.SetTable().'''
        return self.columns[col]['editor'].__name__ + repr(self.columns[col]['kwargs'])

    def CanGetValueAs(self, row, col, type_name):
        '''Return whether or not the 'type' name for the cell at the given
        row and column matches the given type_name.'''
        return type_name == self.GetTypeName(row, col)

    def CanSetValueAs(self, row, col, type_name):
        '''Return whether or not the 'type' name for the cell at the given
        row and column matches the given type_name.'''
        return self.CanGetValueAs(row, col, type_name)

    def DeleteRows(self, pos=0, numRows=1):
        '''Delete numRows rows starting with row pos.'''
        app.debugmsg('DataTable.DeleteRows(pos=%s, numRows=%s)' % (pos, numRows))
        self.deleting_rows = true
        for c in range(len(self.data)):
            self.data[c] = self.data[c][0:pos] + self.data[c][pos + numRows:]
        msg = GridTableMessage(self, GRIDTABLE_NOTIFY_ROWS_APPENDED, -numRows)
        self.GetView().ProcessTableMessage(msg)
        self.deleting_rows = false

    def Clone(self):
        '''Return a copy of self.'''
        data = [self.data[c][:] for c in range(len(self.data))]
        return DataTable(self.columns, data, self.rows)


def menuitem(menu, text, func, help='', id=-1):
    '''Append an item to the given menu with the given text, handler
    function, tooltip help text and id.'''
    item = menu.Append(id=id, text=text, help=help)
    app.mainframe.Bind(EVT_MENU, logerrors(func), item)


class DataGrid(Grid):
    '''A Grid class that automatically redefines cell editors and calls
    AutoSizeColumns whenever SetTable is called (unless column widths were
    manually specified in the DataTable). Can only be used with tables of
    class DataTable.'''

    def __init__(self, parent, id=-1, pos=DefaultPosition, size=DefaultSize, style=WANTS_CHARS, name='DataGrid'):
        '''Initialise this grid. Cell overflow is disabled. Editing is
        enabled. Scrolling is enabled. Row labels are suppressed. Margins
        are zero.'''
        Grid.__init__(self, parent, id, pos, size, style, name)
        self.SetDefaultCellOverflow(false)
        self.EnableEditing(true)
        self.EnableScrolling(true, true)
        self.SetRowLabelSize(0)
        self.SetMargins(0, 0)
        self.datatable = none
        self.Bind(EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)
        self.Bind(EVT_GRID_LABEL_RIGHT_CLICK, self.OnRightClick)

    def can_paste_grid(self):
        ''' Return whether or not there is a grid clipboard that is compatible with this grid.'''
        if (hasattr(app, 'grid_clipboard') or app.load_grid_clipboard()) and \
                app.grid_clipboard.GetNumberCols() == self.GetTable().GetNumberCols() and \
                [_['header'] for _ in app.grid_clipboard.columns] == [_['header'] for _ in self.GetTable().columns] and \
                app.grid_clipboard.rows == self.GetTable().rows:
            # Copy DataTable.columns in case app.grid_clipboard has been
            # loaded from disk which would mean that we only have the column
            # headers, not everything like editor classes and hook functions.
            app.grid_clipboard.columns = self.GetTable().columns
            return true
        return false

    @logerrors
    def OnRightClick(self, event):
        '''Handler for the EVT_GRID_CELL_RIGHT_CLICK event. Show popup menu.'''
        app.debugmsg('DataGrid.OnRightClick')
        menu = Menu()
        if self.GetTable().GetNumberRows() > 0 and self.GetGridCursorRow() >= 0:
            menuitem(menu, 'Delete Row (Ctrl-D)', self.OnDeleteRow, 'Delete the currently selected row')
        menuitem(menu, 'Insert Row (Ctrl-I)', self.OnInsertRow, 'Insert a row above the currently selected row')
        if self.GetTable().GetNumberRows() > 0:
            menuitem(menu, 'Erase All Rows (Ctrl-E)', self.OnEraseRows, 'Erase all rows')
        menuitem(menu, 'Copy Grid (Ctrl-F)', self.OnCopyGrid, 'Copy the entire grid into a special grid clipboard')
        if self.can_paste_grid():
            menuitem(menu, 'Paste Grid (Ctrl-G)', self.OnPasteGrid, 'Paste the special grid clipboard into the grid')
        app.mainframe.PopupMenu(menu)
        menu.Destroy()

    @logerrors
    def OnInsertRow(self, event=none):
        '''Handler for the EVT_MENU event for the insert row popup menu
        item. Insert a row above the currently selected row.'''
        app.debugmsg('DataGrid.OnInsertRow')
        table = self.GetTable()
        r = self.GetGridCursorRow()
        data = [table.data[c][:r] + [''] + table.data[c][r:] for c in range(len(table.data))]
        self.SetTable(DataTable(table.columns, data, table.rows))
        self.Refresh()

    @logerrors
    def OnDeleteRow(self, event=none):
        '''Handler for the EVT_MENU event for the delete row popup menu
        item. Delete the currently selected row.'''
        app.debugmsg('DataGrid.OnDeleteRow')
        table = self.GetTable()
        if table.GetNumberRows() > 1:
            table.DeleteRows(self.GetGridCursorRow())
            self.fix_grid_cursor()
        else:
            for i in range(table.GetNumberCols()):
                table.SetValue(0, i, '')
            self.Refresh()

    @logerrors
    def OnEraseRows(self, event=none):
        '''Handler for the EVT_MENU event for the erase all rows popup menu
        item. Delete all rows.'''
        app.debugmsg('DataGrid.OnEraseRows')
        self.SetGridCursor(0, 0)
        table = self.GetTable()
        while table.GetNumberRows() > 1:
            table.DeleteRows(0)
            self.fix_grid_cursor()
        for i in range(table.GetNumberCols()):
            table.SetValue(0, i, '')
        self.Refresh()

    def fix_grid_cursor(self):
        '''Set the cursor to be in a row that exists if it is not already the case.
        This is necessary after the last row is deleted for whatever reason.'''
        row, col = self.GetGridCursor()
        num_rows = self.GetNumberRows()
        if num_rows == 0 and row != 0:
            self.SetGridCursor(0, 0)
        elif row > num_rows - 1:
            self.SetGridCursor(num_rows - 1, col)

    @logerrors
    def OnCopyGrid(self, event=none):
        '''Handler for the EVT_MENU event for the copy grid popup menu item.
        Copy the entire grid into a special grid clipboard.'''
        app.debugmsg('DataGrid.OnCopyGrid')
        app.grid_clipboard = self.GetTable().Clone()
        app.save_grid_clipboard()

    @logerrors
    def OnPasteGrid(self, event=none):
        '''Handler for the EVT_MENU event for the paste grid popup menu
        item. Paste the special grid clipboard into the grid.'''
        app.debugmsg('DataGrid.OnPasteGrid')
        if not hasattr(app, 'grid_clipboard'):
            app.errormsg('There is nothing in the grid clipboard')
            return
        if app.grid_clipboard.GetNumberCols() != self.GetTable().GetNumberCols():
            app.errormsg('The grid clipboard has the wrong number of columns to paste here')
            return
        self.SetTable(app.grid_clipboard)

    def GetTable(self):
        '''Return the underlying DataTable object.'''
        return self.datatable()

    def GetGridCursor(self):
        '''Return the (row, col) tuple indicating the currently selected cell.'''
        return (self.GetGridCursorRow(), self.GetGridCursorCol())

    def SetTable(self, table, takeOwnership=false, selmode=Grid.SelectCells):
        '''Supply a DataTable object to this grid. Define cell editors based
        on the columns supplied to the DataTable object and recalculate
        column widths based on the data itself (or set column widths
        according to the DataTable). Note that, unlike Grid.SetTable(), this
        method can be called multiple times to reset the underlying data.
        However, takeOwnership and selmode are only used the first time that
        this method is called.'''
        if not self.datatable:
            Grid.SetTable(self, table, takeOwnership, selmode)
            import weakref
            self.datatable = weakref.ref(table)
        else:
            self.last_rows = self.GetTable().GetNumberRows()
            self.last_cols = self.GetTable().GetNumberCols()
        self._set(table)
        return true

    def _set(self, table):
        '''Replace the existing table (if any) with the data in this new
        DataTable object.'''
        # Set the cells
        if not hasattr(self, 'last_rows'):
            self.last_rows = table.GetNumberRows()
        if not hasattr(self, 'last_cols'):
            self.last_cols = table.GetNumberCols()
        next_rows = table.GetNumberRows()
        next_cols = table.GetNumberCols()
        cmds = [
            (self.last_rows, next_rows, GRIDTABLE_NOTIFY_ROWS_DELETED, GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self.last_cols, next_cols, GRIDTABLE_NOTIFY_COLS_DELETED, GRIDTABLE_NOTIFY_COLS_APPENDED)
        ]
        self.BeginBatch()
        for curr, new, delmsg, addmsg in cmds:
            if new < curr:
                self.ProcessTableMessage(GridTableMessage(self.GetTable(), delmsg, new, curr - new))
            elif new > curr:
                self.ProcessTableMessage(GridTableMessage(self.GetTable(), addmsg, new - curr))
        self.GetTable()._set(table.columns, table.data, table.rows)
        self.ProcessTableMessage(GridTableMessage(self.GetTable(), GRIDTABLE_REQUEST_VIEW_GET_VALUES))
        self.EndBatch()
        self.last_rows = next_rows
        self.last_cols = next_cols
        # Set the column editor types and widths
        for c in range(table.GetNumberCols()):
            type_name = table.GetTypeName(0, c)
            col = table.columns[c]
            hooks = dict(
                [(hook, col[hook]) for hook in ['beginhook', 'endhook', 'resethook', 'validhook'] if hook in col])
            self.RegisterDataType(type_name, GridCellStringRenderer(),
                                  EntryGridCellEditor(col['editor'], hooks=hooks, **col['kwargs']))
            if 'pixelwidth' in col:
                self.SetColSize(c, col['pixelwidth'])
            elif 'charwidth' in col:
                self.SetColSize(c, (col['charwidth'] + 1) * self.GetCharWidth())
            else:
                self.AutoSizeColumn(c, false)
        # Set the row label column width and alignment
        self.SetRowLabelSize(self.GetCharWidth() * (2 + max([len(r) for r in table.rows])) if table.rows else 0)
        self.SetRowLabelAlignment(ALIGN_LEFT, ALIGN_TOP)
        # Hacklet: On Windows, the scroll bars aren't resized
        # so fiddle with the window size to trigger it.
        # h, w = self.GetSize()
        # self.SetSize((h+1, w))
        # self.SetSize((h, w))
        # self.ForceRefresh()
        return true


class AutoEditGridMixin(GridAutoEditMixin):
    '''A mixin class for Grid subclasses that completes the task that
    GridAutoEditMixin is supposed to do. GridAutoEditMixin only makes
    editing start automatically when the user clicks on a cell with the
    mouse. Editing doesn't start automatically when the Grid control
    receives focus via Tab navigation or the SetFocus() method. Replacing
    GridAutoEditMixin with this mixin makes editing start in either case.
    Subclasses just need to call AutoEditGridMixin.__init__(). If the grid
    has an EVT_SET_FOCUS handler, make sure that it skips the event.'''

    def __init__(self):
        '''Initialise this mixin. Call GridAutoEditMixin.__init__() and set
        up a handler for the EVT_SET_FOCUS event.'''
        GridAutoEditMixin.__init__(self)
        self._about_to_enable = false
        self._ignore_focus = false
        self.Bind(EVT_SET_FOCUS, self._AutoEditGridMixin_OnSetFocus)

    @logerrors
    def _AutoEditGridMixin_OnSetFocus(self, event):
        '''Handler for the EVT_SET_FOCUS event. Automatically start editing
        when the user tabs to this grid or when the application calls
        SetFocus().'''
        debug_event('AutoEditGridMixin.OnSetFocus%s' % ('(ignored)' if self._ignore_focus else ''), event)
        if self._ignore_focus:
            return
        if not self._about_to_enable:
            self._about_to_enable = true
            CallAfter(self.SafeEnableCellEditControl, true)
        event.Skip()

    def StartIgnoringFocus(self):
        '''Start ignoring EVT_SET_FOCUS events. This is needed when the
        AutoEditGridMixin hogs the focus too much. For example, in the
        VarDataPage, when the focus is in the grid, clicking on the search
        ctrl only moves the focus there briefly and it returns to the grid.
        Also, when saving vardata, the code sends focus to the search ctrl
        programmatically but it doesn't work without saving twice. Having
        the code there stop ignoring focus here while it is setting the
        focus to where it wants it fixes the problem.'''
        self._ignore_focus = true

    def StopIgnoringFocus(self):
        '''Stop ignoring EVT_SET_FOCUS events.'''
        self._ignore_focus = false

    def SafeEnableCellEditControl(self, enable=true):
        '''Version of EnableCellEditControl that does nothing if the grid
        has already been destroyed by the time it is called.'''
        # This is only an issue during semi-automatic testing
        app.debugmsg('AutoEditGridMixin.SafeEnableCellEditControl(enable=%r)' % enable)
        if isinstance(self, Grid) and self.CanEnableCellControl():
            self.EnableCellEditControl(enable)
        self._about_to_enable = false


class HorizontalGridMixin():
    '''A mixin class for Grid subclasses that changes the behaviour of the
    Return key when editing a cell so that it selects the cell to the right
    rather than the cell below. If the current cell is the last cell in the
    row, the first cell of the next row is selected instead. If there is no
    next row, self.GetTable().SetValue() is called to trigger the creation
    of a new row. If the table is a DataTable object, this will work. For
    other table classes, it probably won't. Alt-Return will select the cell
    to the left (or the rightmost cell in the next row up).'''

    def __init__(self):
        '''Initialise this mixin. Set up a handler for the EVT_KEY_DOWN event.'''
        self.Bind(EVT_KEY_DOWN, self._HorizontalGridMixin_OnKeyDown)

    @logerrors
    def _HorizontalGridMixin_OnKeyDown(self, event):
        '''Handler for the EVT_KEY_DOWN event. Only consumes Return keys.'''
        debug_event('HorizontalGridMixin.OnKeyDown', event)
        # Bail out unless the key is either Return or Shift-Return
        if not event.GetKeyCode() in [WXK_RETURN, WXK_NUMPAD_ENTER] or not (
                event.GetModifiers() in [0, MOD_ALT, MOD_SHIFT, MOD_ALT | MOD_SHIFT]):
            event.Skip()
            return
        # Stop editing the current cell
        self.DisableCellEditControl()
        if event.AltDown():
            # Move to the left (if there is a cell to the left)
            if not self.MoveCursorLeft(event.ShiftDown()):
                # Otherwise, move to the right-most cell in the previous row
                prev_row = self.GetGridCursorRow() - 1
                if prev_row >= 0:
                    table = self.GetTable()
                    rightmost_col = table.GetNumberCols() - 1
                    self.SetGridCursor(prev_row, rightmost_col)
                    self.MakeCellVisible(prev_row, rightmost_col)
        else:
            # Move to the right (if there is a cell to the right)
            if not self.MoveCursorRight(event.ShiftDown()):
                # Otherwise, move to the left-most cell in the next row down
                next_row = self.GetGridCursorRow() + 1
                table = self.GetTable()
                # If there is no next row, create one first by calling SetValue()
                # for the new cell (assumes that DataTable is used).
                if next_row >= table.GetNumberRows():
                    table.SetValue(next_row, 0, '')
                self.SetGridCursor(next_row, 0)
                self.MakeCellVisible(next_row, 0)


class FastDataGrid(AutoEditGridMixin, HorizontalGridMixin, DataGrid):
    '''A DataGrid class that automatically starts editing cells when they
    are selected. When Return is pressed while editing a cell, the editing
    stops, and the next row to the right is selected and editing commences
    again. When the right-most end of the row is reached, Return moves to
    the left-most cell in the next row. If there is no next row, a new row
    is created and editing continues.'''

    def __init__(self, parent, id=-1, pos=DefaultPosition, size=DefaultSize, style=WANTS_CHARS, name='DataGrid'):
        '''Initialise this grid. Just calls all the __init__ methods for the
        parent classes.'''
        DataGrid.__init__(self, parent, id, pos, size, style, name)
        AutoEditGridMixin.__init__(self)
        HorizontalGridMixin.__init__(self)

    # Example of creating a grid

    self.grid_columns = [
        dict(header='Per', charwidth=3, editor=IntEntry, kwargs=dict(name='period', width=3, optional=false),
             endhook=self.endhook_period),
        dict(header='Element', charwidth=15, editor=UpperTextCodeEntry,
             kwargs=dict(name='element', tableclass=T_element, width=15, modifiable=false, display='code',
                         filterf=self.filterf_award_element), endhook=self.endhook_element),
        dict(header='Typ', charwidth=3, editor=UpperTextCodeEntry,
             kwargs=dict(name='input_type', tableclass=T_input_type, width=3, modifiable=false, display='code',
                         optional=false), beginhook=self.beginhook_input_type),
        dict(header='Units', charwidth=11, editor=NumEntry, kwargs=dict(name='element_units', precision=4),
             endhook=self.endhook_units),
        dict(header='Cash', charwidth=11, editor=NumEntry, kwargs=dict(name='element_cash', precision=2)),
        dict(header='P', charwidth=2, editor=UpperTextEntry, kwargs=dict(name='element_predetermined_flag', width=2),
             endhook=self.endhook_predetermined_flag, validhook=self.validhook_predetermined_flag),
        dict(header='Costing', charwidth=15, editor=UpperTextCodeEntry,
             kwargs=dict(name='cost_centre', tableclass=T_cost_centre, width=15, display='code'),
             beginhook=self.beginhook_cost_centre),
    ]
    self.grid_data = blank_data(1, len(self.grid_columns))
    self.grid_datatable = DataTable(self.grid_columns, self.grid_data)
    # Sum charwidths plus 1 for each column plus 2 for good measure :)
    chars = sum([col['charwidth'] for col in self.grid_columns]) + len(self.grid_columns) + 2
    self.grid_ctrl_resizer = ResizeWidget(self)
    self.grid_ctrl = tabbed(FastDataGrid(self.grid_ctrl_resizer, size=(self.GetCharWidth() * chars, 200), name='grid'))
    self.grid_ctrl.SetTable(self.grid_datatable)
