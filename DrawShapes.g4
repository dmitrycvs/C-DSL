grammar DrawShapes;

// Parser Rules
program: (statement)+ EOF;

statement: assignment
         | conditional
         | forLoop
         | whileLoop
         | functionDefinition
         | functionCall
         | shape
         | transformation
         | printStmt
         | returnStmt;

assignment: ID '=' (expression | STRING);

conditional: 'if' '(' condition ')' '{' (statement)* '}' 
             (elseIfPart)*
             (elsePart)?;

elseIfPart: 'else' 'if' '(' condition ')' '{' (statement)* '}';

elsePart: 'else' '{' (statement)* '}';

condition: expression comparison expression;

comparison: '==' | '<' | '>' | '<=' | '>=' | '!=';

forLoop: 'for' ID 'in' ('range' '(' expression (',' expression)? ')' | INT) '{' (statement)* '}';

whileLoop: 'while' '(' condition ')' '{' (statement)* '}';

functionDefinition: 'function' ID '(' (parameter (',' parameter)*)? ')' '{' (statement)* returnStmt '}';

parameter: ID ('=' literal)?;

returnStmt: 'return' expression;

functionCall: ID '(' (expression (',' expression)*)? ')';

expression: term (('+' | '-' | '*' | '/') term)*;

term: ID | NUMBER | '(' expression ')' | functionCall;

literal: NUMBER | 'true' | 'false' | STRING;

shape: triangleShape | circleShape | rectangleShape | polygonShape;

triangleShape: 'triangle' ID point ',' point ',' point ('draw')?;

circleShape: 'circle' ID 'center' point 'radius' NUMBER ('draw')?;

rectangleShape: 'rectangle' ID 'top' '-' 'left' point 'width' NUMBER 'height' NUMBER ('draw')?;

polygonShape: 'polygon' ID 'vertices' '(' point (',' point)+ ')' ('draw')?;

transformation: 
      rotateTransform
    | scaleTransform
    | translateTransform
    | reflectTransform
    | addFeatureTransform;

rotateTransform: 'rotate' ID 'by' NUMBER ('degrees')? ('draw')?;

scaleTransform: 'scale' ID 'by' NUMBER ('draw')?;

translateTransform: 'translate' ID 'by' point ('draw')?;

reflectTransform: 'reflect' ID 'by' ('x-axis' | 'y-axis' | 'origin' | point) ('draw')?;

addFeatureTransform: 'add' ('median' | 'bisector' | 'perpendicular') 'to' ID 'from' point ('draw')?;

printStmt: 'print' (STRING | expression);

point: '(' expression ',' expression ')';

// Lexer Rules
ID: [a-zA-Z][a-zA-Z0-9_]*;
NUMBER: '-'?[0-9]+('.'[0-9]+)?;
INT: [0-9]+;
STRING: '"' .*? '"';
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\r'? '\n' -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;