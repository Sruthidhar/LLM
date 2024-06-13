import random

def generate_data(criteria):
    # Generate synthetic data based on the given criteria
    data = []
    for _ in range(10):  # Generate 10 data points as an example
        # Generate some random data based on the criteria
        if criteria == "even":
            value = random.randint(1, 100) * 2
        elif criteria == "odd":
            value = random.randint(1, 100) * 2 + 1
        else:
            value = random.randint(1, 100)
        data.append(value)
    return data

def process_data(data):
    # Process the generated data
    for value in data:
        # Do something with each value, like printing or saving to a file
        print(value)

def main():
    # Get criteria for generating data
    criteria = input("Enter criteria for generating data (even, odd, or any): ")

    # Generate data based on criteria
    data = generate_data(criteria)

    if data:
        # Process the generated data
        process_data(data)
    else:
        print("Failed to generate data.")

if __name__ == "__main__":
    main()
