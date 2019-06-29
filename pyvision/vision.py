import os
import io
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from google.cloud import vision

def draw_rectangle(x1, y1, x2, y2):
    proportion = img_source.size[0] / (img_source.size[0] / img_source.size[1]) / 200
    width = 1 * int(proportion)
    outline_color = "green"
    draw = ImageDraw.Draw(img_source)
    draw.rectangle([(x1, y1), (x2, y2)], fill=None, outline=outline_color, width=width)
    del draw

def draw_text(x, y, objectname):
    fill_color = "white"
    shadow_color = "black"
    #image proportion calc, to fit any image size
    proportion = img_source.size[0] / (img_source.size[0] / img_source.size[1])
    fontsize = 2 * int(proportion/100)
    font = ImageFont.truetype("arial.ttf",size=fontsize)
    draw = ImageDraw.Draw(img_source)
    #draw background
    height = font.getsize(objectname)[1] 
    width = font.getsize(objectname)[0]
    draw.rectangle([(x, y), (x + width, y + height*1.4)], fill=shadow_color, outline=None, width=width)
    #draw text inside
    draw.text([x, y], objectname, fill=fill_color, font=font)
    del draw

#json key from google api
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="key.json"

#api client
client = vision.ImageAnnotatorClient()

#input image
path = "imagem4.jpg"
with io.open(path, "rb") as image_file:
    content = image_file.read()
#open image file
img_source = Image.open(path)

#object of type vision.types.Image
image = vision.types.Image(content=content)

#objects response from api
objects = client.object_localization(image=image).localized_object_annotations
#save response just for check if needed
with open("response.txt","w") as f:
    f.write(str(objects))

#creating a list/dictionarie of objects from response
objects_list = []
for _object in objects:
    bounding_poly_list = []
    for poly in _object.bounding_poly.normalized_vertices:
        bounding_poly_list.append({"x":poly.x, "y":poly.y})
    objects_list.append({"mid":_object.mid, "name":_object.name, "score":_object.score, "vertice": bounding_poly_list})

#choosing only objects with best score, if duplicated
unique_objects = objects_list.copy()
for _object in objects_list:
    for single in list(unique_objects):
        if _object["vertice"] == single["vertice"] and _object["score"] > single["score"]:
            unique_objects.remove(single)

#rename objects with order number, getting unique names list first
object_names = []
for _object in unique_objects:
    if _object['name'] not in object_names:
        object_names.append(_object['name'])
for name in object_names:
    count = 1
    for _object in unique_objects:
        if _object['name'] == name:
            _object['name'] = f"{name} 0{count}"
            count += 1

#plot unique objects response inside image
for _object in unique_objects:
    #draw object rectangle
    draw_rectangle(_object['vertice'][0]['x'] * img_source.size[0],
                   _object['vertice'][0]['y'] * img_source.size[1],
                   _object['vertice'][2]['x'] * img_source.size[0],
                   _object['vertice'][2]['y'] * img_source.size[1])
    print(f"Printed in image: '{_object['name']}'")
#separate to avoid rectangle over the text
for _object in unique_objects:
    #draw text rectangle
    draw_text(_object['vertice'][0]['x'] * img_source.size[0],
              _object['vertice'][0]['y'] * img_source.size[1],
              str(_object['name']))

# write to file
img_source.save("output_" + path)

print("\nAll done!\n")