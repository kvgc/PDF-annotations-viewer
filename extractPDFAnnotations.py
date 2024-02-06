from PyPDF2 import PdfFileReader
import subprocess
from pathlib import Path
import markdown2
import sys
import fitz
import glob
import os


import base64
#https://stackoverflow.com/questions/6375942/how-do-you-base-64-encode-a-png-image-for-use-in-a-data-uri-in-a-css-file
def image_to_data_url(filename):
    """
    This function is used to convert an image to a data url so that it can embedded in the html file
    """
    ext = filename.split('.')[-1]
    prefix = f'data:image/{ext};base64,'
    with open(filename, 'rb') as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode('utf-8')

filenames = glob.glob(str(sys.argv[1]) + "/*.pdf")

for filename in sorted(filenames):
    print(filename)
    try:
        reader = PdfFileReader(filename)
        readerMU = fitz.open(filename) 

        ## use pdfannots to extract the highlights
        subprocess.call(['pdfannots', filename,'--no-condense' ,'-s','highlights', '-o', 'pdfAnnots_foo.txt'])
        txt = Path('pdfAnnots_foo.txt').read_text()

        finalNote = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Annotations</title>
        </head>
        <body>
        <h3>Notes</h3>

        '''

        filename = "pdfanno://" + filename


        pageNum=0
        for page in reader.pages:
            pageMU = readerMU.load_page(pageNum)
            pageNum+=1

            for annots in pageMU.annots(types=[fitz.PDF_ANNOT_SQUARE]):
                squareAn = 1
                try:
                    rect = annots.rect  # Rect is a tuple (x0, y0, x1, y1)
                    pix = pageMU.get_pixmap(clip=rect, dpi=100)
                    # pix.save(f"p{pageNum}A{squareAn}.png")
                    pix.save("tmp.png")
                    IMGSRC = image_to_data_url("tmp.png")        
                    finalNote += f'''<a href="{filename}#page={str(pageNum)}"><img src="{IMGSRC}"></a><br>'''

                    # finalNote += f'''<a href="{filename}#page={str(pageNum)}"><img width=50% src="p{pageNum}A{squareAn}.png"><br></a>'''

                    squareAn += 1 
                except:
                    pass    

            
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    subtype = annot.get_object()["/Subtype"]
                    if subtype == "/Text":
                        finalNote+='''<br><a href="''' + filename  + '''#page=''' + str(pageNum) + '''">'''+ '''Page:'''+ str(pageNum)+'''</a>''' + annot.get_object()["/Contents"] +'''<br>'''
                
                    if subtype == "/FreeText":
                        finalNote+= '''<br><a href="''' + filename  + '''#page=''' + str(pageNum) + '''">'''+ '''Page-'''+ str(pageNum)+''':</a> ''' + annot.get_object()["/Contents"] +'''<br>'''
                    



        ## replace all the page 1, page 3 , etc from output to be urls instead. Assume maximum of 1000 pages
        ## Has to be reversed otherwise Page 100 might be mistaken for Page 10 or Page 1
        for i in reversed(range(1000)):
            string = "Page %d"%(i+1)
            string_updated =''' <a href="''' + filename  + '''#page=''' + '''%d">Page-%d'''%(i+1,i+1) + '''</a>'''
            txt = txt.replace(string, string_updated)


        finalNote += "<br>"+markdown2.markdown(txt)
        
        finalNote += ''' 
        </body>
        </html>
        '''
        f = open(f"annotations/{filename.split('/')[-1].split('.pdf')[0]}.html",'w')
        f.write(finalNote)
        f.close()

    except Exception as e:
        print(e)
        pass



# Specify the path to your folder containing HTML files
folder_path = "annotations/"


# Create the index.html file
import os
os.remove(os.path.join(folder_path, "index.html"))

# Get a list of all HTML files in the folder
html_files = [file for file in os.listdir(folder_path) if file.endswith(".html")]


with open(os.path.join(folder_path, "index.html"), "w") as index_file:
    # Write the HTML header with Bootstrap 5 included
    index_file.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1'>\n")
    index_file.write("<title>HTML Files Preview</title>\n")
    index_file.write(''' 
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.0.1/js/bootstrap.min.js" integrity="sha512-EKWWs1ZcA2ZY9lbLISPz8aGR2+L7JVYqBAYTq5AXgBkSjRSuQEGqWx8R1zAX16KdXPaCjOCaKE8MCpU0wcHlHA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
                      ''')
    index_file.write("<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>\n")
    index_file.write("</head>\n<body class='bg-light'>")  # Added a light background color

    # Container for previews with some additional styling
    index_file.write("<div class='container mt-5'>\n")

    # Generate previews for each HTML file
    for html_file in html_files:
        html_file_split = html_file.split('.html')[0]
        file_path = os.path.join(folder_path, html_file)
        with open(file_path, "r") as html_content:
            # Read a portion of the content as a preview (adjust as needed)
            preview_content = html_content.read()

            # Card-based design for each preview
            index_file.write("<div class='card mb-4'>\n")
            index_file.write("<div class='card-body'>\n")

            # Write a link to the file and its preview using Bootstrap classes
            index_file.write(f"<h5 class='card-title mb-3'>{html_file_split}")  # Added Bootstrap margin-bottom
            # index_file.write(f"<button type='button' class='btn btn-info' data-toggle='collapse' data-target='#{html_file.split('.html')[0]}' ><a href='{html_file}' target='_blank' class='btn btn-success'>Open</a></button>")            
            index_file.write(f"&nbsp;&nbsp;&nbsp;<button class='btn btn-primary' type='button' data-bs-toggle='collapse' data-bs-target='#{html_file_split}' aria-expanded='false' aria-controls='{html_file_split}'>Open</button></h5>")            
            index_file.write(f"<br><div class='collapse' id='{html_file_split}'><div class='card card-body'>{preview_content}</div></div>\n")  # Added Bootstrap margin-bottom

            index_file.write("</div>\n</div>\n")  # Close card-body and card divs

    index_file.write("</div>\n")  # Close the container

    # Close the HTML file
    index_file.write("</body></html>")


print("index.html generated successfully.")
