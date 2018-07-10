import wx
import wx.grid as  gridlib
import logging

from carlib.database import TransactionManager, DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence import Model
from carlib.utils import generate_sql_statement
from carlib.virtualgrid import BufferedDataSource

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

test = "millions"


# test = ""


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
        if test == "millions":
            if sub_operation == "count":
                sql = "SELECT  count(*) FROM veritrade "
            else:
                sql = "SELECT  marca,modelo,version,CHASSISDATA FROM veritrade "
                sql = sql + "ORDER BY $o0,$o1,$o2,$o3 "
                sql = sql + "OFFSET " + str(c_constraints.offset) + " ROWS "
                sql = sql + "FETCH NEXT " + str(c_constraints.limit) + " ROWS ONLY"

                sql = generate_sql_statement(self.driver_id, sql, c_constraints, remove_unused=True)
        else:
            if sub_operation == "count":
                sql = "SELECT  count(*) FROM tb_carroceria "
            else:
                sql = "SELECT  f_carroceria,f_carroceriatext FROM tb_carroceria "  # where f_carroceriatext='CISTERNA'"
                sql = sql + "ORDER BY $o0,$o1   "
                sql = sql + "OFFSET " + str(c_constraints.offset) + " ROWS "
                sql = sql + "FETCH NEXT " + str(c_constraints.limit) + " ROWS ONLY"

                sql = generate_sql_statement(self.driver_id, sql, c_constraints, remove_unused=True)

        print(sql)
        return sql


class BufferedDataSourceImpl(BufferedDataSource):
    def __init__(self, driver, connect_values, buffer_size):
        BufferedDataSource.__init__(self, buffer_size)

        trx = TransactionManager(driver, connect_values)
        daoDelegate = DAODelegateTest()
        self.__dao = DatabasePersistence(trx, daoDelegate)

    def getNumberOfRecords(self, constraints):
        wait = wx.BusyCursor()

        records = self.__dao.fetch_records(constraints, raw_answers=True, sub_operation="count")

        del wait
        num_records = records[1][0]
        return num_records

    def fetchRecordsToBuffer(self, constraints):
        wait = wx.BusyCursor()
        print("Paso fetchRecords")
        records = self.__dao.fetch_records(constraints, raw_answers=True)
        del wait
        del records[0]
        return records


# ---------------------------------------------------------------------------

class VirtualTable(gridlib.PyGridTableBase):

    def __init__(self, log, bufferedDataSource, columns):
        gridlib.PyGridTableBase.__init__(self)

        self.__bufferedDataSource = bufferedDataSource
        self.log = log
        self.__columns = columns

    # This is all it takes to make a custom data table to plug into a
    # wxGrid.  There are many more methods that can be overridden, but
    # the ones shown below are the required ones.  This table simply
    # provides strings containing the row and column values.

    def GetNumberRows(self):
        return self.__bufferedDataSource.maxRows()

    def GetNumberCols(self):
        if test == "millions":
            return len(self.__columns)
        else:
            return 2

    def GetColLabelValue(self, col):
        return self.__columns[col]["colname"]

    def IsEmptyCell(self, row, col):
        return True

    def GetValue(self, row, col):
        # print(row)
        record = self.__bufferedDataSource.getRow(row)
        if record is not None:
            try:
                #if type(record[col]) == str or type(record[col]) == unicode:
                if type(record[col]) == str:
                        return record[col]
                else:
                    return str(record[col])
            except UnicodeEncodeError as ex:
                # print(row, col, record[col], type(record[col]))
                return "error"
        else:
            return None

    def SetValue(self, row, col, value):
        self.log.write('SetValue(%d, %d, "%s") ignored.\n' % (row, col, value))

    def DeleteRows(self, pos=0, numRows=1):
        print("Eliminando")
        return True


# ---------------------------------------------------------------------------


class VirtualGrid(gridlib.Grid):
    def __init__(self, parent, log, bufferedDataSource, setupData):
        gridlib.Grid.__init__(self, parent, -1)

        self.tableBase = VirtualTable(log, bufferedDataSource, setupData["columns"])

        self.__bufferedDataSource = bufferedDataSource
        self.__setupData = setupData

        self.__order_field_pos = []
        self.initSortOrder()

        self.Bind(wx.EVT_TIMER, self.OnTimeout)
        self.__timer = wx.Timer(self)

        self.Bind(wx.EVT_SCROLLWIN, self.OnScrollGrid)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # trap the column label's paint event:
        columnLabelWindow = self.GetGridColLabelWindow()
        columnLabelWindow.Bind(wx.EVT_PAINT, self.OnColumnHeaderPaint)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnGridLabelLeftClick)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.tableBase, True)

    def initSortOrder(self):
        if self.__setupData["order_fields"]:
            for i in range(len(self.__setupData["order_fields"])):
                self.__order_field_pos.append(self.__setupData["order_fields"][i]["field"])
                self.__bufferedDataSource.setOrderField(self.__setupData["order_fields"][i]["field"],
                                                        self.__setupData["order_fields"][i]["desc"])

    def OnColumnHeaderPaint(self, evt):
        w = self.GetGridColLabelWindow()
        dc = wx.PaintDC(w)

        # For each column, draw it's rectangle, it's column name,
        # and it's sort indicator, if appropriate
        for col in range(self.GetNumberCols()):
            self.drawColumnHeader(col, dc)

    def OnGridLabelLeftClick(self, evt):
        self.processSort(evt.GetCol())

    def processSort(self, gridCol=None):
        if gridCol is None:
            gridCol = self.GetGridCursorCol()

        col_id = self.__setupData["columns"][gridCol]["map"]
        order_field = next(
            (item for item in self.__setupData["order_fields"] if item.get("field") and item["field"] == col_id), None)

        print(order_field)
        descending = False
        if order_field:
            if not order_field["desc"]:
                descending = True
            elif order_field["desc"]:
                descending = None
            else:
                descending = False
            order_field["desc"] = descending
        else:
            self.__setupData["order_fields"].append({"field": col_id, "desc": False})
            self.__order_field_pos.append(col_id)
            print("==========>", self.__setupData["order_fields"])

        if order_field and descending is None:
            # update local order variables.
            self.__setupData["order_fields"].remove(order_field)
            self.__order_field_pos.remove(order_field["field"])
            self.__bufferedDataSource.clearOrderFields()
            for i in range(len(self.__setupData["order_fields"])):
                self.__bufferedDataSource.setOrderField(self.__setupData["order_fields"][i]["field"],
                                                        self.__setupData["order_fields"][i]["desc"])
        else:
            self.__bufferedDataSource.setOrderField(col_id, descending)

        # paint
        self.MakeCellVisible(0, 0)
        self.SetGridCursor(0, 0)

        # update the scrollbars and the displayed part of the grid
        self.AdjustScrollbars()
        self.ForceRefresh()

    def drawColumnHeader(self, column, dc):
        # https://groups.google.com/forum/#!topic/wxpython-users/EvqUc4iWLYI
        font = dc.GetFont()

        totColSize = -self.GetViewStart()[0] * self.GetScrollPixelsPerUnit()[0]  # Thanks Roger Binns
        for col in range(column):
            totColSize += self.GetColSize(col)

        dc.SetBrush(wx.Brush("WHEAT", wx.TRANSPARENT))
        dc.SetTextForeground(wx.BLACK)
        colSize = self.GetColSize(column)
        rect = (totColSize, 0, colSize, 32)
        print("Recvtangulo=", rect)
        dc.DrawRectangle(rect[0] - (column != 0 and 1 or 0), rect[1],
                         rect[2] + (column != 0 and 1 or 0), rect[3])

        print("pintado ", column)
        col = self.__setupData["columns"][column]["map"]
        order_field = next(
            (item for item in self.__setupData["order_fields"] if item.get("field") and item["field"] == col), None)
        print("pintado ", column, col, order_field)

        if order_field:
            font.SetWeight(wx.BOLD)
            # draw a triangle, pointed up or down, at the
            # top left of the column.
            left = rect[0] + 3
            top = rect[1] + 3
            dc.SetBrush(wx.Brush("WHEAT", wx.BRUSHSTYLE_SOLID))
            if not order_field["desc"]:
                dc.DrawPolygon([(left, top), (left + 6, top), (left + 3, top + 4)])
            else:
                dc.DrawPolygon([(left + 3, top), (left + 6, top + 4), (left, top + 4)])

            order_pos = self.__setupData["order_fields"].index(order_field) + 1
            dc.DrawText(str(order_pos), rect[0] + rect[2] - dc.GetFullTextExtent(str(order_pos))[0] - 3, top)
        else:
            font.SetWeight(wx.NORMAL)

        dc.SetFont(font)
        dc.DrawLabel("%s" % self.GetColLabelValue(column),
                     rect, wx.ALIGN_CENTER | wx.ALIGN_TOP)

    def OnTimeout(self, evt):
        print("Se apago")
        self.__bufferedDataSource.lockRead = False
        self.ForceRefresh()

    def OnKeyDown(self, evt):
        print("key down")
        if evt.KeyCode == wx.WXK_PAGEDOWN or evt.KeyCode == wx.WXK_PAGEUP:
            self.__bufferedDataSource.lockRead = True

            print("Arranco")
            self.__timer.Start(200, oneShot=wx.TIMER_ONE_SHOT)
        evt.Skip()

    def OnScrollGrid(self, evt):
        # print('BEGIN ONscroll Grid\n')
        print("Arranco")
        self.__timer.Start(200, oneShot=wx.TIMER_ONE_SHOT)

        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
        elif not self.__bufferedDataSource.lockRead:
            if self.GetNumberRows() == 0:
                return
            self.__bufferedDataSource.lockRead = True
        evt.Skip()


# ---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Huge (virtual) Table Demo", size=(640, 480))

        steps = 100
        if test == "millions":
            steps = 500
        bufferedDataSource = BufferedDataSourceImpl('mssql',
                                                    {'dsn': 'MSSQLServer', 'host': '192.168.0.2', 'port': '1433',
                                                     'user': 'sa', 'password': 'Melivane100',
                                                     'database': 'veritrade'}, steps)

        setup_data = {
            "model": {
                "marca": {"type": "str"},
                "modelo": {"type": "str"},
                "version": {"type": "str"},
                "CHASSISDATA": {"type": "str"}
            },
            "columns": [
                {"colname": "Marca", "map": "marca"},
                {"colname": "Modelo", "map": "modelo"},
                {"colname": "Version", "map": "version"},
                {"colname": "VIN", "map": "CHASSISDATA"}
            ],
            "order_fields": [
                {
                    "field": "marca",
                    "desc": True
                },
                {
                    "field": "version",
                    "desc": False
                }
            ]
        }

        setup_data_2 = {
            "model": {
                "f_carroceria": {"type": "str"},
                "f_carroceriatext": {"type": "str"}
            },
            "columns": [
                {"colname": "Carroceria", "map": "f_carroceria"},
                {"colname": "Descripcion", "map": "f_carroceriatext"}
            ],
            "order_fields": [
                {
                    "field": "f_carroceria",
                    "desc": False
                }
            ]
        }
        #        order_Fields_pos = ["field1", "field2"]

        if test == "millions":
            grid = VirtualGrid(self, log, bufferedDataSource, setup_data)
        else:
            grid = VirtualGrid(self, log, bufferedDataSource, setup_data_2)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # marca,modelo,version,CHASSISDATA

    app = wx.App()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

# ---------------------------------------------------------------------------
