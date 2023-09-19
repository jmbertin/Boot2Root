import turtle

window = turtle.Screen()
my_turtle = turtle.Turtle()

with open('turtle', 'r') as f:
    lines = f.readlines()

for line in lines:
    line_parts = line.split(' ')
    command = line_parts[0]

    if command == 'Tourne':
        direction = line_parts[1]
        degrees = int(line_parts[3])
        if direction == 'gauche':
            my_turtle.left(degrees)
        elif direction == 'droite':
            my_turtle.right(degrees)
    elif command == 'Avance':
        spaces = int(line_parts[1])
        my_turtle.forward(spaces)
    elif command == 'Recule':
       spaces = int(line_parts[1])
       my_turtle.backward(spaces)

turtle.done()
