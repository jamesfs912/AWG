from PyQt6.QtWidgets import QLineEdit

def findBestPrefix(val, prefixes):
    """ Finds the best prefix for a given value.
    
    Parameters:
    val (float): The value to find the best prefix for.
    prefixes (dict of str to float): The dictionary of prefixes to search through.
    
    Returns: 
    (float, str): The value with the best prefix, and the prefix itself."""
    for p in prefixes:
        n_val = val / prefixes[p]
        if n_val >= 1 and n_val < 1e3:
            return (n_val, p)
    return (val, "")
            
def endsWithLower(str, str2):
    """ Checks if a string ends with another string, ignoring case."""
    return str[-len(str2):].lower() == str2.lower()
        
def parseStringToVal(str_in, prefixes, expected_unit):
    """ Parses a string into a value.
    
    Parameters:
    str_in (str): The string to parse.
    prefixes (dict of str to float): The dictionary of prefixes to search through.
    expected_unit (str): The expected unit of the value.
    
    Returns:
    float: The value parsed from the string, or None if the string could not be parsed.
    """
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
    """Clamps a value to a given range.
    
    Parameters:
    val (float): The value to clamp.
    minVal (float): The minimum value of the range.
    maxVal (float): The maximum value of the range.
    
    Returns:
    float: The clamped value.
    """
    return float(min(maxVal, max(minVal, val)))
        
class Input(QLineEdit):
    def editFin(self):
        """Function called when the user has finished editing the text box. If no valid value is entered, the text box is reset to the previous value."""
        val = parseStringToVal(self.text(), self.prefixes, self.def_unit)
        if val is None:
            self.undo()
        else:
            self.setVal(val)
            
    def keyPressEvent(self, event):
        """Function called when a key is pressed while the text box is selected. If the up or down arrow keys are pressed, the value is incremented or decremented by 1, respectively.

        Parameters:
        event (QKeyEvent): The key event that was triggered.
        """
        if event.key() == 16777235: 
            self.setVal(self.value + 1)
        elif event.key() == 16777237: 
            self.setVal(self.value - 1)
        else:
            QLineEdit.keyPressEvent(self, event)
            
    def wheelEvent(self, event):
        self.setVal(self.value + event.angleDelta().y() / 120)
        event.accept()
            
    def setVal(self, val, runCallback = True):
        """ Sets the value of the text box.
        
        Parameters:
        val (float): The value to set the text box to.
        runCallback (bool): Whether or not to run the callback function after setting the value, defaults to True.
        """
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