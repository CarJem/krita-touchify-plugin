# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from enum import IntEnum
from jemlib.alib_datatypes.EnumGroup import EnumGroup, Group

from PyQt5.QtGui import QIcon

from jemlib.alib_vaporjem import Logger

class ContextRequirements:

    class Mode(IntEnum):
        OR=1,
        AND=2,
        NOT=3

        @staticmethod
        def toString(input: int):
            if input == ContextRequirements.Mode.AND:
                return "AND"
            elif input == ContextRequirements.Mode.OR:
                return "OR"
            elif input == ContextRequirements.Mode.NOT:
                return "NOT"
            else:
                return "???"

    @dataclass
    class DisplayRule:
        name: str
        value: str
        icon: QIcon

        def asRule(self, mode: int):
            details = self.value.split("||")
            while "" in details: details.remove("")
            if len(details) != 2: return None

            return ContextRequirements.Rule(details[0], details[1], mode)

    @dataclass
    class Rule:
        type: str
        value: str
        mode: int

        def export(self):
            if self.mode == ContextRequirements.Mode.AND: return f"AND||{self.type}||{self.value}"
            elif self.mode == ContextRequirements.Mode.OR: return f"OR||{self.type}||{self.value}"
            elif self.mode == ContextRequirements.Mode.NOT: return f"NOT||{self.type}||{self.value}"
            else: return None



        @staticmethod
        def parse(item: str):
            details = item.split("||")
            while "" in details: details.remove("")
            if len(details) != 3: return None

            option = details[0]
            group = details[1]
            value = details[2]


            known_values = [x.value for x in ContextRequirements.getKnownValues()]

            if f"{group}||{value}" not in known_values: return None

            if option == "AND":
                return ContextRequirements.Rule(group, value, ContextRequirements.Mode.AND)
            elif option == "OR":
                return ContextRequirements.Rule(group, value, ContextRequirements.Mode.OR)
            elif option == "NOT":
                return ContextRequirements.Rule(group, value, ContextRequirements.Mode.NOT)

    @dataclass
    class Context:
        current_tool: str
        selection_active: bool

    @staticmethod
    def parse(input: str) -> list["ContextRequirements.Rule"]:
        temp_list = input.split(",")
        if "" in temp_list: temp_list.remove("")

        actual_temp_list = []
        for item in temp_list:
            output = ContextRequirements.Rule.parse(item)
            if output: actual_temp_list.append(output)
        return actual_temp_list

    @staticmethod
    def getKnownValues() -> list["ContextRequirements.DisplayRule"]:
        def generate():
            from jemlib.api_krita.enums.tool import Tool
            results: list[ContextRequirements.DisplayRule] = []

            def appendOption(name: str, value: str, icon: any):
                results.append(ContextRequirements.DisplayRule(name, value, icon))

            for value, data in Tool._member_map_.items():
                data: Tool
                appendOption(f"Tool: {data.pretty_name}", f"Tool||{data.value}", data.icon)

            for group_string, group_data in Items._groups_.items():
                group_data: Group
                for key in group_data.keys:
                    actual_enum = Items[key]
                    value = f"{group_data.name}||{actual_enum.value}"
                    Logger.logDebug("JemLib", "ContextRequirements", "getRequirements", value)
                    appendOption(f"{actual_enum.pretty_name}", value, actual_enum.icon)
            return results

        try:
            return ContextRequirements.__knownValues
        except AttributeError:
            ContextRequirements.__knownValues = generate()
            return ContextRequirements.__knownValues

    @staticmethod
    def hasRequirements(items: list[str], context: "ContextRequirements.Context"):
        if not context: return True
        if not items: return True
        
        not_values = []
        and_values = []
        or_values = []

        Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", "starting test...")

        for entry in items:
            rule = ContextRequirements.Rule.parse(entry)
            if not rule: continue
            failed = False

            if rule.type == "Tool": 
                output = context.current_tool == rule.value

            elif rule.type == Items.STATUS.name:
                if rule.value == Items.STATUS_HAS_SELECTION.value: output = context.selection_active
                else: failed = True

            else: 
                failed = True

            if failed:
                Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"{ContextRequirements.Mode.toString(rule.mode)} - {rule.type} - {rule.value} - ???")
                continue
            else:
                Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"{ContextRequirements.Mode.toString(rule.mode)} - {rule.type} - {rule.value} - {output}")

            if rule.mode == ContextRequirements.Mode.NOT:
                not_values.append(output)
            elif rule.mode == ContextRequirements.Mode.AND:
                and_values.append(output)
            elif rule.mode == ContextRequirements.Mode.OR:
                or_values.append(output)
            else:
                continue

        not_conditions_met = not True in not_values or len(not_values) == 0
        or_conditions_met = True in or_values or len(or_values) == 0
        and_conditions_met = not False in and_values or len(and_values) == 0

        Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"not_conditions_met: {not_conditions_met}")
        Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"or_conditions_met: {or_conditions_met}")
        Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"and_conditions_met: {and_conditions_met}")

        return not_conditions_met and or_conditions_met and and_conditions_met
    

class Items(EnumGroup):

    STATUS = Group("Status")
    STATUS_HAS_SELECTION = "HasSelection"

    @property
    def pretty_name(self) -> str:
        if self in PRETTY_NAMES:
            return PRETTY_NAMES[self]
        return f"Condition: {self.name.replace('_', ' ')}"

    @property
    def icon(self) -> QIcon:
        from jemlib.managers.IconRepository import IconRepository
        if self in ICON_NAMES:
            return IconRepository.iconLoader(ICON_NAMES[self])
        return IconRepository.fallbackIcon()

ICON_NAMES = {
    Items.STATUS_HAS_SELECTION: "material:select-all"
}

PRETTY_NAMES = {
    Items.STATUS_HAS_SELECTION: "Status: Has Selection"
}