# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass


from jemlib.api_krita.enums import NodeType
from jemlib.api_krita.wrappers.node import NodeAPI


from krita import Document as KritaDocument


@dataclass
class DocumentAPI:
    """Wraps krita `Document` for typing, docs and compatibility."""

    __internal__: KritaDocument

    def isValid(self):
        return self.__internal__ != None

    @property
    def internal(self) -> KritaDocument:
        return self.__internal__
    
    @property
    def width(self) -> int:
        if self.isValid(): return self.__internal__.width()
        else: return 0

    @property
    def height(self) -> int:
        if self.isValid(): return self.__internal__.height()
        else: return 0


    @property
    def root_node(self) -> NodeAPI:
        """Settable property with this `Document`'s active `Node`."""
        if self.isValid(): return NodeAPI(self.__internal__.rootNode())
        else: return NodeAPI(None)

    @property
    def active_node(self) -> NodeAPI:
        """Settable property with this `Document`'s active `Node`."""
        if self.isValid(): return NodeAPI(self.__internal__.activeNode())
        else: return NodeAPI(None)

    @active_node.setter
    def active_node(self, node: NodeAPI) -> None:
        """Set active `Node`."""
        if self.isValid(): self.__internal__.setActiveNode(node.__internal__)

    def create_node(self, name: str, node_type: NodeType) -> NodeAPI:
        """
        Create a Node.

        IMPORTANT: Created node must be then added to node tree to be
        usable from Krita. For example with add_child_node() method of
        Node Class.

        When relevant, the new Node will have the color space of the
        image by default; that can be changed with Node::setColorSpace.

        The settings and selections for relevant layer and mask types
        can also be set after the Node has been created.
        """
        if self.isValid(): return NodeAPI(self.__internal__.createNode(name, node_type.value))
        else: return NodeAPI(None)

    @property
    def current_time(self) -> int:
        """Settable property with this `Document`'s current frame number."""
        if self.isValid(): return self.__internal__.currentTime()
        else: return 0

    @current_time.setter
    def current_time(self, time: int) -> None:
        """Set current time using frame number"""
        if self.isValid(): self.__internal__.setCurrentTime(round(time))

    def get_top_nodes(self) -> list[NodeAPI]:
        """Return a list of `Nodes` without a parent."""
        if not self.isValid(): return []
        return [NodeAPI(node) for node in self.__internal__.topLevelNodes()]

    def get_all_nodes(self, include_collapsed: bool = False) -> list[NodeAPI]:
        """Return a list of all `Nodes` in this document bottom to top."""
        if not self.isValid(): return []
        def recursive_search(nodes: list[NodeAPI], found_so_far: list[NodeAPI]):
            for node in nodes:
                if include_collapsed or not node.collapsed:
                    recursive_search(node.get_child_nodes(), found_so_far)
                found_so_far.append(node)
            return found_so_far
        return recursive_search(self.get_top_nodes(), [])

    @property
    def dpi(self) -> int:
        """Return dpi (dot per inch) of the document."""
        if self.isValid(): return self.__internal__.resolution()
        else: return 72

    def refresh(self) -> None:
        """Refresh OpenGL projection of this document."""
        if self.isValid(): self.__internal__.refreshProjection()

    def read_annotation(self, name: str) -> str:
        """Read annotation from .kra document parsed as string."""
        if not self.isValid(): return ""
        return self.__internal__.annotation(name).data().decode(encoding="utf-8")

    def write_annotation(self, name: str, description: str, value: str):
        """Write annotation to .kra document."""
        if self.isValid():
            self.__internal__.setAnnotation(name,description,value.encode(encoding="utf-8"))

    def contains_annotation(self, name: str) -> bool:
        """Return if annotation of given name is stored in .kra."""
        if self.isValid(): return name in self.__internal__.annotationTypes()
        else: return False

    def colorModel(self) -> str:
        return self.__internal__.colorModel()
    
    def colorProfile(self) -> str:
        return self.__internal__.colorProfile()
    
    def colorDepth(self) -> str:
        return self.__internal__.colorDepth() 

    def crop(self, x: int, y: int, w: int, h: int):
        self.__internal__.crop(x, y, w, h)

    def waitForDone(self):
        self.__internal__.waitForDone()

    def refresh_projection(self):
        self.__internal__.refreshProjection()
