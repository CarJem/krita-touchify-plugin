# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wraps krita api, ensuring PEP8 compatibility, proper typing and enums.

Main wrapper `Krita` can return wrappers to other elements of the
interface. This package has to be independent of other extension
packages.

Other api elements that require importing from other packages are
available here so that the imports to omit unresolved warnings there.
"""

from touchify_prototype.src.api_krita.core_api import KritaInstance

KritaAPI = KritaInstance()
"""Wraps krita API for typing, documentation and PEP8 compatibility."""

__all__ = ["KritaAPI"]
