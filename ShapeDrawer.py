from antlr4 import *
from DrawShapesLexer import DrawShapesLexer
from DrawShapesParser import DrawShapesParser
from DrawShapesVisitor import DrawShapesVisitor
import matplotlib.pyplot as plt

class ShapeDrawer(DrawShapesVisitor):
    def __init__(self):
        self.variables = {}  # Dictionary to store variables

    def visitProgram(self, ctx):
        for stmt in ctx.statement():
            self.visit(stmt)
        return None

    def visitAssignment(self, ctx):
        var_name = ctx.ID().getText()
        var_value = ctx.STRING().getText().strip('"')  # Remove quotes
        self.variables[var_name] = var_value
        return None

    def visitConditional(self, ctx):
        # First, evaluate the main condition
        condition_result = self.visit(ctx.condition())
        
        if condition_result:
            # Execute the if block statements
            for stmt in ctx.statement():
                self.visit(stmt)
            return None
        
        # Check if there are any else-if parts
        if ctx.elseIfPart():
            for else_if_part in ctx.elseIfPart():
                else_if_condition_result = self.visit(else_if_part.condition())
                if else_if_condition_result:
                    # Execute the else-if block statements
                    for stmt in else_if_part.statement():
                        self.visit(stmt)
                    return None
        
        # If no condition matched, check for else part
        if ctx.elsePart():
            # Execute the else block statements
            for stmt in ctx.elsePart().statement():
                self.visit(stmt)
        
        return None

    def visitCondition(self, ctx):
        var_name = ctx.ID().getText()
        expected_value = ctx.STRING().getText().strip('"')
        actual_value = self.variables.get(var_name, "")
        result = actual_value == expected_value
        print(f"DEBUG - Condition: {var_name} == {expected_value}, actual value: '{actual_value}', result: {result}")
        return result

    def visitLoop(self, ctx):
        loop_var = ctx.ID().getText()
        repeat_count = int(ctx.INT().getText())
        
        for i in range(repeat_count):
            self.variables[loop_var] = str(i)
            for stmt in ctx.statement():
                self.visit(stmt)
        
        return None

    def visitShape(self, ctx):
        name = ctx.ID().getText()
        points = [self.visit(point) for point in ctx.point()]
        print(f"DEBUG - Drawing triangle {name} with points {points}")
        self.draw_triangle(name, points)
        return None

    def visitPrintStmt(self, ctx):
        message = ctx.STRING().getText().strip('"')
        print(f"DEBUG - Executing print statement: '{message}'")
        print(message)
        return None

    def visitPoint(self, ctx):
        x = int(ctx.INT(0).getText())
        y = int(ctx.INT(1).getText())
        return (x, y)

    def draw_triangle(self, name, points):
        x_vals, y_vals = zip(*points + [points[0]])  # Close the triangle
        plt.figure()
        plt.plot(x_vals, y_vals, 'bo-')  # Blue dots and lines
        plt.fill(x_vals, y_vals, alpha=0.3)  # Fill with transparency
        plt.text(points[0][0], points[0][1], name, fontsize=12, color="red", fontweight="bold")
        plt.xlim(min(x_vals)-1, max(x_vals)+1)
        plt.ylim(min(y_vals)-1, max(y_vals)+1)
        plt.grid(True)
        plt.show()