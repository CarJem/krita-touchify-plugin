# Python
# Krita
from krita import *
# PyQt5
from PyQt5 import QtCore
# Imagine Board
from .ReferenceCalc import *

class ReferenceViewWorker( QObject ):

    # Run Packer
    def run( self, source, mode, method ):
        # Variables
        self.stop = False
        pin_list = source.pin_list
        count = len( pin_list )

        # Thread Settings
        if mode == "THREAD":
            source.thread_packer.setPriority( QThread.HighestPriority )

        # Time Watcher
        start = QtCore.QDateTime.currentDateTimeUtc()

        # List Packs
        perfect_area = 0
        pack_sort = [] # Yes Packing
        pack_other = [] # No Packing
        for i in range( 0, count ):
            # Index
            pin_list[i]["index"] = i

            # Entry
            entry = {
                "index"    : pin_list[i]["index"],
                "bx"        : pin_list[i]["bx"],
                "by"        : pin_list[i]["by"],
                "bl"        : pin_list[i]["bl"],
                "br"        : pin_list[i]["br"],
                "bt"        : pin_list[i]["bt"],
                "bb"        : pin_list[i]["bb"],
                "bw"        : pin_list[i]["bw"],
                "bh"        : pin_list[i]["bh"],
                "perimeter" : pin_list[i]["perimeter"],
                "area"      : pin_list[i]["area"],
                "ratio"     : pin_list[i]["ratio"],
                }

            # Selection
            select = pin_list[i]["select"]
            if select == True:
                # List
                pack_sort.append( entry )
                # Area
                area = pin_list[i]["area"]
                perfect_area += area
                # Write
                pin_list[i]["pack"] = True
                pin_list[i]["draw"] = None
            else:
                # List
                pack_other.append( entry )
                # Write
                pin_list[i]["pack"] = False
        
        # Reorder Pin List
        list_order = list()
        reorder = list()
        reorder.extend( pack_other )
        reorder.extend( pack_sort )
        for i in range( 0, len( reorder ) ):
            list_order.append( pin_list[ reorder[i]["index"] ] )
        source.pin_list = list_order
        del list_order, reorder

        # Progress Bar
        source.ProgressBar_Maximum( count - 1 )
        source.ProgressBar_Value( 0 )

        # Packing
        if method in ( "GRID", "ROW", "COLUMN", "PILE" ):
            pack_area = self.Pack_Linear( source, mode, method, pack_sort, pack_other, pin_list )
        if method in ( "AREA", "PERIMETER", "RATIO", "CLASS" ):
            pack_area = self.Pack_Optimal( source, mode, method, pack_sort, pack_other, pin_list )

        # Progress Bar
        source.ProgressBar_Maximum( 1 )
        source.ProgressBar_Value( 0 )

        # Time Watcher
        end = QtCore.QDateTime.currentDateTimeUtc()
        delta = start.msecsTo( end )
        time = QTime( 0,0 ).addMSecs( delta )

        # Efficiency
        efficiency = round( ( perfect_area / pack_area ) * 100, 3 )
        # Print
        try:QtCore.qDebug( f"Imagine Board | PACK { time.toString( 'hh:mm:ss.zzz' ) } | COUNT { count } | METHOD { method } | EFFICIENCY { efficiency } %" )
        except:pass

        # Stop Worker
        if mode == "SINGLE":source.Packer_Stop()
        if mode == "THREAD":source.Packer_Thread_Quit()
    def STOP( self ):
        self.stop = True

    # Cycles
    def Pack_Linear( self, source, mode, method, pack_sort, pack_other, pin_list ):
        # Sorting List
        if method in ( "GRID", "ROW" ):
            pack_sort = sorted( pack_sort, reverse=True, key=lambda entry:entry["bh"] )
        if method == "COLUMN":
            pack_sort = sorted( pack_sort, reverse=True, key=lambda entry:entry["bw"] )
        if method == "PILE":
            pack_sort = sorted( pack_sort, reverse=False, key=lambda entry:entry["area"] )

        # Starting Points
        start_x = min( self.List_Key( pack_sort, "bl" ) )
        start_y = min( self.List_Key( pack_sort, "bt" ) )
        if method == "GRID":
            total_area = 0
            for i in range( 0, len( pack_sort ) ):
                total_area += pack_sort[i]["area"]
            side = math.sqrt( total_area )
            end_x = start_x + side
        if method == "PILE":
            lx = max( self.List_Key( pack_sort, "bw" ) )
            ly = max( self.List_Key( pack_sort, "bh" ) )

        # Apply to Reference List
        for s in range( 0, len( pack_sort ) ):
            # Progress Bar
            if s % 5 == 0:
                source.ProgressBar_Value( s + 1 )
                QApplication.processEvents()
            # Stop Cycle
            if self.stop == True:
                message = "Continue Packing ?"
                loop = QMessageBox.question( QWidget(), "Imagine Board", message, QMessageBox.Yes, QMessageBox.Abort )
                if loop == QMessageBox.Abort:
                    break
                self.stop = False

            # Index
            pin_index = pack_sort[s]["index"]

            # Calculation
            if s == 0:
                if method in ( "GRID", "ROW", "COLUMN" ):
                    px = start_x
                    py = start_y
                if method == "GRID":
                    above = start_y + pack_sort[s]["bh"]
                if method == "PILE":
                    px = start_x - pack_sort[s]["bw"] * 0.5 + lx * 0.5
                    py = start_y - pack_sort[s]["bh"] * 0.5 + ly * 0.5
            else:
                if method == "GRID":
                    if pack_sort[s-1]["br"] >= end_x:
                        px = start_x
                        py = above
                        above += pack_sort[s]["bh"]
                    else:
                        px = pack_sort[s-1]["br"]
                        py = pack_sort[s-1]["bt"]
                if method == "ROW":
                    px = pack_sort[s-1]["br"]
                    py = pack_sort[s-1]["bt"]
                if method == "COLUMN":
                    px = pack_sort[s-1]["bl"]
                    py = pack_sort[s-1]["bb"]
                if method == "PILE":
                    px = start_x - pack_sort[s]["bw"] * 0.5 + lx * 0.5
                    py = start_y - pack_sort[s]["bh"] * 0.5 + ly * 0.5

            # Move to Point
            source.Move_Point( pack_sort, s, px, py )
            source.Move_Point( pin_list, pin_index, px, py )

        # Draw
        for s in range( 0 , len( pack_sort ) ):
            pin_index = pack_sort[s]["index"]
            pin_list[pin_index]["pack"] = False
            source.Pin_Draw_QPixmap( pin_list, pin_index )

        # Finish
        pack_area = self.Report_Area( pack_sort )
        return pack_area
    def Pack_Optimal( self, source, mode, method, pack_sort, pack_other, pin_list ):
        # Variables
        ru = 5

        # Sorting List
        if method == "AREA":
            pack_sort = sorted( pack_sort, reverse=True, key = lambda entry:entry["area"] )
        if method == "PERIMETER":
            pack_sort = sorted( pack_sort, reverse=True, key = lambda entry:entry["perimeter"] )
        if method == "RATIO":
            pack_sort = sorted( pack_sort, reverse=False, key = lambda entry:entry["ratio"] )
        if method == "CLASS":
            # Variables
            ratio_0 = []
            ratio_1 = []
            ratio_2 = []
            # Sorting
            for i in range( 0, len( pack_sort ) ):
                ratio = pack_sort[i]["ratio"]
                if ratio < 1:
                    ratio_0.append( pack_sort[i] )
                if ratio == 1:
                    ratio_1.append( pack_sort[i] )
                if ratio > 1:
                    ratio_2.append( pack_sort[i] )
            pack_sort = []
            ratio_0 = sorted( ratio_0, reverse=True, key = lambda entry:entry["area"] )
            ratio_1 = sorted( ratio_1, reverse=True, key = lambda entry:entry["area"] )
            ratio_2 = sorted( ratio_2, reverse=True, key = lambda entry:entry["area"] )
            if len( ratio_0 ) >= len( ratio_2 ):
                pack_sort.extend( ratio_0 )
                pack_sort.extend( ratio_1 )
                pack_sort.extend( ratio_2 )
            else:
                pack_sort.extend( ratio_2 )
                pack_sort.extend( ratio_1 )
                pack_sort.extend( ratio_0 )

        # Variables
        start_x = min( self.List_Key( pack_sort, "bl" ) )
        start_y = min( self.List_Key( pack_sort, "bt" ) )

        # Reset Location
        for s in range( 0, len( pack_sort ) ):
            ox = start_x - pack_sort[s]["bw"]
            oy = start_y - pack_sort[s]["bh"]
            source.Move_Point( pack_sort, s, ox, oy )
            source.Move_Point( pin_list, pack_sort[s]["index"], ox, oy )
        QApplication.processEvents()

        # Variables
        points_x = list()
        points_y = list()
        grid_points = list()
        count = len( pack_sort )
        arranged = list()
        extended = list()
        extended.extend( pack_other )

        # Apply to Sort List
        for s in range( 0, count ):
            # Progress Bar
            if s % 5 == 0:
                source.ProgressBar_Value( s + 1 )
                QApplication.processEvents()
            # Stop Cycle
            if self.stop == True:
                message = "Continue Packing ?"
                loop = QMessageBox.question( QWidget(), "Imagine Board", message, QMessageBox.Yes, QMessageBox.Abort )
                if loop == QMessageBox.Abort:
                    break
                self.stop = False

            # Item
            item = pack_sort[s]
            bw = item["bw"]
            bh = item["bh"]
            pin_index = item["index"]

            # Points XY update
            if s == 0:
                # Extended
                extended = list()
                extended.extend( pack_other )
                len_ext = len( extended )

                # Grid Points
                grid_points = list()

                # Point
                px = start_x
                py = start_y
            else:
                # Lists
                psi = pack_sort[s-1]
                arranged.append( psi )
                extended.append( psi )
                len_ext = len( extended )

                # Variables
                len_grid = len( grid_points )
                end_x = max( self.List_Key( arranged, "br" ) )
                end_y = max( self.List_Key( arranged, "bb" ) )
                delta_x = end_x - start_x
                delta_y = end_y - start_y
                if delta_x >= delta_y:
                    side = delta_x
                else:
                    side = delta_y
                margin = 0.1 # enforces square when equal to zero
                square_x = start_x + side + bw * margin
                square_y = start_y + side + bh * margin

                # Control
                control = list()
                for g in range( 0, len_grid ):
                    # Grid Point with Item
                    gl = grid_points[g][0]
                    gr = gl + bw
                    gt = grid_points[g][1]
                    gb = gt + bh

                    valid = None
                    # State Delete
                    for e in range( 0, len_ext ):
                        # E Point
                        el = extended[e]["bl"]
                        er = extended[e]["br"]
                        et = extended[e]["bt"]
                        eb = extended[e]["bb"]

                        # Overlaps
                        overlap = (( round(gl,ru) >= round(el,ru) and round(gl,ru) < round(er,ru) ) and ( round(gt,ru) >= round(et,ru) and round(gt,ru) < round(eb,ru) ))
                        # Logic
                        if overlap == True:
                            valid = False
                            break
                    # State Consider Valid or None
                    if valid != False:
                        for e in range( 0, len_ext ):
                            # E Point
                            el = extended[e]["bl"]
                            er = extended[e]["br"]
                            et = extended[e]["bt"]
                            eb = extended[e]["bb"]

                            # Test Fit
                            fit = ( round(gl,ru) < round(er,ru) and round(gr,ru) > round(el,ru) ) and ( round(gt,ru) < round(eb,ru) and round(gb,ru) > round(et,ru) )
                            # Square Shape
                            if delta_x >= delta_y:square = gr >= square_x
                            else:square = gb >= square_y
                            # Contact is Valid
                            cl = ( round(gl,ru) == round(er,ru) ) and ( round(gt,ru) <= round(eb,ru) and round(gb,ru) >= round(et,ru) )
                            ct = ( round(gt,ru) == round(eb,ru) ) and ( round(gl,ru) <= round(er,ru) and round(gr,ru) >= round(el,ru) )
                            contact = cl == True or ct == True

                            # Logic
                            if fit == True or square == True:
                                valid = None
                                break
                            if contact == True:
                                valid = True

                    # Write
                    grid_points[g][2] = valid
                    if valid == True:
                        # Variables
                        box_x = ( start_x, end_x, gl, gr )
                        box_y = ( start_y, end_y, gt, gb )
                        min_x = min( box_x )
                        max_x = max( box_x )
                        min_y = min( box_y )
                        max_y = max( box_y )
                        width = abs( max_x - min_x )
                        height = abs( max_y - min_y )

                        # Calculations
                        if delta_x >= delta_y:
                            ca = gt - start_y
                            cb = gl - start_x
                            side = height
                        else:
                            ca = gl - start_x
                            cb = gt - start_y
                            side = width
                        index = g

                        # Control
                        control.append( {
                            "CA"     : ca,
                            "CB"     : cb,
                            "SIDE"   : side,
                            "INDEX"  : index,
                            } )

                # Control Sort
                k1 = "CA"
                k2 = "CB"
                sort = list()
                if len( control ) > 0:
                    # Control Selection
                    control = sorted( control, key=lambda entry:entry[k1] )
                    c0 = control[0][k1]
                    for item in control:
                        check = c0 #+ ( item["SIDE"] * 0.2 )
                        if item[k1] <= check:
                            sort.append( item )
                        else:
                            break
                    # Sort Control
                    sort = sorted( sort, key=lambda entry:entry[k2] )

                    # Variables
                    index = sort[0]["INDEX"]
                    grid_points[index][2] = False
                    # Point
                    px = grid_points[index][0]
                    py = grid_points[index][1]
                else:
                    self.stop = True
                    #QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( "Imagine Board | ERROR packer cycle" ) )

                # Garbage
                del control, sort

            # Grid Points with Item
            gl = px
            gr = px + bw
            gt = py
            gb = py + bh

            # Item Valid Points
            grid_points.append( [ gr, gt, None ] )
            grid_points.append( [ gl, gb, None ] )
            grid_points.append( [ gr, gb, None ] )
            if s != 0:
                points_x = [ start_x ]
                points_y = [ start_y ]
                points_x.extend( self.List_Key( extended, "br" ) )
                points_y.extend( self.List_Key( extended, "bb" ) )
                grid_points = self.Extra_Points( gl, gr, gt, gb, arranged, grid_points, start_x, start_y, source )
                del points_x, points_y

            # Deleted Invalid Grid Points
            remove = list()
            previous = list()
            for gp in grid_points:
                point = [ gp[0], gp[1] ]
                valid = gp[2]
                if ( valid == False or point in previous ):
                    remove.append( gp )
                else:
                    previous.append( point )
            for ri in remove:
                grid_points.remove( ri )
            del remove, previous

            # Move
            source.Move_Point( pack_sort, s, px, py )
            source.Move_Point( pin_list, pin_index, px, py )

            # Debug Points
            # source.p = grid_points.copy()
            # source.update()
            # QApplication.processEvents()
            # QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( str(s) ) )

        # Draw
        for s in range( 0 , count ):
            # Variables
            item = pack_sort[s]
            index = item["index"]
            px = item["bl"]
            py = item["bt"]
            # Render
            pin_list[index]["pack"] = False
            source.Pin_Draw_QPixmap( pin_list, index )

        # Finish
        area = self.Report_Area( pack_sort )
        return area

        # Garbage
        del pack_sort, pack_other, extended, grid_points

    # Support
    def List_Key( self, lista, key ):
        check = list()
        for i in lista:
            value = i[key]
            if value not in check:
                check.append( value )
        return check
    def Report_Area( self, lista ):
        # Lists
        min_x = min( self.List_Key( lista, "bl" ) )
        max_x = max( self.List_Key( lista, "br" ) )
        min_y = min( self.List_Key( lista, "bt" ) )
        max_y = max( self.List_Key( lista, "bb" ) )
        # Calculations
        w = abs( max_x - min_x )
        h = abs( max_y - min_y )
        area = w * h
        # Return
        return area
    def Extra_Points( self, gl, gr, gt, gb, arranged, grid_points, start_x, start_y, source ):
        # Variables
        pl = list(); pr = list(); pt = list(); pb = list()
        sw = list(); sh = list()
        i1 = list(); i2 = list(); i3 = list(); i4 = list()
        # Read
        lbl = self.List_Key( arranged, "bl" )
        lbr = self.List_Key( arranged, "br" )
        lbt = self.List_Key( arranged, "bt" )
        lbb = self.List_Key( arranged, "bb" )

        # Cycle
        for a in range( 0, len( arranged ) ):
            # E Point
            al = arranged[a]["bl"]
            ar = arranged[a]["br"]
            at = arranged[a]["bt"]
            ab = arranged[a]["bb"]

            # Projecting Points to Minor
            if ab <= gt:
                dist_y = gt - ab
                if gl >= al and gl <= ar:
                    pl.append( [ dist_y, gl, ab ] )
                if gr >= al and gr <= ar:
                    pr.append( [ dist_y, gr, ab ] )
            if ar <= gl:
                dist_x = gl - ar
                if gt >= at and gt <= ab:
                    pt.append( [ dist_x, ar, gt ] )
                if gb >= at and gb <= ab:
                    pb.append( [ dist_x, ar, gb ] )

            # Points to Self
            if at >= gb:
                dist_y = gb - at
                if ( al >= gl and al <= gr ):
                    px = Limit_Range( al, gl, gr )
                    py = gb
                    boolean = self.Connection_Valid( arranged, a, px, gb, px, at )
                    if boolean == True:
                        sh.append( [ dist_y, px, py ] )
                if ( ar >= gl and ar <= gr ):
                    px = Limit_Range( ar, gl, gr )
                    py = gb
                    boolean = self.Connection_Valid( arranged, a, px, gb, px, at )
                    if boolean == True:
                        sh.append( [ dist_y, px, py ] )
            if al >= gr:
                dist_x = gr - al
                if ( at >= gt and at <= gb ):
                    px = gr
                    py = Limit_Range( at, gt, gb )
                    boolean = self.Connection_Valid( arranged, a, gr, py, al, py )
                    if boolean == True:
                        sw.append( [ dist_x, px, py ] )
                if ( ab >= gt and ab <= gb ):
                    px = gr
                    py = Limit_Range( ab, gt, gb )
                    boolean = self.Connection_Valid( arranged, a, gr, py, al, py )
                    if boolean == True:
                        sw.append( [ dist_x, px, py ] )

            # Intersection Points
            if ar <= gl and ab <= gt: # top left
                dist = Trig_2D_Points_Distance( gl, gt, ar, ab )
                p = [ dist, [ gl, ab ], [ ar, gt ] ]
                i1.append( p )
            if al >= gr and ab <= gt: # top right
                dist = Trig_2D_Points_Distance( gr, gt, al, ab )
                p = [ dist, [ gr, ab ], [ al, gt ] ]
                i2.append( p )
            if ar <= gl and at >= gb: # bot left
                dist = Trig_2D_Points_Distance( gl, gb, ar, at )
                p = [ dist, [ gl, at ], [ ar, gb ] ]
                i3.append( p )
            if al >= gr and at >= gb: # bot right
                dist = Trig_2D_Points_Distance( gr, gb, al, at )
                p = [ dist, [ gr, at ], [ al, gb ] ]
                i4.append( p )

        # Sort Start
        grid_points.append( [ start_x, gb, None ] )
        grid_points.append( [ gr, start_y, None ] )
        # Sort Projected
        for lista in [ pl, pr, pt, pb ]:
            if len( lista ) > 0:
                lista.sort()
                item = lista[0]
                array = [ item[1], item[2], None ]
                grid_points.append( array )
        # Sort Self
        for lista in [ sw, sh ]:
            if len( lista ) > 0:
                lista.sort()
                for item in lista:
                    array = [ item[1], item[2], None ]
                    grid_points.append( array )
        # Sort Intersections
        for lista in [ i1, i2, i3, i4 ]:
            if len( lista ) > 0:
                lista.sort()
                item = lista[0]
                if item != 0:
                    a1 = [ item[1][0], item[1][1], None ]
                    a2 = [ item[2][0], item[2][1], None ]
                    grid_points.append( a1 )
                    grid_points.append( a2 )
        # Return
        return grid_points
    def Connection_Valid( self, lista, a, p1x, p1y, p2x, p2y ):
        # Variables
        boolean = True
        for i in range( 0, len( lista ) ):
            if i != a:
                # Read
                il = lista[i]["bl"]
                ir = lista[i]["br"]
                it = lista[i]["bt"]
                ib = lista[i]["bb"]
                # Checks
                check = ( ir > p1x and il < p2x ) and ( ib > p1y and it < p2y )
                if check == True:
                    boolean = False
                    break
        # Return
        return boolean
