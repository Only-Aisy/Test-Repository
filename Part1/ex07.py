# Dictionary containing names and ages
age = {'Hans': 24, 'Prag': 23, 'Bunyod': 18}

# TODO:
# 1. Print the whole dictionary
# 2. Print the age of 'Hans'
# 3. Change the age of 'Prag' to 30
# 4. Print the updated age of 'Prag'
# 5. Delete key-value pair of 'Bunyod' from the dictionary
# 6. Print the updated dictionary

# Insert your code
print(age)
print(age["Hans"])
age["Prag"]=30
print(age["Prag"])
age.pop("Bunyod")
print(age)