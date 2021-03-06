# copyright Chessdevil Consulting BVBA 2015 - 2019

import logging
import uuid
import asyncio
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.sql import select
from sqlalchemy.engine import RowProxy
from kbsb.mysql import DbBase

class DbClub(DbBase):
    TABLENAME = 'p_clubs'
    VERSION = 1

