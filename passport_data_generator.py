from faker import Faker
import json
import random
from datetime import datetime, timedelta

fake = Faker()

# Function to generate passport data
def generate_passport_data():
    # Generate a state/territory for Place of Birth
    state_territory = fake.state()

    # Format the dates as "dd MMM YYYY"
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%d %b %Y')
    date_of_issue = (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%d %b %Y')
    date_of_expiry = (datetime.now() + timedelta(days=random.randint(365, 1825))).strftime('%d %b %Y')

    # Generate a list of given names
    num_given_names = random.randint(1, 2)
    given_names = [fake.first_name() for _ in range(num_given_names)]

    # Format MRZ Line 1
    given_names_str = ''.join([f"{name}<" for name in given_names])

    
    

    passport_data = {
        "Type": "P",
        "Code": fake.random_element(elements=('GBR', 'USA', 'FRA', 'GER', 'CAN')),
        "PassportNumber": fake.random_int(min=100000000, max=999999999),
        "Surname": fake.last_name(),
        "GivenName": given_names,
        "Nationality": "UNITED STATES OF AMERICA",  # Change to USA for the specified format
        "DateOfBirth": date_of_birth,
        "PlaceOfBirth": f"{state_territory}, U.S.A",
        "Sex": fake.random_element(elements=('M', 'F')),
        "DateOfIssue": date_of_issue,
        "DateOfExpiration": date_of_expiry,
        "Authority": "United States",
        "Endorsements": f"SEE PAGE {fake.random_int(min=1, max=10)}",
    }

    # Generating two lines of MRZ in the specified format
   
    string1 = f"P<{passport_data['Code']}{passport_data['Surname']}<<{given_names_str}"
    string2 = '<' * (44 - len(string1))

    # Now, you can use string1 and string2 as needed
    mrz_line1 = f"{string1}{string2}"


    passport_number_digits = str(passport_data['PassportNumber']).zfill(9)
    dob_digits = datetime.strptime(passport_data['DateOfBirth'], '%d %b %Y').strftime('%y%m%d')
    expiry_digits = datetime.strptime(passport_data['DateOfExpiration'], '%d %b %Y').strftime('%y%m%d')

    
    random_digits = ''.join([str(fake.random_int(0, 9)) for _ in range(15)])
    
    mrz_line2 = f"{passport_number_digits}{fake.random_digit()}USA{dob_digits}{fake.random_digit()}{passport_data['Sex']}{expiry_digits}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}<{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}{fake.random_digit()}"

    return passport_data, mrz_line1, mrz_line2

# Generate and save 10 fake passport data as JSON
passport_list = []
for _ in range(10000):
    passport_data, mrz_line1, mrz_line2 = generate_passport_data()
    passport_data["MRZLine1"] = mrz_line1
    passport_data["MRZLine2"] = mrz_line2
    passport_list.append(passport_data)

# Save the generated passport data to a JSON file
with open("fake_passports.json", "w") as json_file:
    json.dump(passport_list, json_file, indent=2)

print("Fake passports saved to 'fake_passports.json'.")
