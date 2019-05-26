import netpack as pk
"""
To ensure parsing and outputting packets with netpack objects works as intended
"""

def testNetPack1():
    p1 = pk.Netpack(head=3, data=b'12345')
    p2 = pk.Netpack(datapacket=p1.out())
    v1,v2 = vars(p1), vars(p2)
    assert v1 == v2

def testVideoPackIndex0():
    p1 = pk.Videopack(head=1, data=b'12345', imageId=11, index=0, imageLen=9)
    p2 = pk.Videopack(datapacket=p1.out())
    v1,v2 = vars(p1), vars(p2)
    assert v1 == v2

def testVideoPack1():
    p1 = pk.Videopack(head=2, data=b'12345', imageId=14, index=4, imageLen=9)
    p2 = pk.Videopack(datapacket=p1.out())
    v1,v2 = vars(p1), vars(p2)
    del v1['imageLen']
    assert v1 == v2

def testAll():
    testNetPack1()
    testVideoPack1()
    testVideoPackIndex0()
    print('All tests passed')

testAll()