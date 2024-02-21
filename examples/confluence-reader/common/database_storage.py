# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pickle
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from common.storage import IStorage
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import LargeBinary
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError


class DatabaseStorage(IStorage):
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
        self.table = Table(
            "vdk_storage",
            self.metadata,
            Column("name", String, primary_key=True),
            Column("content", LargeBinary),
            Column("content_type", String),
        )
        self.metadata.create_all(self.engine)

    def store(self, name: str, content: Union[str, bytes, Any]) -> None:
        serialized_content, content_type = self._serialize_content(content)
        ins = self.table.insert().values(
            name=name, content=serialized_content, content_type=content_type
        )
        try:
            with self.engine.connect() as conn:
                conn.execute(ins)
                conn.commit()
        except IntegrityError:
            # Handle duplicate name by updating existing content
            upd = (
                self.table.update()
                .where(self.table.c.name == name)
                .values(content=serialized_content, content_type=content_type)
            )
            with self.engine.connect() as conn:
                conn.execute(upd)
                conn.commit()

    def retrieve(self, name: str) -> Optional[Union[str, bytes, Any]]:
        sel = self.table.select().where(self.table.c.name == name)
        with self.engine.connect() as conn:
            result = conn.execute(sel).fetchone()
            if result:
                return self._deserialize_content(result.content, result.content_type)
        return None

    def list_contents(self) -> List[str]:
        sel = select(self.table.c.name)
        with self.engine.connect() as conn:
            result = conn.execute(sel).fetchall()
            return [row[0] for row in result]

    def remove(self, name: str) -> bool:
        del_stmt = self.table.delete().where(self.table.c.name == name)
        with self.engine.connect() as conn:
            result = conn.execute(del_stmt)
            conn.commit()
            return result.rowcount > 0

    @staticmethod
    def _serialize_content(content: Union[str, bytes, Any]) -> tuple[bytes, str]:
        if isinstance(content, bytes):
            return content, "bytes"
        elif isinstance(content, str):
            return content.encode(), "string"
        else:
            # Fallback to pickle for other types
            return pickle.dumps(content), "pickle"

    @staticmethod
    def _deserialize_content(content: bytes, content_type: Optional[str]) -> Any:
        if content_type == "pickle":
            return pickle.loads(content)
        if content_type == "string":
            return content.decode()
        return content
