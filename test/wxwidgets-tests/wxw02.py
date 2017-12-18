import wx
import wx.grid

colLabels = ("First", "Last")
rowLabels = ("line1", "line2", "line3")
mylist0 = [("bob", "dernier"), ("mike", "max"), ("John", "Paul")]
mylist1 = [("Geoff", "Alan"), ("Fred", "Robin"), ("Pat", "Nat")]
data = mylist0


class LineupTable(wx.grid.PyGridTableBase):
    def __init__(self, entries, rowLabels=None, colLabels=None):
        wx.grid.PyGridTableBase.__init__(self)
        self.entries = entries
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        # we need to store the row length and column length to
        # see if the table has changed size
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberRows(self):
        return len(self.entries)

    def GetNumberCols(self):
        return len(self.colLabels)

    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]

    def GetRowLabelValue(self, row):  # col):
        if self.rowLabels:
            return self.rowLabels[row]

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        entry = self.entries[row][col]
        print"GetValue = ", entry
        return self.entries[row][col]

    def SetValue(self, row, col, value):
        print "row = ", row, " col = ", col, " value = ", value

    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(),
             wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(),
             wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = wx.grid.GridTableMessage(self, delmsg, new, current - new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self, addmsg, new - current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # update the column rendering plugins
        # self._updateColAttrs(grid)

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wx.grid.GridTableMessage(self,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)


class SimpleGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.tableBase = LineupTable(data, rowLabels, colLabels)
        self.SetTable(self.tableBase, True)
        self.ForceRefresh()

    def ResetTable(self, table):
        self.tableBase = LineupTable(table, rowLabels, colLabels)
        self.SetTable(self.tableBase, True)

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self.tableBase.ResetView(self)
        self.tableBase.UpdateValues(self)


class TestFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "A Grid", size=(375, 375))
        p = wx.Panel(self, -1)
        self.grid = SimpleGrid(p)

        mychoice = None
        sample = [u"choice: mylist0", u"choice: mylist1"]
        self.mycombo = wx.ComboBox(p, wx.NewId(), value=u"", choices=sample)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.subSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.subSizer.Add(self.mycombo)
        sizer.Add(self.subSizer, 50, wx.EXPAND | wx.TOP, border=10)
        sizer.Add(self.grid, 100, wx.EXPAND | wx.TOP, border=10)
        p.SetSizer(sizer)
        p.Fit()
        self.Centre()

    def OnSelect(self, event):
        mychoice = event.GetSelection()
        if mychoice == 0:
            newData = mylist0
        elif mychoice == 1:
            newData = mylist1
        self.grid.tableBase.entries = newData
        #        self.grid.ResetTable(newData)
        self.grid.Reset()
        self.grid.ForceRefresh()
        print self.grid.tableBase.entries


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = TestFrame(None)
    frame.Show(True)
    app.MainLoop()