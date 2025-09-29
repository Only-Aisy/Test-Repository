import random
# TODO: Refer to the objective and sample output and figure out your own code!
# Time to graduate :p
print ("What is your name?")
name = input()
adjective = ["Quirky", "Sassy", "Eccentric", "Terrified", "Boastful", "Amazing"]
animals = ["Quokka", "Pig", "Dog", "Tapir", "Dolphin", "Centipede"]
a =random.choice(adjective)
b =random.choice(animals)


print(f" {name} , your codename is: {a} {b}")

c = random.randrange(0, 100)
print(f"Your lucky number is: {c}")