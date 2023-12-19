from PIL import Image, ImageDraw, ImageFont
import json

def draw_text_with_box(draw, position, text, font, color=(0, 0, 0)):
    # Draw the text on the image
    #print('============================================================================')
    #draw.text(position, text, color, font=font)
    spacing=5
    x, y = position
    for s in text:
        # Draw the current character
        draw.text((x, y), s, font=font, fill='black')

        # Calculate bounding box for the current character
        bb = draw.textbbox((x, y), s, font=font)

        # Draw a rectangle around the current character
        #draw.rectangle(bb, outline=color)
        #print(bb)

        # Update x-coordinate for the next character with spacing
        x = bb[2] - spacing
    # Get the bounding box coordinates for the drawn text
    bbox = (position[0], position[1], x, bb[3])

    
    # Draw a rectangle around the text
    #draw.rectangle(bbox, outline=color)
    
    
    return bbox

def convert_bbox_to_four_points(bbox):
    x1, y1, x2, y2 = bbox
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def convert_bbox_to_string(bbox):
    x1, y1, x2, y2 = bbox
    return f"{x1},{y1},{x2},{y1},{x2},{y2},{x1},{y2}"

def save_box_information(image_id, filename, boxes):
    # Create the 'boxes_trans' directory if it doesn't exist
   

    tsv_filename = f"dataset/boxes_trans/{filename.replace('.png', '.tsv')}"

    with open(tsv_filename, 'w') as tsv_file:
        
        i=0
        for box in boxes:
            box_coords = convert_bbox_to_string(box['bbox'])
            tsv_file.write(f"{i}\t{box_coords}\t{box['text']}\t{box['data_type']}\n")
            i += 1

# Load the first 10 passports from the JSON file
with open("fake_passports.json", "r") as json_file:
    passports = json.load(json_file)

dir = "v3"
j = 0

for passport in passports:
    #print(passport)

    # Load the base image
    base_image = Image.open('passport_template.png')
    draw = ImageDraw.Draw(base_image)

    # Use an OCR-B font
    ocrb_font_path = 'OCRB.otf'
    font = ImageFont.truetype(ocrb_font_path, 27)
   
        #change coordinates
   
    type_bbox = draw_text_with_box(draw, (418, 102),passport['Type'], font)
    #print(f"Type Bounding Box: {type_bbox}")

    code_bbox = draw_text_with_box(draw, (560, 102),passport['Code'], font)
    #print(f"Code Bounding Box: {code_bbox}")

    passport_number_text = str(passport['PassportNumber'])
    passport_number_bbox = draw_text_with_box(draw, (800, 102), passport_number_text, font)
    #print(f"Passport Number Bounding Box: {passport_number_bbox}")

     # Draw passport information on the image and get bounding box coordinates
    surname_text = passport['Surname']
    surname_bbox = draw_text_with_box(draw, (365, 155), surname_text, font)
    #print(f"Surname Bounding Box: {surname_bbox}")

    given_name_text = ' '.join(passport['GivenName'])
    given_name_bbox = draw_text_with_box(draw, (365, 215), given_name_text, font)
    #print(f"Given Name Bounding Box: {given_name_bbox}")
    
    nationality_bbox = draw_text_with_box(draw, (365, 270), passport['Nationality'], font)
    #print(f"nationality Bounding Box: {nationality_bbox}")
    
    dob_text = passport['DateOfBirth']
    dob_bbox = draw_text_with_box(draw, (365, 325), dob_text, font)
    #print(f"Date of Birth Bounding Box: {dob_bbox}")

    PlaceOfBirth_bbox = draw_text_with_box(draw, (365, 380),passport['PlaceOfBirth'], font)
    #print(f"PlaceOfBirth Bounding Box: {PlaceOfBirth_bbox}")

    
    sex_bbox = draw_text_with_box(draw, (900, 380),passport['Sex'], font)
    #print(f"Sex Bounding Box: {sex_bbox}")

    issue_date_text = passport['DateOfIssue']
    issue_date_bbox = draw_text_with_box(draw, (365, 435), issue_date_text, font)
    #print(f"Date of Issue Bounding Box: {issue_date_bbox}")

    Authority_bbox = draw_text_with_box(draw, (820, 435),passport['Authority'], font)
    #print(f"Authority Bounding Box: {Authority_bbox}")
    
    expire_date_bbox = draw_text_with_box(draw, (365, 490), passport['DateOfExpiration'], font)
    #print(f"Date of Expiry Bounding Box: { expire_date_bbox}")
    
    Endorsements_bbox = draw_text_with_box(draw, (365, 545),passport['Endorsements'], font)
    #print(f"Endorsements Bounding Box: {Endorsements_bbox}")

    # Save the image with a unique filename
    filename = f"dataset/images/image_{j}.png"
    base_image.save(filename)
    
    
    boxes = [
        {'bbox': type_bbox, 'text': passport['Type'], 'data_type': 'type'},
        {'bbox': code_bbox, 'text': passport['Code'], 'data_type': 'code'},
        {'bbox': passport_number_bbox, 'text': passport['PassportNumber'], 'data_type': 'passport_number'},
        {'bbox': surname_bbox, 'text': surname_text, 'data_type': 'Surname'},
        {'bbox': given_name_bbox, 'text': given_name_text, 'data_type': 'GivenName'},
        {'bbox': nationality_bbox, 'text': passport['Nationality'], 'data_type': 'nationality'},
        {'bbox': dob_bbox, 'text': passport['DateOfBirth'], 'data_type': 'date_of_birth'},
        {'bbox': PlaceOfBirth_bbox, 'text': passport['PlaceOfBirth'], 'data_type': 'place_of_birth'},
        {'bbox': sex_bbox, 'text': passport['Sex'], 'data_type': 'sex'},
        {'bbox': issue_date_bbox, 'text': passport['DateOfIssue'], 'data_type': 'date_of_issue'},
        {'bbox': Authority_bbox, 'text': passport['Authority'], 'data_type': 'authority'},
        {'bbox': expire_date_bbox, 'text': passport['DateOfExpiration'], 'data_type': 'date_of_expiration'},
	{'bbox': Endorsements_bbox, 'text': passport['Endorsements'], 'data_type': 'endorsements'},
        
        # Add more boxes for other fields as needed
     ]
    
    filename2=f"image_{j}.png"
    save_box_information(j, filename2, boxes)

    j += 1
