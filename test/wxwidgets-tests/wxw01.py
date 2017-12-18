## import all of the wxPython GUI package
import wx

## Create a new frame class, derived from the wxPython Frame.
from wx.grid import Grid

from carlib.database import TransactionManager, DatabasePersistence
from carlib.database.impl import MsSQLBaseDelegate
from carlib.persistence import Model, Constraints
from carlib.utils import dbutils


class MyFrame(wx.Frame):

    def __init__(self, parent, id, title):
        self.dao = self.init_db();
        self.read_records = 0
        constraint = Constraints()
        constraint.offset = 0
        constraint.limit = 100

        # First, call the base class' __init__ method to create the frame
        wx.Frame.__init__(self, parent, id, title,
                         wx.Point(100, 100), wx.Size(300, 200))

        # Associate some events with methods of this class
        wx.EVT_SIZE(self, self.OnSize)
        #wx.EVT_SCROLLWIN_BOTTOM(self, self.OnEndScroll)

        # Add a panel and some controls to display the size and position
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('#FDDF99')

        self.grid = Grid(panel)
        self.grid.CreateGrid(0,12)
        wx.grid.EVT_GRID_CELL_LEFT_CLICK(self,self.OnGridLeftClick)
        #wx.EVT_SCROLLWIN_BOTTOM(self.grid, self.OnEndScroll)
        self.grid.Bind(wx.EVT_SCROLLWIN, self.OnEndScroll)


        #self.grid.SetCellBackgroundColour(2, 2, wx.CYAN)

        #self.grid.SetCellEditor(5, 0, wx.grid.GridCellNumberEditor(1,1000))
        #self.grid.SetCellValue(5, 0, "123")

        #self.grid.SetCellAlignment(9, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        #self.grid.SetCellValue(9, 1, "This cell is set to span 3 rows and 3 columns")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        #self.grid.ClearGrid()
        ##self.grid.AppendRows(20)
        #self.grid.SetColLabelValue(0,"test")
        #self.grid.SetCellValue(21, 1, "This cell is set to span 3 rows and 3 columns")

        rows = self.dao.fetch_records(constraint, raw_answers=True, record_type_classname=AutosModel)
        self.read_records = len(rows)

        print(rows[0])
        #print(rows[7]["marca"])
        #print(rows[7]["modelo"])
        #print(rows[7]["version"])

        self.printRows(rows)

    def printRows(self,rows):
        self.grid.SetColLabelValue(0,rows[0][0][0])
        self.grid.SetColLabelValue(1,rows[0][1][0])
        self.grid.SetColLabelValue(2,rows[0][2][0])


        self.grid.AppendRows(self.read_records)
        i = -1
        for row in rows:
            #print(i)
            #print(row[0])
            #print(row[1])
            #print(row[2])
            if i > -1:
                self.grid.SetCellValue(i, 0, row[0])
                self.grid.SetCellValue(i, 1, row[1])
                self.grid.SetCellValue(i, 2, str(row[2]))
            i = i+1

        self.grid.AutoSize()
    # This method is called automatically when the CLOSE event is
    # sent to this window
    def OnCloseWindow(self, event):
        # tell the window to kill itself
        self.Destroy()

    def OnEndScroll(self, event):
        # tell the window to kill itself
        print("Llegue al final")
        print(event.GetPosition())
        print(event.GetOrientation())
        #print(event.__dict__)
        #print(event.commandType)
        event.Skip()

    # This method is called by the system when the window is resized,
    # because of the association above.
    def OnSize(self, event):

        # tell the event system to continue looking for an event handler,
        # so the default handler will get called.
        event.Skip()

    def OnGridLeftClick(self, evt):
        print "OnCellLeftClick: (%d,%d) %s\n" % (evt.GetRow(),
                                                 evt.GetCol(),
                                                 evt.GetPosition())
        evt.Skip()

    def init_db(self):

        trx = TransactionManager('mssql', {'dsn': 'MSSQLServer', 'host': '192.168.0.7', 'port': '1433',
                                          'user': 'sa', 'password': 'melivane', 'database': 'veritrade'})


        daoDelegate = DAODelegateTest()
        return DatabasePersistence(trx, daoDelegate)

# Every wxWidgets application must have a class derived from wxApp
class MyApp(wx.App):

    # wxWidgets calls this method to initialize the application
    def OnInit(self):
        # Create an instance of our customized Frame class
        frame = MyFrame(None, -1, "This is a test")
        frame.Show(True)

        # Return a success flag
        return True


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
        if c_constraints:
            sql = "select"
            if c_constraints.limit and c_constraints.offset == 0:
                sql = sql + " top " + str(c_constraints.limit) + " marca,modelo,version from veritrade"
            elif c_constraints.limit - c_constraints.offset > 0:
                sql = sql + " marca,modelo,version from(select top 1000000 marca,modelo,version,row_number() over(order by (select null)) as row from veritrade "
                sql = sql + dbutils.process_fetch_conditions(self.driver_id, c_constraints)
                sql = sql + ")m where row between " + str(c_constraints.offset) + " and " + str(
                    c_constraints.offset + c_constraints.limit - 1)
            else:
                sql = " marca,modelo,version from veritrade"
        else:
            sql = "select  marca,modelo,version from veritrade"
        print (sql)
        return sql

app = MyApp(0)     # Create an instance of the application class
app.MainLoop()     # Tell it to start processing events
