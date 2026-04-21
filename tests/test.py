from PIL import Image

pil_img = Image.open("logo-noxia.png")

ratio = pil_img.height / pil_img.width
print(ratio)