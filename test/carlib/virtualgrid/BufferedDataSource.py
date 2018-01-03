from abc import ABCMeta, abstractmethod

from carlib.persistence import Constraints

class BufferedDataSource(object):
    __metaclass__ = ABCMeta

    def __init__(self, buffer_size):
        self.__bufferSize = buffer_size
        self.__records = None
        self.__totalRows = None
        self.__lastRow = None
        self.__lastTopRow = None
        self.__lastEndRow = None
        self.__lockRead = False
        self.__offset = 0
        self.__limit = buffer_size
        self.__orderColumn = None
        self.constraints = Constraints()

    @property
    def lockRead(self):
        """
        Retorna la definicion bloqueo de lectura de datos del buffer.
        Si es True impedira que se lean datos mientras esta encendido.

        Returns
        -------
        bool
            True si el bloqueo de lectura esta activado

        """
        return self.__lockRead

    @lockRead.setter
    def lockRead(self, value):
        """
        Setea la definicion del flag de bloque de lectura del buffer.

        Es importante anotar que si no es booleano se asumira siempre como False

        Parameters
        ----------
        value: bool
            True si el bloqueo de lectura debe activarse , False de lo contrario

        Returns
        -------
        None

        """
        if value and type(value) == bool:
            self.__lockRead = value
        else:
            self.__lockRead = False

    @abstractmethod
    def getNumberOfRecords(self, constraints):
        pass

    @abstractmethod
    def fetchRecordsToBuffer(self, constraints):
        pass

    def maxRows(self):
        if self.__totalRows is None:
            self.__totalRows = self.getNumberOfRecords(self.constraints)
        return self.__totalRows

    def getRow(self, row):
        # memb = mem_profile.memory_usage_psutil()
        # print ('Memory (Before): {}Mb'.format(memb))
        # t1 = time.clock()

        offset = (self.__bufferSize / 2) * (row // (self.__bufferSize / 2) - 1)
        if offset < 0:
            offset = 0
        self.__offset = offset

        if self.__lastRow is None:
            self.__lastRow = 0

        if not self.__lockRead:
            if row >= self.__lastEndRow or row < self.__lastTopRow:
                print("HAY QUE LERRRRRRRRRRRRRRR , row= ", row)

                self.constraints.offset = offset
                self.constraints.limit = self.__limit

                self.__records = self.fetchRecordsToBuffer(self.constraints)

                self.__lastTopRow = offset
                self.__lastEndRow = offset + self.__limit
        elif (row >= self.__lastEndRow or row < self.__lastTopRow) and abs(row - self.__lastRow) > self.__bufferSize:
            if len(self.__records) > 0:
                print(
                    ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> eliminando registros ",
                    row)
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
            except IndexError:
                # print("ERROR = ", row)
                return None

    def setOrderField(self, orderColumn, sortedColDescending):
        self.__lastTopRow = 0
        self.__lastEndRow = 0
        self.__lastRow = 0

        print("Status = ",orderColumn,sortedColDescending)
        newDirection = Constraints.SortType.DESC if sortedColDescending else Constraints.SortType.ASC

        if self.constraints.sort_field_exists(orderColumn) == False:
            self.constraints.add_sort_field(orderColumn, newDirection )
            return True
        elif self.constraints.sort_fields[orderColumn] != newDirection:
            self.constraints.add_sort_field(orderColumn, newDirection )
            return True
        return False

    def clearOrderFields(self):
        self.__lastTopRow = 0
        self.__lastEndRow = 0
        self.__lastRow = 0

        self.constraints.clear_sort_fields()
