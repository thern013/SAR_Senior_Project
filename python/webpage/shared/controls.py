counter = 0

def get_counter():
    global counter
    return counter

def set_counter(new_value):
    global counter
    counter = new_value

def increase_counter():
    global counter
    counter += 1
