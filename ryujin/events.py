# MIT License

# Copyright (c) 2022 ryujin-xd™

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect
import re
from pathlib import Path

from pymongo import MongoClient
from telethon import events

from ryujin import MONGO_DB_URI, telethn

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["RyujinRobot"]
gbanned = db.gban


def register(**args):
    """Registers a new message."""
    pattern = args.get("pattern", None)

    r_pattern = r"^[/!.]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        telethn.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def chataction(**args):
    """Registers chat actions."""

    def decorator(func):
        telethn.add_event_handler(func, events.ChatAction(**args))
        return func

    return decorator


def userupdate(**args):
    """Registers user updates."""

    def decorator(func):
        telethn.add_event_handler(func, events.UserUpdate(**args))
        return func

    return decorator


def inlinequery(**args):
    """Registers inline query."""
    pattern = args.get("pattern", None)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    def decorator(func):
        telethn.add_event_handler(func, events.InlineQuery(**args))
        return func

    return decorator


def callbackquery(**args):
    """Registers inline query."""

    def decorator(func):
        telethn.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator


def bot(**args):
    pattern = args.get("pattern")
    r_pattern = r"^[/]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    reg = re.compile("(.*)")

    if pattern is not None:
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = cmd.group(1).replace("$", "").replace("\\", "").replace("^", "")
            except BaseException:
                pass

            try:
                FUN_LIST[file_test].append(cmd)
            except BaseException:
                FUN_LIST.update({file_test: [cmd]})
        except BaseException:
            pass

    def decorator(func):
        async def wrapper(check):
            if check.edit_date:
                return
            if check.fwd_from:
                return
            if check.is_group or check.is_private:
                pass
            else:
                print("i don't work in channels")
                return
            if check.is_group:
                if check.chat.megagroup:
                    pass
                else:
                    print("i don't work in small chats")
                    return

            users = gbanned.find({})
            for c in users:
                if check.sender_id == c["user"]:
                    return
            try:
                await func(check)
                try:
                    LOAD_PLUG[file_test].append(func)
                except Exception:
                    LOAD_PLUG.update({file_test: [func]})
            except BaseException:
                return
            else:
                pass

        telethn.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator


def ryujin(**args):
    pattern = args.get("pattern", None)
    args.get("disable_edited", False)
    ignore_unsafe = args.get("ignore_unsafe", False)
    unsafe_pattern = r"^[^/!#@\$A-Za-z]"
    args.get("group_only", False)
    args.get("disable_errors", False)
    args.get("insecure", False)
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    if "disable_edited" in args:
        del args["disable_edited"]

    if "ignore_unsafe" in args:
        del args["ignore_unsafe"]

    if "group_only" in args:
        del args["group_only"]

    if "disable_errors" in args:
        del args["disable_errors"]

    if "insecure" in args:
        del args["insecure"]

    if pattern:
        if not ignore_unsafe:
            args["pattern"] = args["pattern"].replace("^.", unsafe_pattern, 1)
