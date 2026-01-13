# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from jemlib.alib_datatypes.EnumGroup import EnumGroup, Group

from PyQt5.QtGui import QIcon

from jemlib.alib_vaporjem import Logger

class ContextRequirements:

    @dataclass
    class Context:
        current_tool: str
        selection_active: bool
        

    @staticmethod
    def getRequirements():
        from jemlib.api_krita.enums.tool import Tool
        results: list[dict[str, any]] = []

        def appendOption(name: str, value: str, icon: any):
            results.append({ 'name': f"{name} (AND)", 'value': f"AND||{value}", 'icon': icon })
            results.append({ 'name': f"{name} (OR)",  'value': f"OR||{value}", 'icon': icon })
            results.append({ 'name': f"{name} (NOT)", 'value': f"NOT||{value}", 'icon': icon })


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

    @staticmethod
    def hasRequirements(items: list[str], context: "ContextRequirements.Context"):
        if not context: return True
        if not items: return True
        
        not_values = []
        and_values = []
        or_values = []

        Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", "starting test...")

        for entry in items:
            br = entry.split("||")
            if len(br) != 3: continue
            condition = br[0]
            type = br[1]
            value = br[2]

            output = None
            failed = False

            if type == "Tool": output = context.current_tool == value
            elif type == Items.STATUS.name:
                if value == Items.STATUS_HAS_SELECTION.value: output = context.selection_active
                else: failed = True
            else: failed = True

            if failed:
                Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"{condition} - {type} - {value} - ???")
                continue
            else:
                Logger.logDebug("JemLib", "ContextRequirements", "hasRequirements", f"{condition} - {type} - {value} - {output}")

            if condition == "NOT":
                not_values.append(output)
            elif condition == "AND":
                and_values.append(output)
            elif condition == "OR":
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