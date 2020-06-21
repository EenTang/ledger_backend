#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
FileName:   exceptions.py
Author:     Tang Jiandong
Date:       2020-06-20 23:10:58
@contact:

Description:

"""


class BaseError(Exception):
    pass


class ParamsError(BaseError):
    pass


class NotAllowed(BaseError):
    pass
