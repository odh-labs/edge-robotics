#!/usr/bin/python
from mongo_tool import MongoTool

if __name__=="__main__":
    mt = MongoTool()
    mt.delete()
    print("deleted last month data")
    mt.disconnect()