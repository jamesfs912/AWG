from PyQt6.QtWidgets import QLineEdit

def findBestPrefix(val, prefixes):
    #return (val, "")
    for p in prefixes:
        n_val = val / prefixes[p]
        if n_val >= 1 and n_val < 1e3:
            return (n_val, p)
    return (val, "")
            
def endsWithLower(str, str2):
    return str[-len(str2):].lower() == str2.lower()
        
def parseStringToVal(str_in, prefixes, expected_unit):
    str_in = str_in.replace(" ", "")
    
    if endsWithLower(str_in, expected_unit):
        str_in = str_in[:-len(expected_unit)]
        
    mag = 1
    for p in prefixes:
        if endsWithLower(str_in, p):
            str_in = str_in[:-len(p)]
            mag = prefixes[p]
    
    try:
        val = float(str_in)
    except Exception as e:
        return None
        
    return val * mag
    
def fixRange(val, minVal, maxVal):
    return float(min(maxVal, max(minVal, val)))
        
class Input(QLineEdit):
    def editFin(self):
        val = parseStringToVal(self.text(), self.prefixes, self.def_unit)
        if val is None:
            self.undo()
        else:
            self.setVal(val)
            
    def keyPressEvent(self, event):
       # print(str(event.key()))
        if event.key() == 16777235: #Key_Up: #what the hell is the fucking import for this?????
            self.setVal(self.value + 1)
        elif event.key() == 16777237: #Key_Down:
            self.setVal(self.value - 1)
        else:
            QLineEdit.keyPressEvent(self, event)
            
    def wheelEvent(self, event):
        self.setVal(self.value + event.angleDelta().y() / 120)
        event.accept()
            
    def setVal(self, val, runCallback = True):
        val = fixRange(val, self.range[0], self.range[1])
        self.value = val
        val, prefix = findBestPrefix(val, self.prefixes)
        self.setText(f"{val} {prefix}{self.def_unit}")
        if runCallback:
            self.callback_update()
        
    def __init__(self, callback_update, range, init_val, def_unit, prefixes = [], *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        self.editingFinished.connect(self.editFin)
        self.callback_update = callback_update
        self.range = range
        self.prefixes = prefixes
        self.def_unit = def_unit
        self.setVal(init_val)