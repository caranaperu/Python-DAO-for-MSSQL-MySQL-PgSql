import time
import wx
import wx.grid as  gridlib

import mem_profile
from carlib.database import TransactionManager, DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence import Model, Constraints

test = "millions"
# test = ""
myTableBase = None


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
            if sub_operation == "last":
                sql = "SELECT  * FROM( "
                sql = sql + "SELECT  TOP " + str(
                    c_constraints.limit) + " marca,modelo,version,CHASSISDATA FROM veritrade "
                sql = sql + "ORDER BY marca desc,modelo desc,version desc,CHASSISDATA desc"
                sql = sql + " )x  ORDER BY marca,modelo,version,CHASSISDATA"
            elif sub_operation == "count":
                sql = "SELECT  count(*) FROM veritrade "
            else:
                sql = "SELECT  marca,modelo,version,CHASSISDATA FROM veritrade "
                sql = sql + "ORDER BY marca,modelo,version,CHASSISDATA "
                sql = sql + "OFFSET " + str(c_constraints.offset) + " ROWS "
                sql = sql + "FETCH NEXT " + str(c_constraints.limit) + " ROWS ONLY"
        else:
            if sub_operation == "count":
                sql = "SELECT  count(*) FROM tb_carroceria "
            else:
                sql = "SELECT  f_carroceria,f_carroceriatext FROM tb_carroceria "  # where f_carroceriatext='CISTERNA'"
                sql = sql + "ORDER BY f_carroceria  "
                sql = sql + "OFFSET " + str(c_constraints.offset) + " ROWS "
                sql = sql + "FETCH NEXT " + str(c_constraints.limit) + " ROWS ONLY"

        print (sql)
        return sql


class BufferedDataSource(object):
    def __init__(self, driver, connect_values, buffer_size):
        trx = TransactionManager(driver, connect_values)
        daoDelegate = DAODelegateTest()
        self.__dao = DatabasePersistence(trx, daoDelegate)
        #self.__ispending = False
        #self.__topRow = None
        # self.__endRow = None
        self.__bufferSize = buffer_size
        self.__records = None
        self.constraint = Constraints()
        self.totalRows = None
        self.__lastRow = None
        self.__lastTopRow = None
        self.__lastEndRow = None
        self.constraint.offset = 0
        self.constraint.limit = buffer_size

    def maxRows(self):
        if self.totalRows is None:
            # self.totalRows = 100000000
            records = self.__dao.fetch_records(self.constraint, raw_answers=True, sub_operation="count")
        self.totalRows = records[1][0]
        return self.totalRows

    def getRow(self, row, onThumb=False):
        # memb = mem_profile.memory_usage_psutil()
        # print ('Memory (Before): {}Mb'.format(memb))
        # t1 = time.clock()

        offset = (self.__bufferSize / 2) * (row // (self.__bufferSize / 2) - 1)
        if offset < 0:
            offset = 0
        self.constraint.offset = offset

        if self.__lastRow is None:
            self.__lastRow = 0

        # print("row= ",row)
        if not myTableBase.GetView().scrollLock:
            if row >= self.__lastEndRow or row < self.__lastTopRow:
                print("HAY QUE LERRRRRRRRRRRRRRR , row= ", row)
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True,
                                                          record_type_classname=AutosModel)
                del self.__records[0]

                self.__lastTopRow = offset
                self.__lastEndRow = offset + self.constraint.limit
        elif (row >= self.__lastEndRow or row < self.__lastTopRow) and abs(row - self.__lastRow) > self.__bufferSize:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> eliminando registros ", row)
            if len(self.__records) > 0:
                self.__records = []
        self.__lastRow = row

        # t2 = time.clock()
        # memf = mem_profile.memory_usage_psutil()
        # print ('Memory (After) : {}Mb'.format(memf))
        # print ('Diff {} mem'.format(memf - memb))
        # print ('Diff {} mem'.format(1024 * (memf - memb)))
        # print ('Took {} Seconds'.format(t2 - t1))

        if len(self.__records) > 0:
            try:
                return self.__records[row - self.__lastTopRow]
            except IndexError as ex:
                print("ERROR = ", row)
                return None


# ---------------------------------------------------------------------------

class HugeTable(gridlib.PyGridTableBase):

    def __init__(self, log):
        gridlib.PyGridTableBase.__init__(self)

        steps = 100
        if test == "millions":
            steps = 500

        self.__bufferedDataSource = BufferedDataSource('mssql',
                                                       {'dsn': 'MSSQLServer', 'host': '192.168.0.5', 'port': '1433',
                                                        'user': 'sa', 'password': 'Melivane100',
                                                        'database': 'veritrade'}, steps)
        self.log = log
        self.odd = gridlib.GridCellAttr()
        self.odd.SetBackgroundColour("sky blue")
        self.even = gridlib.GridCellAttr()
        self.even.SetBackgroundColour("sea green")

    def GetAttr(self, row, col, kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    # This is all it takes to make a custom data table to plug into a
    # wxGrid.  There are many more methods that can be overridden, but
    # the ones shown below are the required ones.  This table simply
    # provides strings containing the row and column values.

    def GetNumberRows(self):
        return self.__bufferedDataSource.maxRows()

    def GetNumberCols(self):
        if test == "millions":
            return 4
        else:
            return 2

    def IsEmptyCell(self, row, col):
        return True

    def GetValue(self, row, col):
        record = self.__bufferedDataSource.getRow(row)
        if record is not None:
            try:
                if type(record[col]) == str or type(record[col]) == unicode:
                    return record[col]
                else:
                    return str(record[col])
            except UnicodeEncodeError as ex:
                print(row, col, record[col], type(record[col]))
            return "eroor"
        else:
            return None

    def SetValue(self, row, col, value):
        self.log.write('SetValue(%d, %d, "%s") ignored.\n' % (row, col, value))

    def DeleteRows(self, pos=0, numRows=1):
        print("Eliminando")
        return True


# ---------------------------------------------------------------------------


class HugeTableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        global myTableBase
        gridlib.Grid.__init__(self, parent, -1)

        self.tableBase = HugeTable(log)
        myTableBase = self.tableBase
        t2 = time.clock()
        self.scrollLock = False

        self.Bind(wx.EVT_TIMER, self.OnTimeout)
        self.__timer = wx.Timer(self)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.tableBase, True)

        self.Bind(wx.EVT_SCROLLWIN, self.OnScrollGrid)
        self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnBeginScroll)
        # self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnEndScroll)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # self.Bind(wx.EVT_KEY_UP,self.OnKeyUp)
        # self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)


    def OnTimeout(self, evt):
        print("Se apago")
        self.scrollLock = False
        self.ForceRefresh()

    def OnKeyDown(self, evt):
        print("key down")
        if evt.KeyCode == wx.WXK_PAGEDOWN or evt.KeyCode == wx.WXK_PAGEUP:
            self.scrollLock = True
            print("Arranco")
            self.__timer.Start(200, oneShot=wx.TIMER_ONE_SHOT)

            # if evt.KeyCode == wx.WXK_PAGEDOWN:
            #    print("PGDN")
            # if evt.KeyCode == wx.WXK_PAGEUP:
            #    print("PGUP")

        evt.Skip()

    def OnScrollGrid(self, evt):
        # print('BEGIN ONscroll Grid\n')

        # if not self.__timer.IsRunning():
        print("Arranco")
        self.__timer.Start(200, oneShot=wx.TIMER_ONE_SHOT)

        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
        elif not self.scrollLock:
            evt.Skip()
        return

    def OnBeginScroll(self, evt):
        # print('BEGIN scroll thumb\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
            return
        if self.GetNumberRows() == 0:
            return
        self.scrollLock = True
        evt.Skip()


# ---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Huge (virtual) Table Demo", size=(640, 480))
        grid = HugeTableGrid(self, log)

        # grid.SetReadOnly(5, 5, True)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    app = wx.App()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

# ---------------------------------------------------------------------------
