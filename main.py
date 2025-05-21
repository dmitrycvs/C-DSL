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

# Example 1 - Basic shapes and conditionals (as in the original)
example1 = '''
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

# Example 2 - Polygon and transformations
example2 = '''
// Create a polygon
polygon P vertices ((0,0), (10,0), (10,10), (0,10)) draw

// Rotate the polygon
rotate P by 45 degrees draw

// Create a triangle and demonstrate reflection
triangle T (0,0), (20,0), (10,15) draw
reflect T by origin draw
'''

# Example 3 - Sophisticated loops and expressions
example3 = '''
// Create a circle using expressions
x = 10
y = 10
radius = 5 * 2
circle C center (x, y) radius radius draw

// Using a for loop to create multiple shapes
for i in range(1, 5) {
    circle Ci center (i * 10, 20) radius i * 2 draw
}

// Demonstrate a while loop
counter = 1
while (counter < 5) {
    rectangle R top-left (counter * 5, counter * 5) width 10 height 10 draw
    counter = counter + 1
}
'''

# Example 4 - Functions and feature additions
example4 = '''
// Define a function to create a triangle
function createTriangle(x, y, size) {
    triangle T (x, y), (x + size, y), (x + size/2, y + size) draw
    return T
}

// Use the function to create a triangle
myTriangle = createTriangle(0, 0, 30)

// Add geometric features to the triangle
add median to myTriangle from (0, 0)
add bisector to myTriangle from (0, 0)
add perpendicular to myTriangle from (0, 0)
'''

# Example 5 - Complex transformations
example5 = '''
// Create shapes
triangle T (0,0), (30,0), (15,20) draw
circle C center (50, 50) radius 15 draw
rectangle R top-left (10,10) width 20 height 15 draw
polygon P vertices ((70,10), (80,20), (90,10), (80,0)) draw

// Apply different transformations
scale T by 1.5 draw
translate C by (20, -10) draw
rotate R by 30 degrees draw
reflect P by y-axis draw
'''

parse_and_run(example1)
# parse_and_run(example2)
# parse_and_run(example3)
# parse_and_run(example4)
# parse_and_run(example5)