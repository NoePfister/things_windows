from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from typing import Any, List, Optional

import orjson
from pydantic import BaseModel, Field


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


def orjson_prettydumps(v, *, default):
    return orjson.dumps(v, default=default, option=orjson.OPT_INDENT_2).decode()


class Destination(int, Enum):
    # destination: {0: inbox, 1: today/evening, 2: someday}
    INBOX = 0
    TODAY = 1
    SOMEDAY = 2


class Status(int, Enum):
    TODO = 0
    CANCELLED = 2
    COMPLETE = 3


class Note(BaseModel):
    _t: str = Field("tx", alias="_t")
    ch: int = Field(0, alias="ch")
    value: str = Field("", alias="v")
    t: int = Field(0, alias="t")

    class Config:
        allow_population_by_field_name = True


class Util:
    @staticmethod
    def now():
        return datetime.now()


class TodoItem(BaseModel):
    index: int = Field(0, alias="ix")
    title: str = Field("", alias="tt")
    status: Status = Field(Status.TODO, alias="ss")
    destination: Destination = Field(Destination.INBOX, alias="st")
    creation_date: Optional[datetime] = Field(None, alias="cd")
    modification_date: Optional[datetime] = Field(None, alias="md")
    scheduled_date: Optional[datetime] = Field(None, alias="sr")  # TODO: round to int
    completion_date: Optional[datetime] = Field(None, alias="sp")
    tir: Optional[int] = Field(None, alias="tir")
    due_date: Optional[datetime] = Field(None, alias="dd")  # TODO: round to int
    in_trash: bool = Field(False, alias="tr")
    is_project: bool = Field(False, alias="icp")
    projects: List[Any] = Field(default_factory=list, alias="pr")
    areas: List[Any] = Field(default_factory=list, alias="ar")
    is_evening: int = Field(0, alias="sb")
    tags: List[Any] = Field(default_factory=list, alias="tg")
    tp: int = Field(0, alias="tp")
    dds: None = Field(None, alias="dds")
    rt: List[Any] = Field(default_factory=list, alias="rt")
    rmd: None = Field(None, alias="rmd")
    dl: List[Any] = Field(default_factory=list, alias="dl")
    do: int = Field(0, alias="do")
    lai: None = Field(None, alias="lai")
    agr: List[Any] = Field(default_factory=list, alias="agr")
    lt: bool = Field(False, alias="lt")
    icc: int = Field(0, alias="icc")
    ti: int = Field(0, alias="ti")
    reminder: Optional[time] = Field(None, alias="ato")
    icsd: None = Field(None, alias="icsd")
    rp: None = Field(None, alias="rp")
    acrd: None = Field(None, alias="acrd")
    rr: None = Field(None, alias="rr")
    note: Note = Field(default_factory=Note, alias="nt")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda d: d.timestamp(),
            time: lambda t: (t.hour * 60 + t.minute) * 60 + t.second,
        }
        json_loads = orjson.loads
        # json_dumps = orjson_dumps
        # json_dumps = orjson_prettydumps # FIXME: json_encoders doesn't work with orjson

    @staticmethod
    def create(index: int, title: str, destination: Destination) -> TodoItem:
        now = Util.now()
        return TodoItem(
            index=index,
            title=title,
            destination=destination,
            creation_date=now,
            modification_date=now,
        )

    @staticmethod
    def todo() -> TodoItem:
        item = TodoItem(
            status=Status.TODO, modification_date=Util.now(), completion_date=None
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

    @staticmethod
    def complete() -> TodoItem:
        now = Util.now()
        item = TodoItem(
            status=Status.COMPLETE, modification_date=now, completion_date=now
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

    @staticmethod
    def cancel() -> TodoItem:
        now = Util.now()
        item = TodoItem(
            status=Status.CANCELLED, modification_date=now, completion_date=now
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

    @staticmethod
    def delete() -> TodoItem:
        item = TodoItem(in_trash=True, modification_date=Util.now())
        return item.copy(include={"in_trash", "modification_date"})

    @staticmethod
    def restore() -> TodoItem:
        item = TodoItem(in_trash=False, modification_date=Util.now())
        return item.copy(include={"in_trash", "modification_date"})

    @staticmethod
    def set_due_date(deadline: datetime) -> TodoItem:
        item = TodoItem(due_date=deadline, modification_date=Util.now())
        return item.copy(include={"due_date", "modification_date"})

    @staticmethod
    def clear_due_date() -> TodoItem:
        item = TodoItem(due_date=None, modification_date=Util.now())
        return item.copy(include={"due_date", "modification_date"})

    @staticmethod
    def set_reminder(reminder: time, scheduled_date: datetime) -> TodoItem:
        item = TodoItem(
            reminder=reminder,
            scheduled_date=scheduled_date,
            modification_date=Util.now(),
        )
        return item.copy(include={"reminder", "scheduled_date", "modification_date"})

    @staticmethod
    def clear_reminder() -> TodoItem:
        item = TodoItem(reminder=None, modification_date=Util.now())
        return item.copy(include={"reminder", "modification_date"})


if __name__ == "__main__":
    item = TodoItem.create(index=1, title="test", destination=Destination.TODAY)
    print(item)
    # print("serialize to json")
    # serialized_json = item.json(by_alias=True)
    # print(serialized_json)
    # print("deserialize from json")
    # deserialized_json = TodoItem.parse_raw(serialized_json)
    # print(deserialized_json)
