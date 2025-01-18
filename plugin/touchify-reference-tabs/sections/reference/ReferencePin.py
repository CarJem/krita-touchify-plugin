from dataclasses import dataclass
from typing import Optional
from PyQt5.QtGui import QPixmap


@dataclass
class ReferencePin:
        # ID
        index : Optional[int] = None
        # Type
        tipo : Optional[str] = None
        # State
        render : Optional[bool]  = None
        active : Optional[bool]  = None
        select : Optional[bool]  = None
        pack   : Optional[bool]  = None
        # Transform
        trz : Optional[float]  = None
        tsk : Optional[float]  = None # ( diameter of circle )
        tsw : Optional[float] = None  # ( width with no rotation )
        tsh : Optional[float] = None  # ( height with no rotation )
        # Bound Box
        bx : Optional[float]  = None # ( center x )
        by : Optional[float]  = None # ( center y )
        bl : Optional[float]  = None # ( left )
        br : Optional[float]  = None # ( right )
        bt : Optional[float]  = None # ( top )
        bb : Optional[float]  = None # ( bottom )
        bw : Optional[float]  = None # ( width )
        bh : Optional[float]  = None # ( height )
        # Clip
        cl : Optional[float] = None
        cr : Optional[float] = None
        ct : Optional[float] = None
        cb : Optional[float] = None
        cw : Optional[float] = None
        ch : Optional[float] = None
        # Dimensions
        area        : Optional[float] = None
        perimeter   : Optional[float] = None
        ratio       : Optional[float] = None
        # Edits
        egs         : Optional[bool]  = None
        efx         : Optional[bool]  = None
        efy         : Optional[bool]  = None
        # Text
        text        : Optional[str] = None
        font        : Optional[str] = None
        letter      : Optional[int] = None
        pen         : Optional[str] = None
        bg          : Optional[str] = None
        # Pixmap
        path        : Optional[str] = None
        web         : Optional[str] = None
        qpixmap     : Optional[QPixmap] = None
        draw        : Optional[QPixmap] = None
        zdata       : Optional[str] = None #(string of bytes)

        #IDK
        cstate: Optional[bool] = None

        #def __setitem__(self, key, value):
            #setattr(self, key, value)

        #def __getitem__(self, item):
            #return getattr(self, item)


        @staticmethod
        def dict_factory(x):
            exclude_fields = ("qpixmap", "draw")
            return {k: v for (k, v) in x if ((v is not None) and (k not in exclude_fields))}
        
        def dict(self):
            return {
                #ID
                "index": self.index,
                # Type
                "tipo": self.tipo,
                # State
                "render"     : self.render, # bool
                "active"     : self.active, # bool
                "select"     : self.select, # bool
                "pack"       : self.pack, # bool
                # Transform
                "trz"        : self.trz, # float
                "tsk"        : self.tsk, # float ( diameter of circle )
                "tsw"        : self.tsw, # float ( width with no rotation )
                "tsh"        : self.tsh, # float ( height with no rotation )
                # Bound Box
                "bx"         : self.bx, # float ( center x )
                "by"         : self.by, # float ( center y )
                "bl"         : self.bl, # float ( left )
                "br"         : self.br, # float ( right )
                "bt"         : self.bt, # float ( top )
                "bb"         : self.bb, # float ( bottom )
                "bw"         : self.bw, # float ( width )
                "bh"         : self.bh, # float ( height )
                # Clip
                "cl"         : self.cl, # float
                "cr"         : self.cr, # float
                "ct"         : self.ct, # float
                "cb"         : self.cb, # float
                "cw"         : self.cw, # float
                "ch"         : self.ch, # float
                # Dimensions
                "area"       : self.area, # float
                "perimeter"  : self.perimeter, # float
                "ratio"      : self.ratio, # float
                # Edits
                "egs"        : self.egs, # bool
                "efx"        : self.efx, # bool
                "efy"        : self.efy, # bool
                # Text
                "text"       : self.text, # string
                "font"       : self.font, # string
                "letter"     : self.letter, # integer
                "pen"        : self.pen, # string
                "bg"         : self.bg, # string
                # Pixmap
                "path"       : self.path, # string
                "web"        : self.web, # string
                #"qpixmap"    : self.qpixmap, # QPixmap
                #"draw"       : self.draw, # QPixmap
                "zdata"      : self.zdata, # string of bytes
            }