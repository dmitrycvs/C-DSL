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
    # Create input stream and lexer
    input_stream = InputStream(input_text)
    lexer = DrawShapesLexer(input_stream)
    
    # Add error listener to lexer
    error_listener = DSLErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    
    # Create token stream and parser
    stream = CommonTokenStream(lexer)
    parser = DrawShapesParser(stream)
    
    # Add error listener to parser
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    
    # Parse the input
    tree = parser.program()
    
    # Check if there were any errors during parsing
    if error_listener.has_error:
        print("Execution stopped due to syntax errors.")
        return
    
    # If no errors, run the visitor
    visitor = ShapeDrawer()
    visitor.visit(tree)

# Example usage
input_text = '''
shape = "triangle"

if (shape == "triangle") {
    for i in 3 {
        triangle A (0,0), (5,0), (3,4) draw
    }
} else if (shape == "circle") {
    circle B center (5,5) radius 10 draw
    triangle C (1,1), (6,1), (3,5) draw
} else {
    print "Unknown shape type"
}
'''

parse_and_run(input_text)