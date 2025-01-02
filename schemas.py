from pydantic import BaseModel
from typing import List, Dict, Optional


class TableSchema(BaseModel):
    table_name: str
    columns: List[str]
    rows: List[List[str]]

class TablesSchema(BaseModel):
    tables: List[TableSchema]

