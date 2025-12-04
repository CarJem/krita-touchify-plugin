# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from touchify_prototype.src.api_krita.enums import BlendingMode


from krita import Node as KritaNode


@dataclass
class NodeAPI():
    """Wraps krita `Node` for typing, documentation and compatibility."""

    __internal__: KritaNode

    def isValid(self):
        return self.__internal__ != None
    
    @property
    def internal(self) -> KritaNode:
        return self.__internal__

    @property
    def color_label(self) -> int:
        if self.isValid(): return self.__internal__.colorLabel()
        else: return 0

    @color_label.setter
    def color_label(self, value: int):
        if self.isValid(): self.__internal__.setColorLabel(value)

    @property
    def name(self) -> str:
        """Settable property with this node's name."""
        if self.isValid(): return self.__internal__.name()
        else: return ""

    @name.setter
    def name(self, new_name: str) -> None:
        """Set name of this node."""
        if self.isValid(): self.__internal__.setName(new_name)

    @property
    def visible(self) -> bool:
        """Settable property with visibility of this node."""
        if self.isValid(): return self.__internal__.visible()
        else: return False

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set visibility of this node."""
        if self.isValid(): self.__internal__.setVisible(value)

    def toggle_visibility(self) -> None:
        """Change visibility of this node to the opposite one."""
        if self.isValid(): self.visible = not self.visible

    @property
    def opacity(self) -> int:
        """Settable property with opacity of this node."""
        if self.isValid(): return round(self.__internal__.opacity()/2.55)
        else: return 0

    @opacity.setter
    def opacity(self, opacity: int) -> None:
        """Set opacity of this node."""
        if self.isValid(): self.__internal__.setOpacity(round(2.55*opacity))

    @property
    def blending_mode(self) -> BlendingMode:
        """Settable property with blending_mode of this node."""
        if self.isValid(): return BlendingMode(self.__internal__.blendingMode())
        else: return BlendingMode.NORMAL

    @blending_mode.setter
    def blending_mode(self, blending_mode: BlendingMode | str) -> None:
        """Set blending_mode of this node."""
        if not self.isValid(): 
            return
        elif type(blending_mode) == BlendingMode:
            self.__internal__.setBlendingMode(blending_mode.value)
        elif type(blending_mode) == str:
            actual_mode = BlendingMode.of(blending_mode)
            self.__internal__.setBlendingMode(actual_mode.value)

    @property
    def pinned_to_timeline(self) -> bool:
        """Settable property of node being pinned to timeline."""
        if self.isValid(): return self.__internal__.isPinnedToTimeline()
        else: return False

    @pinned_to_timeline.setter
    def pinned_to_timeline(self, pinned_to_timeline: bool) -> None:
        """Set pinned_to_timeline property of this node."""
        if self.isValid(): self.__internal__.setPinnedToTimeline(pinned_to_timeline)

    @property
    def collapsed(self) -> bool:
        """Settable property telling whether this node is collapsed."""
        if self.isValid(): return self.__internal__.collapsed()
        else: return False

    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        """Change collapsed state of this node."""
        if self.isValid(): self.__internal__.setCollapsed(value)

    @property
    def is_group_layer(self) -> bool:
        """Read-only property telling if this node is a group."""
        if self.isValid(): return self.__internal__.type() == "grouplayer"
        else: return False

    @property
    def is_animated(self) -> bool:
        """Read-only property telling if this node has animation frames."""
        if self.isValid(): return self.__internal__.animated()
        else: return False

    @property
    def unique_id(self) -> str:
        """Read-only property holding unique ID of a node."""
        if self.isValid(): return self.__internal__.uniqueId()
        else: return None


    def add_child_node(self, child: 'NodeAPI', above: 'NodeAPI') -> bool:
        """
        Add the given node in the list of children.

        Parameters:
            child - the node to be added
            above - the node above which this node will be placed

        Returns false if adding the node failed.
        """
        if self.isValid():
            return self.__internal__.addChildNode(child.__internal__, above.__internal__)
        else:
            return False

    def get_child_nodes(self) -> list['NodeAPI']:
        """Return a list of wrapped Nodes that are children of this one."""
        if self.isValid(): return [NodeAPI(node) for node in self.__internal__.childNodes()]
        else: return []

    def get_parent_node(self) -> 'NodeAPI':
        """Return wrapped Node being a parent of this node."""
        if self.isValid(): return NodeAPI(self.__internal__.parentNode())
        else: return NodeAPI(None)

    def __eq__(self, node: 'NodeAPI') -> bool:
        """Two objects are the same node, when their unique IDs matches."""
        if not self.isValid() and node == None:
            return True
        elif not isinstance(node, NodeAPI):
            return False
        return self.unique_id == node.unique_id
