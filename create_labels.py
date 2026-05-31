import pickle

class_names = [
    "blackheads",
    "dark_spots",
    "whiteheads",
    "wrinkles"
]

with open("class_names.pkl", "wb") as f:
    pickle.dump(class_names, f)

print("class_names.pkl created")