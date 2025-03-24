grammar DrawShapes;

// Parser Rules
program: (statement)+ EOF;

statement: assignment
         | conditional
         | loop
         | shape
         | printStmt;

assignment: ID '=' STRING;

conditional: 'if' '(' condition ')' '{' (statement)* '}' 
             (elseIfPart)*
             (elsePart)?;

elseIfPart: 'else' 'if' '(' condition ')' '{' (statement)* '}';

elsePart: 'else' '{' (statement)* '}';

condition: ID '==' STRING;

loop: 'for' ID 'in' INT '{' (statement)* '}';

shape: triangleShape | circleShape;

triangleShape: 'triangle' ID point ',' point ',' point 'draw';

circleShape: 'circle' ID 'center' point 'radius' INT 'draw'?;

printStmt: 'print' STRING;

point: '(' INT ',' INT ')';

// Lexer Rules
ID: [a-zA-Z]+;
INT: [0-9]+;
STRING: '"' .*? '"';
WS: [ \t\r\n]+ -> skip;