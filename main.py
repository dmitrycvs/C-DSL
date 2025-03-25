from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from ShapeDrawer import ShapeDrawer
from DrawShapesLexer import DrawShapesLexer
from DrawShapesParser import DrawShapesParser
from DrawShapesVisitor import DrawShapesVisitor

class DSLErrorListener(ErrorListener):
    def __init__(self):
        super(DSLErrorListener, self).__init__()
        self.has_error = False
        self.error_message = ""

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.has_error = True
        self.error_message = f"Error at line {line}:{column} - {msg}"
        print(self.error_message)

def parse_and_run(input_text):
    input_stream = InputStream(input_text)
    lexer = DrawShapesLexer(input_stream)
    
    error_listener = DSLErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    
    stream = CommonTokenStream(lexer)
    parser = DrawShapesParser(stream)
    
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    
    tree = parser.program()
    
    if error_listener.has_error:
        print("Execution stopped due to syntax errors.")
        return
    
    visitor = ShapeDrawer()
    visitor.visit(tree)

input_text = '''
shape = "circle"

if (shape == "triangle") {
    triangle A (0,0), (5,0), (3,4) draw
} else if (shape == "circle") {
    circle B center (5,5) radius 10 draw
} else if (shape == "rectangle") {
    rectangle C top-left (2,2) width 8 height 4 draw
} else {
    print "Unknown shape type"
}
'''

parse_and_run(input_text)