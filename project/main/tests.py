# /import time
# import datetime
from django.test import TestCase


# # Create your tests here.
# import os
# files = os.listdir(os.getcwd())
# for file in files:
#     print(file,time.ctime(os.path.getctime(file)))
class Array:
    list_type = ['str', 'int', 'bool', 'float']

    def __init__(self, lenght, type, init_data=[]):
        self.lenght = lenght
        self.type = type
        self.__data = init_data
        self.__manage(init_data, lenght)

    def __manage(self, init_data, lenght):
        if self.type == 'int':
            if not init_data:
                self.__data = [0] * lenght
            self.type = int
        if self.type == 'str':
            if not init_data:
                self.__data = [''] * lenght
            self.type = str
        if self.type == 'bool':
            if not init_data:
                self.__data = [False] * lenght
            self.type = bool
        if self.type == 'float':
            if not init_data:
                self.__data = [0.0] * lenght
            self.type = float
        if init_data:
            """checks if types are correct"""
            for item in init_data:
                if not isinstance(item, self.type):
                    raise TypeError("Crazy man, you have inserted mis-type element")

    def __setitem__(self, key, value):
        if isinstance(value, self.type):
            self.__data[key] = value
            return value
        else:
            raise TypeError("please insert the appropriate data type!")

    def __getitem__(self, item):
        return self.__data[item]

    def __str__(self):
        representaion = str(self.__data)
        representaion = "{" + representaion[1:-1] + "}"
        return representaion

    def __iter__(self):
        for item in self.__data:
            yield item

    def __len__(self):
        return self.lenght

    def __class__(self):
        return self.type


type("sdfsdf")
ar1 = Array(3, "str", ['ali', 'ahmad', 'mahdmood'])
ar1[2] = "assal"
print(ar1)
for item in ar1:
    print(item)
print(ar1.type)
