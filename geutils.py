# -*- coding: utf-8 -*-

"""
***************************************************************************
    geutils.py
    ---------------------
    Date                 : October 2013
    Copyright            : (C) 2013-2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'October 2013'
__copyright__ = '(C) 2013-2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import uuid
import tempfile
import shutil


def tempDirectory():
    tmp = os.path.join(tempfile.gettempdir(), 'getools')
    if not os.path.exists(tmp):
        os.makedirs(tmp)

    return os.path.abspath(tmp)


def tempFileName(basename):
    tmp = os.path.join(tempDirectory(), uuid.uuid4().hex)
    if not os.path.exists(tmp):
        os.makedirs(tmp)

    fName = os.path.join(tmp, basename)
    return fName


def removeTempFiles():
    tmp = tempDirectory()
    if os.path.exists(tmp):
        shutil.rmtree(tmp, True)
