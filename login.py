from json import load
from requests import session
from requests.utils import requote_uri
from re import findall, M as multiline
import wget
from pathlib import Path
import os
import shutil
from bs4 import BeautifulSoup

host = "https://login.iiit.ac.in/cas/login"
service = "https://courses.iiit.ac.in/login/index.php?authCAS=CAS"

extensions={
    "https://courses.iiit.ac.in/theme/image.php/boost/core/1632311829/f/pdf-24":"pdf",
    "https://courses.iiit.ac.in/theme/image.php/boost/assign/1632311829/icon":"assignment",
    "https://courses.iiit.ac.in/theme/image.php/boost/core/1632311829/f/mpeg-24":"lecture",
    "https://courses.iiit.ac.in/theme/image.php/boost/quiz/1632311829/icon":"quiz",
    "https://courses.iiit.ac.in/theme/image.php/boost/folder/1632311829/icon":"folder",
    "https://courses.iiit.ac.in/theme/image.php/boost/url/1632311829/icon":"url",
    "https://courses.iiit.ac.in/theme/image.php/boost/core/1632311829/f/spreadsheet-24":"xl",
    "https://courses.iiit.ac.in/theme/image.php/boost/core/1632311829/f/archive":"archive",
    "https://courses.iiit.ac.in/theme/image.php/boost/core/1632311829/f/archive":"anything"
}


# get credentials
try:
    with open("secrets.json", "r") as f:
        secrets = load(f)
        username = secrets.get("username") or input("username: ")
        password = secrets.get("password") or input("password: ")
except:
    username = input("username: ")
    password = input("password: ")

# initiate session
s = session()
page = s.get(host).text

# get execution attribute
execution_re = r'<input type="hidden" name="execution" value="([^<]*)"/>'
execution = findall(execution_re, page, multiline)[0]

# log user in and store cookies in session
login = s.post(
    requote_uri(f"{host}?service={service}"),
    data={
        "username": username,
        "password": password,
        "execution": execution,
        "_eventId": "submit",
        "geolocation": "",
    },
)

# open moodle
course_id = 2275  # input("Course ID: ")
service_COURSEPAGE = f"https://courses.iiit.ac.in/course/view.php?id={course_id}"
#temp="https://courses.iiit.ac.in/pluginfile.php/120962/mod_resource/content/1/IntroLecture_L1_L2_04_07Jan2021_moodle.pdf"
#temp2="https://courses.iiit.ac.in/pluginfile.php/120963/mod_resource/content/1/Chapter2-L2_3_4_SignalsAndSystems_07_11_18Jan2021_CLASS.pdf"
course_page = s.get(service_COURSEPAGE)

soup_main=BeautifulSoup(course_page.content,"lxml")
head_datas = [head.get_text().strip().split(": ") for head in soup_main.find_all('head')]

localpath=f'./course_{head_datas[0][1]}'
if os.path.exists(localpath):
    shutil.rmtree(localpath)   
os.mkdir(localpath)

page_text=course_page.content.decode('UTF-8')


# link="https://courses.iiit.ac.in/mod/resource/view.php?id=25706"
# pdf_temp=s.get(link)
# pdf_local=f"{localpath}/pdf.pdf"
# with open(pdf_local,"wb+") as f:
#     f.write(pdf_temp.content)

# page_text=page_text.replace(link,"pdf.pdf",1)

# with open(f"{localpath}/main_page.html","w+") as f:
#     f.write(page_text)


# all_href=findall(r'https://courses.iiit.ac.in/mod/assign/view.php.*',page_text,multiline)
# for i in all_href:
#     print(i+"\n\n\n")


assignments = findall(
   r"https://courses.iiit.ac.in/mod/(?:resource|quiz|assign|folder|url)/view.php\?id=\d+",
   course_page.text,
   multiline,
)
allmodulenumbers=[]
for i in assignments:
    allmodulenumbers.append(i.split("id=")[1])

icons=[]
for i in allmodulenumbers:
    mod=soup_main.find(id=f'module-{i}')
    for j in mod:
        if j.img['src'] not in icons: 
            icons.append(j.img['src'])
for i in icons:
    print(i)

#print(mod.find_all("div"))


#wget.download("https://courses.iiit.ac.in/pluginfile.php/120962/mod_resource/content/1/IntroLecture_L1_L2_04_07Jan2021_moodle.pdf")

# DEMO: write markup response to file
#with open("moodle.pdf", "w") as f:
#    f.write_bytes(course_page.content)
# filename=Path("moodle.pdf")
# filename.write_bytes(course_page.content)
# course_page = s.get(temp2)
# filename=Path("moodle1.pdf")
# filename.write_bytes(course_page.content)
# print("done, open 'moodle.html' on a browser.")
