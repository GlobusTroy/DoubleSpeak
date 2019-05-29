import enum

class PackType(enum.Enum):
    ClientData = 1
    Handshake = 2
    ServerMessage = 3
    KeepAlive = 4
    NameQuery = 5

class Netpack:
    CLIENT_DATA_MIN = 0
    CLIENT_DATA_MAX = 50
    HANDSHAKE = 51
    SERVER_MESSAGE = 52
    KEEPALIVE = 53
    NAMEQUERY = 54

    typeToOrd = {PackType.ClientData:CLIENT_DATA_MIN, PackType.ServerMessage:SERVER_MESSAGE,
                PackType.KeepAlive:KEEPALIVE, PackType.Handshake:HANDSHAKE, PackType.NameQuery:NAMEQUERY}
    ordToType = {v: k for k, v in typeToOrd.items()}

    def __init__(self, packType=None, head=None, data=None, datapacket=None):
        if packType is not None:
            self.head = Netpack.typeToOrd[packType]
        else:
            self.head = datapacket[0] if head is None else head
        self.data = datapacket[1:] if data is None else data
        self.PackType = Netpack.getPackType(self.head)

    @staticmethod
    def getPackType(head):
        if head <= Netpack.CLIENT_DATA_MAX and head >= Netpack.CLIENT_DATA_MIN:
            return PackType.ClientData
            
        try:
            return Netpack.ordToType[head]
        except:
            return None

    def out(self):
        bytearr = bytearray(b'')
        bytearr.append(self.head)
        return bytes(bytearr + self.data)

class Videopack(Netpack):
    def __init__(self, packType=None, head=None, data=None, imageId=None,
    index=None, imageLen=None, datapacket=None):
        super().__init__(packType=packType,head=head,data=data,datapacket=datapacket)
        if datapacket is not None:
            self.imageId = self.data[0]
            self.index = self.data[1]
            self.data = self.data[2:]
            if self.index == 0:
                self.imageLen = self.data[0]
                self.data = self.data[1:]
        else:
            self.imageId = imageId
            self.index = index
            self.imageLen = imageLen

    def out(self):
        bytearr = bytearray(b'')
        bytearr.append(self.head)
        bytearr.append(self.imageId)
        bytearr.append(self.index)
        if self.index == 0:
            bytearr.append(self.imageLen)
        return bytes(bytearr + self.data)
