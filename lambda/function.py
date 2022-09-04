def check_location(user_location, location_db):
    counter = 0
    for location in location_db:
        if location in user_location:
            counter += 1

    return counter

def check_farbe(user_farbe, farbe_db):
    counter = 0
    for farbe in farbe_db:
        if farbe in user_farbe:
            counter += 1

    return counter

def check_special(user_special, special_db):
    counter = 0
    for special in special_db:
        if special in user_special:
            counter += 1

    return counter
