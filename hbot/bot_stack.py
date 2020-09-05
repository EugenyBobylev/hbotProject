from typing import Dict


class BotStack:

    def __init__(self):
        self.__stack__ = {}

    def push(self, user, message):
        if user in self.__stack__:
            self.__stack__[user].append(message)
        else:
            self.__stack__[user] = [message]

    def pop(self, user):
        result = None
        if user in self.__stack__:
            lst = self.__stack__[user]
            if len(lst) > 0:
                result = lst.pop()
        return result

    def count(self, user):
        return len(self.__stack__[user]) if user in self.__stack__ else 0

    def all_count(self):
        cnt = sum(len(self.__stack__[item]) for item in self.__stack__)
        return cnt
