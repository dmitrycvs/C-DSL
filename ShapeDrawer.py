from antlr4 import *
from DrawShapesLexer import DrawShapesLexer
from DrawShapesParser import DrawShapesParser
from DrawShapesVisitor import DrawShapesVisitor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

class ShapeDrawer(DrawShapesVisitor):
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.shapes = {}
        self.currentFunctionReturn = None
        self.returnFlag = False

    def visitProgram(self, ctx):
        for stmt in ctx.statement():
            self.visit(stmt)
        return None

    def visitAssignment(self, ctx):
        var_name = ctx.ID().getText()
        if ctx.STRING():
            var_value = ctx.STRING().getText().strip('"')
        else:
            var_value = self.visit(ctx.expression())
        self.variables[var_name] = var_value
        return None

    def visitConditional(self, ctx):
        condition_result = self.visit(ctx.condition())
        if condition_result:
            for stmt in ctx.statement():
                self.visit(stmt)
                if self.returnFlag:
                    return self.currentFunctionReturn
            return None
        
        if ctx.elseIfPart():
            for else_if_part in ctx.elseIfPart():
                else_if_condition_result = self.visit(else_if_part.condition())
                if else_if_condition_result:
                    for stmt in else_if_part.statement():
                        self.visit(stmt)
                        if self.returnFlag:
                            return self.currentFunctionReturn
                    return None
        
        if ctx.elsePart():
            for stmt in ctx.elsePart().statement():
                self.visit(stmt)
                if self.returnFlag:
                    return self.currentFunctionReturn
        
        return None

    def visitCondition(self, ctx):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        comp = ctx.comparison().getText()
        
        if isinstance(left, str) and left.isdigit():
            left = float(left)
        if isinstance(right, str) and right.isdigit():
            right = float(right)
            
        if comp == '==':
            return left == right
        elif comp == '<':
            return left < right
        elif comp == '>':
            return left > right
        elif comp == '<=':
            return left <= right
        elif comp == '>=':
            return left >= right
        elif comp == '!=':
            return left != right
        
        return False

    def visitForLoop(self, ctx):
        loop_var = ctx.ID().getText()
        
        # Handle both simple 'for i in 5' and 'for i in range(1, 10)' syntax
        if ctx.INT():
            # Simple 'for i in 5' syntax
            repeat_count = int(ctx.INT().getText())
            start_val = 0
            end_val = repeat_count
        else:
            # 'for i in range(x, y)' syntax
            if len(ctx.expression()) == 1:
                start_val = 0
                end_val = int(self.visit(ctx.expression(0)))
            else:
                start_val = int(self.visit(ctx.expression(0)))
                end_val = int(self.visit(ctx.expression(1)))
        
        original_value = self.variables.get(loop_var, None)
        
        for i in range(start_val, end_val):
            self.variables[loop_var] = i
            for stmt in ctx.statement():
                self.visit(stmt)
                if self.returnFlag:
                    # Restore original variable value if it existed
                    if original_value is not None:
                        self.variables[loop_var] = original_value
                    else:
                        del self.variables[loop_var]
                    return self.currentFunctionReturn
        
        # Restore original variable value if it existed
        if original_value is not None:
            self.variables[loop_var] = original_value
        else:
            del self.variables[loop_var]
        
        return None

    def visitWhileLoop(self, ctx):
        while self.visit(ctx.condition()):
            for stmt in ctx.statement():
                self.visit(stmt)
                if self.returnFlag:
                    return self.currentFunctionReturn
        return None

    def visitFunctionDefinition(self, ctx):
        func_name = ctx.ID().getText()
        # Store function definition for later use
        self.functions[func_name] = ctx
        return None

    def visitFunctionCall(self, ctx):
        func_name = ctx.ID().getText()
        
        # Check if this is a built-in function
        if func_name == 'sin':
            arg = float(self.visit(ctx.expression(0)))
            return math.sin(math.radians(arg))
        elif func_name == 'cos':
            arg = float(self.visit(ctx.expression(0)))
            return math.cos(math.radians(arg))
        elif func_name == 'tan':
            arg = float(self.visit(ctx.expression(0)))
            return math.tan(math.radians(arg))
        elif func_name == 'sqrt':
            arg = float(self.visit(ctx.expression(0)))
            return math.sqrt(arg)
        
        # Check if it's a user-defined function
        if func_name in self.functions:
            func_ctx = self.functions[func_name]
            
            # Save current variables scope
            old_vars = self.variables.copy()
            
            # Create new scope for function
            self.variables = {}
            
            # Process function parameters
            if func_ctx.parameter() and ctx.expression():
                param_list = func_ctx.parameter()
                arg_list = ctx.expression()
                
                # Assign passed arguments to parameters
                for i in range(min(len(param_list), len(arg_list))):
                    param_name = param_list[i].ID().getText()
                    arg_value = self.visit(arg_list[i])
                    self.variables[param_name] = arg_value
                
                # Handle default parameters
                for i in range(len(arg_list), len(param_list)):
                    param = param_list[i]
                    param_name = param.ID().getText()
                    if param.literal():
                        default_value = self.visit(param.literal())
                        self.variables[param_name] = default_value
            
            # Reset return flag
            self.returnFlag = False
            self.currentFunctionReturn = None
            
            # Execute function body
            for stmt in func_ctx.statement():
                self.visit(stmt)
                if self.returnFlag:
                    break
            
            # Get return value
            return_value = self.currentFunctionReturn
            
            # Restore previous scope
            self.variables = old_vars
            self.returnFlag = False
            
            return return_value
        
        print(f"Error: Function '{func_name}' not defined")
        return None

    def visitReturnStmt(self, ctx):
        self.currentFunctionReturn = self.visit(ctx.expression())
        self.returnFlag = True
        return None

    def visitExpression(self, ctx):
        if len(ctx.term()) == 1 and not ctx.getChildCount() > 1:
            return self.visit(ctx.term(0))
        
        result = self.visit(ctx.term(0))
        for i in range(1, len(ctx.term())):
            op = ctx.getChild(i*2-1).getText()
            term_value = self.visit(ctx.term(i))
            
            # Ensure numeric values for operations
            if isinstance(result, str) and result.replace('.', '', 1).isdigit():
                result = float(result)
            if isinstance(term_value, str) and term_value.replace('.', '', 1).isdigit():
                term_value = float(term_value)
                
            if op == '+':
                result += term_value
            elif op == '-':
                result -= term_value
            elif op == '*':
                result *= term_value
            elif op == '/':
                result /= term_value
                
        return result

    def visitTerm(self, ctx):
        if ctx.ID():
            var_name = ctx.ID().getText()
            return self.variables.get(var_name, 0)
        elif ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        elif ctx.expression():
            return self.visit(ctx.expression())
        elif ctx.functionCall():
            return self.visit(ctx.functionCall())
        return 0

    def visitLiteral(self, ctx):
        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        elif ctx.STRING():
            return ctx.STRING().getText().strip('"')
        elif ctx.getText() == 'true':
            return True
        elif ctx.getText() == 'false':
            return False
        return None

    def visitShape(self, ctx):
        return self.visitChildren(ctx)

    def visitTriangleShape(self, ctx):
        name = ctx.ID().getText()
        points = [self.visit(point) for point in ctx.point()]
        # Store shape for potential transformations
        self.shapes[name] = {
            'type': 'triangle',
            'points': points
        }
        
        if ctx.getText().endswith('draw'):
            self.draw_triangle(name, points)
        return None

    def visitCircleShape(self, ctx):
        name = ctx.ID().getText()
        center = self.visit(ctx.point())
        radius = float(ctx.NUMBER().getText())
        # Store shape for potential transformations
        self.shapes[name] = {
            'type': 'circle',
            'center': center,
            'radius': radius
        }
        
        if 'draw' in ctx.getText():
            self.draw_circle(name, center, radius)
        return None

    def visitRectangleShape(self, ctx):
        name = ctx.ID().getText()
        top_left = self.visit(ctx.point())
        width = float(ctx.NUMBER(0).getText())
        height = float(ctx.NUMBER(1).getText())
        # Store shape for potential transformations
        self.shapes[name] = {
            'type': 'rectangle',
            'top_left': top_left,
            'width': width,
            'height': height
        }
        
        if 'draw' in ctx.getText():
            self.draw_rectangle(name, top_left, width, height)
        return None

    def visitPolygonShape(self, ctx):
        name = ctx.ID().getText()
        vertices = [self.visit(point) for point in ctx.point()]
        # Store shape for potential transformations
        self.shapes[name] = {
            'type': 'polygon',
            'vertices': vertices
        }
        
        if 'draw' in ctx.getText():
            self.draw_polygon(name, vertices)
        return None

    def visitTransformation(self, ctx):
        return self.visitChildren(ctx)

    def visitRotateTransform(self, ctx):
        shape_name = ctx.ID().getText()
        angle = float(ctx.NUMBER().getText())
        
        if shape_name in self.shapes:
            shape = self.shapes[shape_name]
            rotated_shape = self.rotate_shape(shape, angle)
            self.shapes[shape_name] = rotated_shape
            
            if 'draw' in ctx.getText():
                self.draw_shape(shape_name, rotated_shape)
        return None

    def visitScaleTransform(self, ctx):
        shape_name = ctx.ID().getText()
        scale_factor = float(ctx.NUMBER().getText())
        
        if shape_name in self.shapes:
            shape = self.shapes[shape_name]
            scaled_shape = self.scale_shape(shape, scale_factor)
            self.shapes[shape_name] = scaled_shape
            
            if 'draw' in ctx.getText():
                self.draw_shape(shape_name, scaled_shape)
        return None

    def visitTranslateTransform(self, ctx):
        shape_name = ctx.ID().getText()
        translation_vector = self.visit(ctx.point())
        
        if shape_name in self.shapes:
            shape = self.shapes[shape_name]
            translated_shape = self.translate_shape(shape, translation_vector)
            self.shapes[shape_name] = translated_shape
            
            if 'draw' in ctx.getText():
                self.draw_shape(shape_name, translated_shape)
        return None

    def visitReflectTransform(self, ctx):
        shape_name = ctx.ID().getText()
        reflection_type = ctx.getChild(3).getText()
        
        if shape_name in self.shapes:
            shape = self.shapes[shape_name]
            reflected_shape = None
            
            if reflection_type == 'x-axis':
                reflected_shape = self.reflect_shape_x_axis(shape)
            elif reflection_type == 'y-axis':
                reflected_shape = self.reflect_shape_y_axis(shape)
            elif reflection_type == 'origin':
                reflected_shape = self.reflect_shape_origin(shape)
            else:  # It's a point
                reflection_point = self.visit(ctx.point())
                reflected_shape = self.reflect_shape_point(shape, reflection_point)
            
            self.shapes[shape_name] = reflected_shape
            
            if 'draw' in ctx.getText():
                self.draw_shape(shape_name, reflected_shape)
        return None

    def visitAddFeatureTransform(self, ctx):
        shape_name = ctx.ID().getText()
        feature_type = ctx.getChild(1).getText()
        point = self.visit(ctx.point())
        
        if shape_name in self.shapes and self.shapes[shape_name]['type'] == 'triangle':
            shape = self.shapes[shape_name]
            if feature_type == 'median':
                self.add_median(shape_name, shape, point)
            elif feature_type == 'bisector':
                self.add_angle_bisector(shape_name, shape, point)
            elif feature_type == 'perpendicular':
                self.add_perpendicular(shape_name, shape, point)
        return None

    def visitPrintStmt(self, ctx):
        if ctx.STRING():
            message = ctx.STRING().getText().strip('"')
            print(message)
        else:
            result = self.visit(ctx.expression())
            print(result)
        return None

    def visitPoint(self, ctx):
        x = self.visit(ctx.expression(0))
        y = self.visit(ctx.expression(1))
        return (float(x), float(y))

    # Drawing methods
    def draw_triangle(self, name, points):
        x_vals, y_vals = zip(*points + [points[0]])
        plt.figure()
        plt.plot(x_vals, y_vals, 'bo-')
        plt.fill(x_vals, y_vals, alpha=0.3)
        plt.text(points[0][0], points[0][1], name, fontsize=12, color="red", fontweight="bold")
        plt.xlim(min(x_vals)-5, max(x_vals)+5)
        plt.ylim(min(y_vals)-5, max(y_vals)+5)
        plt.grid(True)
        plt.title(f"Triangle {name}")
        plt.show()

    def draw_circle(self, name, center, radius):
        plt.figure()
        circle = plt.Circle(center, radius, fill=True, alpha=0.3, edgecolor='blue', facecolor='blue')
        ax = plt.gca()
        ax.add_patch(circle)
        ax.plot(center[0], center[1], 'bo')
        plt.text(center[0], center[1], name, fontsize=12, color="red", fontweight="bold")
        plt.xlim(center[0] - radius - 5, center[0] + radius + 5)
        plt.ylim(center[1] - radius - 5, center[1] + radius + 5)
        plt.axis('equal')
        plt.grid(True)
        plt.title(f"Circle {name}")
        plt.show()

    def draw_rectangle(self, name, top_left, width, height):
        plt.figure()
        rect = patches.Rectangle(
            top_left,
            width,
            height,
            linewidth=1,
            edgecolor='blue',
            facecolor='blue',
            alpha=0.3
        )
        ax = plt.gca()
        ax.add_patch(rect)
        corners = [
            top_left,
            (top_left[0] + width, top_left[1]),
            (top_left[0] + width, top_left[1] + height),
            (top_left[0], top_left[1] + height)
        ]
        x_vals, y_vals = zip(*corners)
        plt.plot(x_vals, y_vals, 'bo-')
        plt.text(top_left[0] + width/2, top_left[1] + height/2, name, 
                 fontsize=12, color="red", fontweight="bold",
                 horizontalalignment='center', verticalalignment='center')
        plt.xlim(min(x_vals)-5, max(x_vals)+5)
        plt.ylim(min(y_vals)-5, max(y_vals)+5)
        plt.grid(True)
        plt.title(f"Rectangle {name}")
        plt.show()

    def draw_polygon(self, name, vertices):
        x_vals, y_vals = zip(*vertices + [vertices[0]])
        plt.figure()
        plt.plot(x_vals, y_vals, 'bo-')
        plt.fill(x_vals, y_vals, alpha=0.3)
        # Center of polygon
        center_x = sum(x for x, _ in vertices) / len(vertices)
        center_y = sum(y for _, y in vertices) / len(vertices)
        plt.text(center_x, center_y, name, fontsize=12, color="red", fontweight="bold")
        plt.xlim(min(x_vals)-5, max(x_vals)+5)
        plt.ylim(min(y_vals)-5, max(y_vals)+5)
        plt.grid(True)
        plt.title(f"Polygon {name}")
        plt.show()

    def draw_shape(self, name, shape):
        if shape['type'] == 'triangle':
            self.draw_triangle(name, shape['points'])
        elif shape['type'] == 'circle':
            self.draw_circle(name, shape['center'], shape['radius'])
        elif shape['type'] == 'rectangle':
            self.draw_rectangle(name, shape['top_left'], shape['width'], shape['height'])
        elif shape['type'] == 'polygon':
            self.draw_polygon(name, shape['vertices'])

    # Transformation methods
    def rotate_shape(self, shape, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        if shape['type'] == 'triangle':
            center_x = sum(x for x, _ in shape['points']) / 3
            center_y = sum(y for _, y in shape['points']) / 3
            
            rotated_points = []
            for px, py in shape['points']:
                # Translate point to origin
                tx = px - center_x
                ty = py - center_y
                
                # Rotate point
                rx = tx * cos_angle - ty * sin_angle
                ry = tx * sin_angle + ty * cos_angle
                
                # Translate back
                rotated_points.append((rx + center_x, ry + center_y))
                
            return {
                'type': 'triangle',
                'points': rotated_points
            }
            
        elif shape['type'] == 'rectangle':
            center_x = shape['top_left'][0] + shape['width'] / 2
            center_y = shape['top_left'][1] + shape['height'] / 2
            
            # Convert rectangle to polygon for rotation
            corners = [
                shape['top_left'],
                (shape['top_left'][0] + shape['width'], shape['top_left'][1]),
                (shape['top_left'][0] + shape['width'], shape['top_left'][1] + shape['height']),
                (shape['top_left'][0], shape['top_left'][1] + shape['height'])
            ]
            
            rotated_points = []
            for px, py in corners:
                # Translate point to origin
                tx = px - center_x
                ty = py - center_y
                
                # Rotate point
                rx = tx * cos_angle - ty * sin_angle
                ry = tx * sin_angle + ty * cos_angle
                
                # Translate back
                rotated_points.append((rx + center_x, ry + center_y))
                
            return {
                'type': 'polygon',
                'vertices': rotated_points
            }
            
        elif shape['type'] == 'circle':
            # Circles remain unchanged under rotation around their center
            return shape
            
        elif shape['type'] == 'polygon':
            center_x = sum(x for x, _ in shape['vertices']) / len(shape['vertices'])
            center_y = sum(y for _, y in shape['vertices']) / len(shape['vertices'])
            
            rotated_vertices = []
            for px, py in shape['vertices']:
                # Translate point to origin
                tx = px - center_x
                ty = py - center_y
                
                # Rotate point
                rx = tx * cos_angle - ty * sin_angle
                ry = tx * sin_angle + ty * cos_angle
                
                # Translate back
                rotated_vertices.append((rx + center_x, ry + center_y))
                
            return {
                'type': 'polygon',
                'vertices': rotated_vertices
            }
            
        return shape

    def scale_shape(self, shape, scale_factor):
        if shape['type'] == 'triangle':
            center_x = sum(x for x, _ in shape['points']) / 3
            center_y = sum(y for _, y in shape['points']) / 3
            
            scaled_points = []
            for px, py in shape['points']:
                # Calculate vector from center to point
                vx = px - center_x
                vy = py - center_y
                
                # Scale vector
                scaled_x = center_x + vx * scale_factor
                scaled_y = center_y + vy * scale_factor
                
                scaled_points.append((scaled_x, scaled_y))
                
            return {
                'type': 'triangle',
                'points': scaled_points
            }
            
        elif shape['type'] == 'rectangle':
            center_x = shape['top_left'][0] + shape['width'] / 2
            center_y = shape['top_left'][1] + shape['height'] / 2
            
            new_width = shape['width'] * scale_factor
            new_height = shape['height'] * scale_factor
            
            new_top_left = (
                center_x - new_width / 2,
                center_y - new_height / 2
            )
            
            return {
                'type': 'rectangle',
                'top_left': new_top_left,
                'width': new_width,
                'height': new_height
            }
            
        elif shape['type'] == 'circle':
            return {
                'type': 'circle',
                'center': shape['center'],
                'radius': shape['radius'] * scale_factor
            }
            
        elif shape['type'] == 'polygon':
            center_x = sum(x for x, _ in shape['vertices']) / len(shape['vertices'])
            center_y = sum(y for _, y in shape['vertices']) / len(shape['vertices'])
            
            scaled_vertices = []
            for px, py in shape['vertices']:
                # Calculate vector from center to vertex
                vx = px - center_x
                vy = py - center_y
                
                # Scale vector
                scaled_x = center_x + vx * scale_factor
                scaled_y = center_y + vy * scale_factor
                
                scaled_vertices.append((scaled_x, scaled_y))
                
            return {
                'type': 'polygon',
                'vertices': scaled_vertices
            }
            
        return shape

    def translate_shape(self, shape, translation_vector):
        tx, ty = translation_vector
        
        if shape['type'] == 'triangle':
            translated_points = [(px + tx, py + ty) for px, py in shape['points']]
            return {
                'type': 'triangle',
                'points': translated_points
            }
            
        elif shape['type'] == 'rectangle':
            new_top_left = (shape['top_left'][0] + tx, shape['top_left'][1] + ty)
            return {
                'type': 'rectangle',
                'top_left': new_top_left,
                'width': shape['width'],
                'height': shape['height']
            }
            
        elif shape['type'] == 'circle':
            new_center = (shape['center'][0] + tx, shape['center'][1] + ty)
            return {
                'type': 'circle',
                'center': new_center,
                'radius': shape['radius']
            }
            
        elif shape['type'] == 'polygon':
            translated_vertices = [(vx + tx, vy + ty) for vx, vy in shape['vertices']]
            return {
                'type': 'polygon',
                'vertices': translated_vertices
            }
            
        return shape

    def reflect_shape_x_axis(self, shape):
        if shape['type'] == 'triangle':
            reflected_points = [(px, -py) for px, py in shape['points']]
            return {
                'type': 'triangle',
                'points': reflected_points
            }
            
        elif shape['type'] == 'rectangle':
            return {
                'type': 'rectangle',
                'top_left': (shape['top_left'][0], -shape['top_left'][1] - shape['height']),
                'width': shape['width'],
                'height': shape['height']
            }
            
        elif shape['type'] == 'circle':
            return {
                'type': 'circle',
                'center': (shape['center'][0], -shape['center'][1]),
                'radius': shape['radius']
            }
            
        elif shape['type'] == 'polygon':
            reflected_vertices = [(vx, -vy) for vx, vy in shape['vertices']]
            return {
                'type': 'polygon',
                'vertices': reflected_vertices
            }
            
        return shape

    def reflect_shape_y_axis(self, shape):
        if shape['type'] == 'triangle':
            reflected_points = [(-px, py) for px, py in shape['points']]
            return {
                'type': 'triangle',
                'points': reflected_points
            }
            
        elif shape['type'] == 'rectangle':
            return {
                'type': 'rectangle',
                'top_left': (-shape['top_left'][0] - shape['width'], shape['top_left'][1]),
                'width': shape['width'],
                'height': shape['height']
            }
            
        elif shape['type'] == 'circle':
            return {
                'type': 'circle',
                'center': (-shape['center'][0], shape['center'][1]),
                'radius': shape['radius']
            }
            
        elif shape['type'] == 'polygon':
            reflected_vertices = [(-vx, vy) for vx, vy in shape['vertices']]
            return {
                'type': 'polygon',
                'vertices': reflected_vertices
            }
            
        return shape

    def reflect_shape_origin(self, shape):
        if shape['type'] == 'triangle':
            reflected_points = [(-px, -py) for px, py in shape['points']]
            return {
                'type': 'triangle',
                'points': reflected_points
            }
            
        elif shape['type'] == 'rectangle':
            return {
                'type': 'rectangle',
                'top_left': (-shape['top_left'][0] - shape['width'], -shape['top_left'][1] - shape['height']),
                'width': shape['width'],
                'height': shape['height']
            }
            
        elif shape['type'] == 'circle':
            return {
                'type': 'circle',
                'center': (-shape['center'][0], -shape['center'][1]),
                'radius': shape['radius']
            }
            
        elif shape['type'] == 'polygon':
            reflected_vertices = [(-vx, -vy) for vx, vy in shape['vertices']]
            return {
                'type': 'polygon',
                'vertices': reflected_vertices
            }
            
        return shape

    def reflect_shape_point(self, shape, point):
        px, py = point
        
        if shape['type'] == 'triangle':
            reflected_points = []
            for x, y in shape['points']:
                # Reflect through point: new_point = 2*point - old_point
                rx = 2 * px - x
                ry = 2 * py - y
                reflected_points.append((rx, ry))
                
            return {
                'type': 'triangle',
                'points': reflected_points
            }
            
        elif shape['type'] == 'rectangle':
            top_left = shape['top_left']
            # Reflect top-left corner
            new_top_left = (2 * px - top_left[0] - shape['width'], 2 * py - top_left[1] - shape['height'])
            
            return {
                'type': 'rectangle',
                'top_left': new_top_left,
                'width': shape['width'],
                'height': shape['height']
            }
            
        elif shape['type'] == 'circle':
            # Reflect center
            new_center = (2 * px - shape['center'][0], 2 * py - shape['center'][1])
            
            return {
                'type': 'circle',
                'center': new_center,
                'radius': shape['radius']
            }
            
        elif shape['type'] == 'polygon':
            reflected_vertices = []
            for x, y in shape['vertices']:
                rx = 2 * px - x
                ry = 2 * py - y
                reflected_vertices.append((rx, ry))
                
            return {
                'type': 'polygon',
                'vertices': reflected_vertices
            }
            
        return shape

    # Triangle-specific feature methods
    def add_median(self, name, shape, point):
        if shape['type'] != 'triangle':
            return
            
        # Find the vertex closest to the given point
        vertices = shape['points']
        closest_vertex = min(vertices, key=lambda v: ((v[0] - point[0])**2 + (v[1] - point[1])**2)**0.5)
        
        # Find the opposite side's midpoint
        vertex_index = vertices.index(closest_vertex)
        other_vertices = [vertices[i] for i in range(3) if i != vertex_index]
        midpoint = ((other_vertices[0][0] + other_vertices[1][0])/2, 
                   (other_vertices[0][1] + other_vertices[1][1])/2)
        
        # Draw the median
        plt.figure()
        plt.plot([closest_vertex[0], midpoint[0]], [closest_vertex[1], midpoint[1]], 'r-')
        
        # Also draw the triangle
        x_vals, y_vals = zip(*vertices + [vertices[0]])
        plt.plot(x_vals, y_vals, 'bo-')
        plt.fill(x_vals, y_vals, alpha=0.3)
        
        plt.text(vertices[0][0], vertices[0][1], f"{name} with median", 
                fontsize=12, color="red", fontweight="bold")
        plt.xlim(min(x_vals)-5, max(x_vals)+5)
        plt.ylim(min(y_vals)-5, max(y_vals)+5)
        plt.grid(True)
        plt.title(f"Triangle {name} with Median")
        plt.show()

    def add_angle_bisector(self, name, shape, point):
        if shape['type'] != 'triangle':
            return
            
        # Find the vertex closest to the given point
        vertices = shape['points']
        closest_vertex = min(vertices, key=lambda v: ((v[0] - point[0])**2 + (v[1] - point[1])**2)**0.5)
        
        # Get the other two vertices
        vertex_index = vertices.index(closest_vertex)
        other_indices = [(vertex_index + 1) % 3, (vertex_index + 2) % 3]
        other_vertices = [vertices[i] for i in other_indices]
        
        # Calculate vectors from the vertex to the other two vertices
        v1 = (other_vertices[0][0] - closest_vertex[0], other_vertices[0][1] - closest_vertex[1])
        v2 = (other_vertices[1][0] - closest_vertex[0], other_vertices[1][1] - closest_vertex[1])
        
        # Normalize vectors
        v1_norm = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_norm = math.sqrt(v2[0]**2 + v2[1]**2)
        
        v1_unit = (v1[0] / v1_norm, v1[1] / v1_norm)
        v2_unit = (v2[0] / v2_norm, v2[1] / v2_norm)
        
        # Calculate the bisector vector
        bisector = (v1_unit[0] + v2_unit[0], v1_unit[1] + v2_unit[1])
        bisector_norm = math.sqrt(bisector[0]**2 + bisector[1]**2)
        
        if bisector_norm > 0:
            bisector_unit = (bisector[0] / bisector_norm, bisector[1] / bisector_norm)
            
            # Determine length of bisector line (use the longest distance to keep it in proportion)
            max_dist = max(v1_norm, v2_norm)
            end_point = (closest_vertex[0] + bisector_unit[0] * max_dist,
                         closest_vertex[1] + bisector_unit[1] * max_dist)
            
            # Draw the angle bisector
            plt.figure()
            plt.plot([closest_vertex[0], end_point[0]], [closest_vertex[1], end_point[1]], 'r-')
            
            # Also draw the triangle
            x_vals, y_vals = zip(*vertices + [vertices[0]])
            plt.plot(x_vals, y_vals, 'bo-')
            plt.fill(x_vals, y_vals, alpha=0.3)
            
            plt.text(vertices[0][0], vertices[0][1], f"{name} with bisector", 
                    fontsize=12, color="red", fontweight="bold")
            plt.xlim(min(x_vals)-5, max(x_vals)+5)
            plt.ylim(min(y_vals)-5, max(y_vals)+5)
            plt.grid(True)
            plt.title(f"Triangle {name} with Angle Bisector")
            plt.show()

    def add_perpendicular(self, name, shape, point):
        if shape['type'] != 'triangle':
            return
            
        # Find the vertex closest to the given point
        vertices = shape['points']
        closest_vertex = min(vertices, key=lambda v: ((v[0] - point[0])**2 + (v[1] - point[1])**2)**0.5)
        
        # Get the other two vertices to define the opposite side
        vertex_index = vertices.index(closest_vertex)
        other_indices = [(vertex_index + 1) % 3, (vertex_index + 2) % 3]
        side_vertex1 = vertices[other_indices[0]]
        side_vertex2 = vertices[other_indices[1]]
        
        # Calculate the line parameters for the opposite side (ax + by + c = 0)
        a = side_vertex2[1] - side_vertex1[1]
        b = side_vertex1[0] - side_vertex2[0]
        c = side_vertex2[0] * side_vertex1[1] - side_vertex1[0] * side_vertex2[1]
        
        # Calculate the foot of the perpendicular
        # The perpendicular line through closest_vertex has slope -b/a if a!=0
        if a != 0:
            # Perpendicular line equation: y - vertex_y = (-b/a)(x - vertex_x)
            # Simplified: a(x - vertex_x) + b(y - vertex_y) = 0
            # ax - a*vertex_x + by - b*vertex_y = 0
            # ax + by = a*vertex_x + b*vertex_y
            
            # Intersection of perpendicular line with the opposite side
            # Solve the system of equations:
            # ax + by + c = 0 (opposite side)
            # ax + by = a*vertex_x + b*vertex_y (perpendicular line)
            
            # For numerical stability, use the fact that the dot product of the 
            # direction vector of the line and the perpendicular is zero
            line_dir = (side_vertex2[0] - side_vertex1[0], side_vertex2[1] - side_vertex1[1])
            line_length = math.sqrt(line_dir[0]**2 + line_dir[1]**2)
            
            if line_length > 0:
                # Normalize line direction
                line_dir = (line_dir[0] / line_length, line_dir[1] / line_length)
                
                # Vector from side_vertex1 to closest_vertex
                to_vertex = (closest_vertex[0] - side_vertex1[0], closest_vertex[1] - side_vertex1[1])
                
                # Project this vector onto the line
                projection_length = to_vertex[0] * line_dir[0] + to_vertex[1] * line_dir[1]
                
                # Calculate foot point
                foot_point = (side_vertex1[0] + projection_length * line_dir[0],
                              side_vertex1[1] + projection_length * line_dir[1])
                
                # Draw the perpendicular
                plt.figure()
                plt.plot([closest_vertex[0], foot_point[0]], [closest_vertex[1], foot_point[1]], 'r-')
                
                # Also draw the triangle
                x_vals, y_vals = zip(*vertices + [vertices[0]])
                plt.plot(x_vals, y_vals, 'bo-')
                plt.fill(x_vals, y_vals, alpha=0.3)
                
                plt.text(vertices[0][0], vertices[0][1], f"{name} with perpendicular", 
                        fontsize=12, color="red", fontweight="bold")
                plt.xlim(min(x_vals)-5, max(x_vals)+5)
                plt.ylim(min(y_vals)-5, max(y_vals)+5)
                plt.grid(True)
                plt.title(f"Triangle {name} with Perpendicular")
                plt.show()