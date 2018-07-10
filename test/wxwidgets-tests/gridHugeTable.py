from __future__ import print_function
import time
import wx
import wx.grid as  gridlib

import mem_profile
from carlib.database import TransactionManager, DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence import Model, Constraints
from carlib.utils import dbutils


class AutosModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.marca = None
        self.modelo = None
        self.version = None

    # retornar None si no se desea chequeo de version
    def get_pk_fields(self):
        return None


class DAODelegateTest(MsSQLBaseDelegate):
    def __init__(self):
        MsSQLBaseDelegate.__init__(self)

    def get_fetch_records_query(self, c_constraints=None, sub_operation=None):
        sql = "SELECT marca,modelo,version,CHASSISDATA FROM veritrade "
        sql = sql+"ORDER BY marca,modelo,version,CHASSISDATA "
        sql = sql +"OFFSET "+str(c_constraints.offset)+" ROWS "
        sql = sql +"FETCH NEXT "+str(c_constraints.limit) +" ROWS ONLY"
        print (sql)
        return sql


# ---------------------------------------------------------------------------

class HugeTable(gridlib.PyGridTableBase):

    def __init__(self, log):
        gridlib.PyGridTableBase.__init__(self)

        self.constraint = Constraints()
        self.dao = self.init_db()
        self.records = None

        # self.topRow = 0
        self.NumberBufferRows = 100
        self.log = log
        self.curPage = 0
        # self._rows = self.GetNumberRows()
        self.visibleRows = None

        self.odd = gridlib.GridCellAttr()
        self.odd.SetBackgroundColour("sky blue")
        self.even = gridlib.GridCellAttr()
        self.even.SetBackgroundColour("sea green")

    @staticmethod
    def init_db():
        trx = TransactionManager('mssql', {'dsn': 'MSSQLServer', 'host': '192.168.0.2', 'port': '1433',
                                           'user': 'sa', 'password': 'Melivane100', 'database': 'veritrade'})

        daoDelegate = DAODelegateTest()
        return DatabasePersistence(trx, daoDelegate)

    def GetAttr(self, row, col, kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    # This is all it takes to make a custom data table to plug into a
    # wxGrid.  There are many more methods that can be overridden, but
    # the ones shown below are the required ones.  This table simply
    # provides strings containing the row and column values.

    def GetNumberRows(self):
        return 100

    def GetNumberCols(self):
        return 4

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        #  memb = mem_profile.memory_usage_psutil()
        #  print ('Memory (Before): {}Mb'.format(memb))
        #  t1 = time.clock()

        if self.records is None:
            self.constraint.offset = 0
            self.constraint.limit = 100
            self.records = self.dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)
            self.column_names = self.records[0]

            del self.records[0]
            # self.topRow = 0
            self.curPage = 1

            self.lastProcesedRow = 0
            self.latsProcesedCol = 0

        visibleRows = 0
        while not self.GetView().IsVisible(visibleRows, col, False):
            visibleRows = visibleRows + 1

        visibleTop = visibleRows
        while self.GetView().IsVisible(visibleRows, col, False):
            visibleRows = visibleRows + 1

        visibleRows = visibleRows - visibleTop
        #print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", visibleRows)

        #if row - self.lastProcesedRow < 0:
        #    print("Para Atras")
        #elif row - self.lastProcesedRow > 0:
        #    print("Para Adelante")


        if row == 0 and col == 0 and (self.lastProcesedRow == row and self.latsProcesedCol != col):
            print(self.constraint.offset)
            if self.constraint.offset > 0:
                self.constraint.offset = self.constraint.offset-50
                self.constraint.limit = self.constraint.limit - 50
                self.curPage = self.curPage - 1

                print(self.constraint.offset, self.constraint.limit)

                del self.records

                self.records = self.dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)
                del self.records[0]

                self.visibleRows = visibleRows
                """reset the view based on the data in the table.  Call
                this when rows are added or destroyed"""
                self.ResetView(self.GetView(),True)
                #self.UpdateValues()

                self.lastProcesedRow = 1
                self.latsProcesedCol = col
        elif row == 99 and col == 0 and (self.lastProcesedRow == row and self.latsProcesedCol != col):
            self.constraint.offset =  self.curPage * 50
            self.constraint.limit = 100  + self.curPage * 50
            self.curPage = self.curPage + 1
            print(self.constraint.offset, self.constraint.limit)

            del self.records

            self.records = self.dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)
            del self.records[0]

            self.visibleRows = visibleRows
            #self.GetView().Reset()
            """reset the view based on the data in the table.  Call
            this when rows are added or destroyed"""
            self.ResetView(self.GetView(),False)
            #self.UpdateValues()

            self.GetView().ForceRefresh()
            self.lastProcesedRow = row
            self.latsProcesedCol = col
        else:
            self.lastProcesedRow = row
            self.latsProcesedCol = col
            #print(row)
            return (str(self.records[row][col]))
            #print("****", self.lastProcesedRow, self.latsProcesedCol)

            #   t2 = time.clock()
            #   memf = mem_profile.memory_usage_psutil()
            #   print ('Memory (After) : {}Mb'.format(memf))
            #   print ('Diff {} mem'.format(memf - memb))
            #   print ('Diff {} mem'.format(1024 * (memf - memb)))
            #   print ('Took {} Seconds'.format(t2 - t1))


    def SetValue(self, row, col, value):
        self.log.write('SetValue(%d, %d, "%s") ignored.\n' % (row, col, value))

    def ResetView(self, grid, isTop):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        # msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, 50)
        # grid.ProcessTableMessage(msg)

        # msg = wx.grid.GridTableMessage(self,  wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 50)
        # grid.ProcessTableMessage(msg)
        self.UpdateValues(grid)

        grid.EndBatch()

        # self._rows = self.GetNumberRows()
        # self._cols = self.GetNumberCols()

        # update the column rendering plugins
        # self._updateColAttrs(grid)
        if not isTop:
            if (50 - self.visibleRows > 0):
                grid.MakeCellVisible(50 - self.visibleRows, 0)
            else:
                grid.MakeCellVisible(50, 0)
            grid.SetGridCursor(49, 0)
        else:
            grid.MakeCellVisible(1, 0)
            grid.SetGridCursor(0, 0)

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh()

    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wx.grid.GridTableMessage(self,
                                       wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

    # def DeleteRows(self, pos = 0, numRows = 1):
    #     del self.records[pos:pos+numRows]


# ---------------------------------------------------------------------------


class HugeTableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        #visibleRows = None
        gridlib.Grid.__init__(self, parent, -1)

        memb = mem_profile.memory_usage_psutil()
        print ('Memory (Before): {}Mb'.format(memb))
        t1 = time.clock()
        self.tableBase = HugeTable(log)
        t2 = time.clock()

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.tableBase, True)

        memf = mem_profile.memory_usage_psutil()
        print ('Memory (After) : {}Mb'.format(memf))
        print ('Diff {} mem'.format(memf - memb))
        print ('Diff {} mem'.format(1024 * (memf - memb)))
        print ('Took {} Seconds'.format(t2 - t1))

        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self.tableBase.ResetView(self)
        self.tableBase.UpdateValues(self)

    def OnRightDown(self, event):
        print("hello")
        print(self.GetSelectedRows())


# ---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Huge (virtual) Table Demo", size=(640, 480))
        #grid = HugeTableGrid(self, log)

        # grid.SetReadOnly(5, 5, True)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    app = wx.App()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

# ---------------------------------------------------------------------------
