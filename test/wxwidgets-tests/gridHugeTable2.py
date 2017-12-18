import time
import wx
import wx.grid as  gridlib

import mem_profile
from carlib.database import TransactionManager, DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence import Model, Constraints
from carlib.utils import dbutils

test = "millions"
#test = ""
myTableBase= None

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
                sql = sql + "SELECT  TOP "+str(c_constraints.limit)+ " marca,modelo,version,CHASSISDATA FROM veritrade "
                sql = sql + "ORDER BY marca desc,modelo desc,version desc,CHASSISDATA desc"
                sql = sql + " )x  ORDER BY marca,modelo,version,CHASSISDATA"
            elif sub_operation == "count":
                sql = "SELECT  count(*) FROM veritrade "
            else:
                sql = "SELECT  marca,modelo,version,CHASSISDATA FROM veritrade "
                sql = sql+"ORDER BY marca,modelo,version,CHASSISDATA "
                sql = sql +"OFFSET "+str(c_constraints.offset)+" ROWS "
                sql = sql +"FETCH NEXT "+str(c_constraints.limit) +" ROWS ONLY"
        else:
            sql = "SELECT  f_carroceria,f_carroceriatext FROM tb_carroceria " # where f_carroceriatext='CISTERNA'"
            sql = sql+"ORDER BY f_carroceria  "
            sql = sql +"OFFSET "+str(c_constraints.offset)+" ROWS "
            sql = sql +"FETCH NEXT "+str(c_constraints.limit) +" ROWS ONLY"

        print (sql)
        return sql

class BufferedDataSource(object):
    def __init__(self, driver, connect_values, buffer_size):
        trx = TransactionManager(driver, connect_values)
        daoDelegate = DAODelegateTest()
        self.__dao = DatabasePersistence(trx, daoDelegate)
        self.__ispending = False
        self.__topRow = None
        self.__endRow = None
        self.__bufferSize = buffer_size
        self.__records = None
        self.constraint = Constraints()
        self.totalRows = None
        self.__lastRow = None
        self.__lastTopRow = None
        self.__lastEndRow = None
        self.constraint.limit = buffer_size




    def maxRows(self):
        if self.totalRows is None:
            #self.totalRows = 100000000
            records = self.__dao.fetch_records(self.constraint, raw_answers=True,sub_operation="count")
        self.totalRows = records[1][0]
        return self.totalRows

    def getRow(self, row, onThumb = False):
        #memb = mem_profile.memory_usage_psutil()
        #print ('Memory (Before): {}Mb'.format(memb))
        #t1 = time.clock()



        #print("+++> LASTTOPROW=", self.__lastTopRow," ROW= ",row, " LASTENDROW= ", self.__lastEndRow)

        offset = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)
        if offset < 0:
            offset = 0
        #endRow = offset+self.__bufferSize
        topRow = offset
        self.constraint.offset = offset
        #self.constraint.limit = self.__bufferSize

        #print("+++> OFFSET=", self.constraint.offset, " LIMIT= ", self.constraint.limit," ROW= ",row)


        #if self.__lastRow is None:
        #    self.__lastRow = 0


        if row >= self.__lastEndRow or row < self.__lastTopRow:
            if myTableBase.GetView().scrollLock is True:
                print("ON SCROOLLOCK")
            else:
                print("OFF SCROOLLOCK")

            #print("ROW=",row," OFFSET2= ",offset," TOPROW= ",topRow," ENDROW=",endRow," SCROLLLOCK=",myTableBase.GetView().scrollLock)
            #print("LASTTOPROW=",self.__lastTopRow," LASTENDROW= ",self.__lastEndRow)
            print("HAY QUE LERRRRRRRRRRRRRRR")
            #self.constraint.offset = offset
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)
            del self.__records[0]

            self.__lastTopRow = topRow
            self.__lastEndRow = topRow + self.constraint.limit

        ##self.__lastRow = row
        #self.__lastTopRow = topRow
        #self.__lastEndRow = topRow+self.constraint.limit



        #t2 = time.clock()
        #memf = mem_profile.memory_usage_psutil()
        #print ('Memory (After) : {}Mb'.format(memf))
        #print ('Diff {} mem'.format(memf - memb))
        #print ('Diff {} mem'.format(1024 * (memf - memb)))
        #print ('Took {} Seconds'.format(t2 - t1))

        if len(self.__records) > 0:
            return self.__records[row-topRow]

    def getRowwwwww(self, row, onThumb = False):
        #memb = mem_profile.memory_usage_psutil()
        #print ('Memory (Before): {}Mb'.format(memb))
        #t1 = time.clock()

        self.constraint.limit = self.__bufferSize
        curPage = row//self.__bufferSize
        topRow = curPage*(self.__bufferSize/2)
        offset = topRow
        offset2 = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)
        endRow = topRow+self.__bufferSize

        offset2 = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)
        if offset2 < 0:
            offset2 = endRow-self.__bufferSize
        endRow = offset2+self.__bufferSize
        topRow = offset2

        print("ROW=",row," OFFSET2= ",offset2," TOPROW= ",topRow," ENDROW=",endRow," LASTROW= ",self.__lastRow,"  SCROLLLOCK=",myTableBase.GetView().scrollLock)

        if self.__lastRow is not None:
            if abs(row-self.__lastRow) > self.__bufferSize:
                print("Leeerrrrrrrrrrrrrrrrrrrrrr")
            elif self.__lastRow > endRow or self.__lastRow < topRow:
                print("Leeerrrrrrrrrrrrrrrrrrrrrr NORMAL")
        else:
            self.__lastRow = 0

        if row >= self.__lastEndRow or row < self.__lastTopRow:
            print("HAY QUE LERRRRRRRRRRRRRRR")
        self.__lastRow = row
        self.__lastTopRow = topRow
        self.__lastEndRow = endRow

        if self.__topRow is None:
            self.constraint.offset = 0
            if self.__bufferSize > self.totalRows:
                self.__bufferSize = self.totalRows

            self.__topRow = 0
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

            del self.__records[0]
            self.__endRow = len(self.__records)

        elif row < self.__topRow:
            self.constraint.offset = self.__topRow - self.__bufferSize/2
            if self.constraint.offset < 0:
                self.constraint.offset = 0
            self.__topRow = self.constraint.offset
            print(">>>>>>>>>>>>>>>>>>>>>> ",row-self.__endRow, " scrolllock >> ",myTableBase.GetView().scrollLock)
            if not myTableBase.GetView().scrollLock:
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)
            else:
                self.__records = []
                self.__endRow = self.__topRow + self.__bufferSize

            print(row, self.__topRow, self.__endRow)

        elif row >= self.__endRow:
            self.constraint.offset = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)

            self.__topRow = self.constraint.offset
            print(">>>>>>>>>>>>>>>>>>>>>> ",row-self.__endRow, " scrolllock >> ",myTableBase.GetView().scrollLock)
            if not myTableBase.GetView().scrollLock:
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)
            else:
                self.__records = []
                self.__endRow = self.__topRow + self.__bufferSize

            print(row, self.__topRow, self.__endRow, len(self.__records))

        else:
            if myTableBase.GetView().scrollLock == False and len(self.__records) == 0:
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX >>>>>",row, " ofsset= ",self.constraint.offset)
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)


        #t2 = time.clock()
        #memf = mem_profile.memory_usage_psutil()
        #print ('Memory (After) : {}Mb'.format(memf))
        #print ('Diff {} mem'.format(memf - memb))
        #print ('Diff {} mem'.format(1024 * (memf - memb)))
        #print ('Took {} Seconds'.format(t2 - t1))

        if row-self.__topRow >= 0 and len(self.__records) > 0:
            return self.__records[row-self.__lastTopRow]

    def getRow_old2(self, row, onThumb = False):
        #memb = mem_profile.memory_usage_psutil()
        #print ('Memory (Before): {}Mb'.format(memb))
        #t1 = time.clock()
        totRows = 1000000000
        #print("--------------------------- ROW= ",row)
        if self.__topRow is None:
            self.constraint.offset = 0
            self.constraint.limit = self.__bufferSize+1
            self.__topRow = 0
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

            del self.__records[0]
            self.__endRow = len(self.__records)

            print(row, self.__topRow, self.__endRow, len(self.__records))

            print("len records = ",len(self.__records)," totRows debe ser = ",self.__topRow+len(self.__records))
            if len(self.__records) <= self.__bufferSize:
                print("**************************************** PAso")
                totRows = self.__topRow+len(self.__records)
            else:
                del self.__records[-1]
                self.__endRow = self.__endRow-1


        elif row < self.__topRow:
            self.constraint.offset = self.__topRow - self.__bufferSize/2
            if self.constraint.offset < 0:
                self.constraint.offset = 0
            self.constraint.limit = self.__bufferSize+1
            self.__topRow = self.constraint.offset
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

            del self.__records[0]
            self.__endRow = self.__topRow + len(self.__records)
            print(row, self.__topRow, self.__endRow)

        elif row >= self.__endRow and row < self.totalRows:
            self.constraint.offset = self.__topRow + self.__bufferSize/2
            self.constraint.offset = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)

            self.constraint.limit  = self.__bufferSize+1
            self.__topRow = self.constraint.offset
            print(">>>>>>>>>>>>>>>>>>>>>> ",row-self.__endRow)
            if row-self.__endRow <= self.__bufferSize:
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)

                print(row, self.__topRow, self.__endRow, len(self.__records))

                print("len records = ",len(self.__records)," totRows debe ser = ",self.__topRow+len(self.__records))
                if len(self.__records) <= self.__bufferSize:
                    print("**************************************** PAso")
                    totRows = self.__topRow+len(self.__records)
                else:
                    del self.__records[-1]
                    self.__endRow = self.__endRow-1
            else:
                self.constraint.offset = (self.__bufferSize / 2) * (row // (self.__bufferSize / 2) - 1)

                self.__topRow = self.constraint.offset
                self.__endRow = self.__topRow + self.__bufferSize
                totRows = self.__endRow
                print("ROW=",row," TOPROW=",self.__topRow," ENROW=",self.__endRow," TOTROWS=",totRows)
                self.__ispending = True
        else:
            #print("SUBPASO SC=",myTableBase.GetView().scrollLock," PENDING=",self.__ispending)
            if row < self.__endRow and row < self.totalRows and myTableBase.GetView().scrollLock == False and self.__ispending:
                print("PASOOOOOOOOO ",self.constraint.offset," -- ",self.__endRow)
                self.__ispending = False
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)
                if len(self.__records) == 1:
                    print("NO hay REGISTROS")
                    self.constraint.limit = self.__bufferSize
                    self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel,sub_operation="last")

                if len(self.__records) > 0 :
                    del self.__records[0]
                    record = self.__records[-1]




        #print("totrows=",self.totalRows," ccccccc ",self.__endRow)

        if row >= self.__endRow:
            print("----PASO XXXXXXXXXXXXXXXXXXXXXXUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
            if row >= totRows and self.totalRows != self.__endRow:
                print("PASO XXXXXXXXXXXXXXXXNokia XXXXXXUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
                self.totalRows = totRows
                myTableBase.GetView().BeginBatch()

                msg = wx.grid.GridTableMessage(myTableBase, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, self.totalRows, 1000000-self.totalRows)
                myTableBase.GetView().ProcessTableMessage(msg)

                msg = wx.grid.GridTableMessage(myTableBase,wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
                myTableBase.GetView().ProcessTableMessage(msg)

                myTableBase.GetView().EndBatch()
                myTableBase.GetView().ForceRefresh()
                print(row, self.__topRow, self.__endRow, len(self.__records))
            return
        #t2 = time.clock()
        #memf = mem_profile.memory_usage_psutil()
        #print ('Memory (After) : {}Mb'.format(memf))
        #print ('Diff {} mem'.format(memf - memb))
        #print ('Diff {} mem'.format(1024 * (memf - memb)))
        #print ('Took {} Seconds'.format(t2 - t1))

        #print(row-self.__topRow)
        #xrow = ["aaa","bbbbb","ccccc","ddddd"]
        #try:
        #    xrow =  self.__records[row-self.__topRow]
        #except Exception as ex:
        #    print("****** ",row - self.__topRow)
        #return xrow
        #print("------------------- ",row,self.__topRow,row-self.__topRow,self.__records[row-self.__topRow][0])
        if row-self.__topRow >= 0 and len(self.__records) > 0:
            return self.__records[row-self.__topRow]


    def getRow_old(self, row, onThumb = False):
        #memb = mem_profile.memory_usage_psutil()
        #print ('Memory (Before): {}Mb'.format(memb))
        #t1 = time.clock()
        totRows = 1000000000

        if self.__topRow is None:
            self.constraint.offset = 0
            self.constraint.limit = self.__bufferSize+1
            self.__topRow = 0
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

            del self.__records[0]
            self.__endRow = len(self.__records)

            print(row, self.__topRow, self.__endRow, len(self.__records))

            print("len records = ",len(self.__records)," totRows debe ser = ",self.__topRow+len(self.__records))
            if len(self.__records) <= self.__bufferSize:
                print("**************************************** PAso")
                totRows = self.__topRow+len(self.__records)
            else:
                del self.__records[-1]
                self.__endRow = self.__endRow-1


        elif row < self.__topRow:
            self.constraint.offset = self.__topRow - self.__bufferSize/2
            if self.constraint.offset < 0:
                self.constraint.offset = 0
            self.constraint.limit = self.__bufferSize+1
            self.__topRow = self.constraint.offset
            self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

            del self.__records[0]
            self.__endRow = self.__topRow + len(self.__records)
            print(row, self.__topRow, self.__endRow)

        elif row >= self.__endRow and row < self.totalRows:
            self.constraint.offset = self.__topRow + self.__bufferSize/2
            self.constraint.offset = (self.__bufferSize/2)*(row//(self.__bufferSize/2)-1)

            self.constraint.limit  = self.__bufferSize+1
            self.__topRow = self.constraint.offset
            print(">>>>>>>>>>>>>>>>>>>>>> ",row-self.__endRow, " scrolllock >> ",myTableBase.GetView().scrollLock)
            if not myTableBase.GetView().scrollLock:
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)
            else:
                #del self.__records
                self.__records = []
                self.__endRow = self.__topRow + self.__bufferSize

            print(row, self.__topRow, self.__endRow, len(self.__records))

            print("len records = ",len(self.__records)," totRows debe ser = ",self.__topRow+len(self.__records))
            if len(self.__records) <= self.__bufferSize:
                print("**************************************** PAso")
                totRows = self.__topRow+len(self.__records)
            else:
                if not myTableBase.GetView().scrollLock:
                    del self.__records[-1]
                self.__endRow = self.__endRow-1
        else:
            if myTableBase.GetView().scrollLock == False and len(self.__records) == 0:
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX >>>>>",row, " ofsset= ",self.constraint.offset)
                self.__records = self.__dao.fetch_records(self.constraint, raw_answers=True, record_type_classname=AutosModel)

                del self.__records[0]
                self.__endRow = self.__topRow + len(self.__records)

        #print("totrows=",self.totalRows," ccccccc ",self.__endRow)

        if row >= self.__endRow:
            print("----PASO XXXXXXXXXXXXXXXXXXXXXXUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
            if row >= totRows and self.totalRows != self.__endRow:
                print("PASO XXXXXXXXXXXXXXXXNokia XXXXXXUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
                self.totalRows = totRows
                myTableBase.GetView().BeginBatch()

                msg = wx.grid.GridTableMessage(myTableBase, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, self.totalRows, 1000000-self.totalRows)
                myTableBase.GetView().ProcessTableMessage(msg)

                msg = wx.grid.GridTableMessage(myTableBase,wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
                myTableBase.GetView().ProcessTableMessage(msg)

                myTableBase.GetView().EndBatch()
                myTableBase.GetView().ForceRefresh()
                print(row, self.__topRow, self.__endRow, len(self.__records))
            return
        #t2 = time.clock()
        #memf = mem_profile.memory_usage_psutil()
        #print ('Memory (After) : {}Mb'.format(memf))
        #print ('Diff {} mem'.format(memf - memb))
        #print ('Diff {} mem'.format(1024 * (memf - memb)))
        #print ('Took {} Seconds'.format(t2 - t1))

        #print(row-self.__topRow)
        #xrow = ["aaa","bbbbb","ccccc","ddddd"]
        #try:
        #    xrow =  self.__records[row-self.__topRow]
        #except Exception as ex:
        #    print("****** ",row - self.__topRow)
        #return xrow
        #print("------------------- ",row,self.__topRow,row-self.__topRow,self.__records[row-self.__topRow][0])
        if row-self.__topRow >= 0 and len(self.__records) > 0:
            return self.__records[row-self.__topRow]

# ---------------------------------------------------------------------------

class HugeTable(gridlib.PyGridTableBase):

    def __init__(self, log):
        gridlib.PyGridTableBase.__init__(self)

        self.__bufferedDataSource = BufferedDataSource('mssql', {'dsn': 'MSSQLServer', 'host': '192.168.0.5', 'port': '1433',
                                           'user': 'sa', 'password': 'Melivane100', 'database': 'veritrade'},500)
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
        return  self.__bufferedDataSource.maxRows()

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
                    return(record[col])
                else:
                    return (str(record[col]))
            except UnicodeEncodeError as ex:
                print(row,col,record[col],type(record[col]))
            return "eroor"
        else:
            return None

    def SetValue(self, row, col, value):
        self.log.write('SetValue(%d, %d, "%s") ignored.\n' % (row, col, value))

    def DeleteRows(self,pos = 0, numRows = 1):
        print("Eliminando")
        return True
# ---------------------------------------------------------------------------


class HugeTableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        global myTableBase
        gridlib.Grid.__init__(self, parent, -1)

        memb = mem_profile.memory_usage_psutil()
        print ('Memory (Before): {}Mb'.format(memb))
        t1 = time.clock()
        self.tableBase = HugeTable(log)
        myTableBase = self.tableBase
        t2 = time.clock()
        self.scrollLock = False

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.tableBase, True)

        #self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, myTableBase.OnThumbTrack)
        #self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, myTableBase.OnThumbRelease)

        self.Bind(wx.EVT_SCROLLWIN, self.OnScrollGrid)
        self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnBeginScroll)
        self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnEndScroll)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.OnEndThumbRelease)
        self.Bind(wx.EVT_SCROLL_ENDSCROLL, self.OnEndScroll2)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.OnEndThumbRelease)
        #self.Bind(wx.EVT_KEY_DOWN,self.OnKeyDown)
        #self.Bind(wx.EVT_KEY_UP,self.OnKeyUp)
        #self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

        memf = mem_profile.memory_usage_psutil()
        print ('Memory (After) : {}Mb'.format(memf))
        print ('Diff {} mem'.format(memf - memb))
        print ('Diff {} mem'.format(1024 * (memf - memb)))
        print ('Took {} Seconds'.format(t2 - t1))

    def OnMouseWheel(self, evt):
        print("mousewheel ")
        evt.Skip()


    def OnKeyDown2(self, evt):
        print("key down")
        if evt.KeyCode == wx.WXK_PAGEDOWN or evt.KeyCode == wx.WXK_PAGEUP:
            self.scrollLock = True
            if evt.KeyCode == wx.WXK_PAGEDOWN:
                print("PGDN")
            if evt.KeyCode == wx.WXK_PAGEUP:
                print("PGUP")

        evt.Skip()

    def OnKeyUp2(self, evt):
        print("key up")
        if evt.KeyCode == wx.WXK_PAGEDOWN or evt.KeyCode == wx.WXK_PAGEUP:
            self.scrollLock = False
            self.ForceRefresh()

            if evt.KeyCode == wx.WXK_PAGEDOWN:
                print("PGDN")
            if evt.KeyCode == wx.WXK_PAGEUP:
                print("PGUP")
            else:
                print("Control?")

        evt.Skip()

    def OnScrollGrid(self, evt):
        print('BEGIN ONscroll\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
        elif not self.scrollLock:
            evt.Skip()
        return

    def OnBeginScroll(self, evt):
        print('BEGIN scroll\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
            return
        if self.GetNumberRows() == 0:
                return
        self.scrollLock = True
        evt.Skip()

    def OnEndScroll(self, evt):
        #This never gets called on 64-bit Linux
        print('End scroll\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            self.scrollLock = False
            evt.Skip()
        else:
            self.scrollLock = False
            pos = evt.GetPosition()
            calcPos =  (pos * self.GetScrollPixelsPerUnit()[1])/self.GetRowSize(0)

            print(">>>>>>>>>>>>>>>>>>> calcpos= ",calcPos)
            #self.tableBase.GetValue(calcPos,0)

            #self.MakeCellVisible(calcPos, 0)
            #self.SetGridCursor(calcPos, 0)

            #h, w = self.GetSize()
            #self.SetSize((h + 1, w))
            #self.SetSize((h, w))

            self.ForceRefresh()


            evt.Skip()

    def OnEndScroll2(self, evt):
        #This never gets called on 64-bit Linux
        print('End scroll 2\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            self.scrollLock = False
            evt.Skip()
        else:
            self.scrollLock = False
            #pos = evt.GetPosition()
            #calcPos =  (pos * self.GetScrollPixelsPerUnit()[1])/self.GetRowSize(0)

            #print(">>>>>>>>>>>>>>>>>>> calcpos= ",calcPos)
            #self.tableBase.GetValue(calcPos,0)

            #self.MakeCellVisible(calcPos, 0)
            #self.SetGridCursor(calcPos, 0)

            #h, w = self.GetSize()
            #self.SetSize((h + 1, w))
            #self.SetSize((h, w))

            self.ForceRefresh()


            evt.Skip()
        return

    def OnEndThumbRelease(self, evt):
        #This never gets called on 64-bit Linux
        print('End Thumb\n')
        self.scrollLock = False
        if evt.GetOrientation() == wx.VERTICAL:
            self.ForceRefresh()
        evt.Skip()
        return

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
