import  wx
import  wx.grid as  gridlib

#---------------------------------------------------------------------------

class HugeTable(gridlib.PyGridTableBase):

    def __init__(self, log):
        gridlib.PyGridTableBase.__init__(self)
        self.log = log

        self.odd=gridlib.GridCellAttr()
        self.odd.SetBackgroundColour("sky blue")
        self.even=gridlib.GridCellAttr()
        self.even.SetBackgroundColour("sea green")

    def GetAttr(self, row, col, kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    def GetNumberRows(self):
        return 10000

    def GetNumberCols(self):
        return 10000

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return str( (row, col) )

#---------------------------------------------------------------------------

class HugeTableGrid(gridlib.Grid):
    def __init__(self, parent, log):
        gridlib.Grid.__init__(self, parent, -1)
        self.log = log
        table = HugeTable(log)
        self.scrollLock = False

        self.SetTable(table, True)

        self.Bind(wx.EVT_SCROLLWIN, self.OnScrollGrid)
        self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnBeginScroll)
        self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnEndScroll)

    def OnScrollGrid(self, evt):
        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
        elif not self.scrollLock:
            evt.Skip()
        return

    def OnBeginScroll(self, evt):
        if evt.GetOrientation() == wx.HORIZONTAL:
            evt.Skip()
            return
        if self.GetNumberRows() == 0:
                return
        self.scrollLock = True
        evt.Skip()

    def OnEndScroll(self, evt):
        #This never gets called on 64-bit Linux
        self.log.write('End scroll\n')
        if evt.GetOrientation() == wx.HORIZONTAL:
            self.scrollLock = False
            evt.Skip()
        else:
            pos = evt.GetPosition()
            calcPos =  (pos * self.GetScrollPixelsPerUnit()[1])/self.GetRowSize(0)
            self.MakeCellVisible(calcPos, 0)
            self.SetGridCursor(calcPos, 0)
            self.scrollLock = False
            evt.Skip()
        return

#---------------------------------------------------------------------------

class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Huge (virtual) Table Demo", size=(640,480))

        grid = HugeTableGrid(self, log)

        grid.SetReadOnly(5,5, True)

#---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()