import tkinter
from tkinter import *
import base64
import hashlib
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from Cryptodome.Cipher import AES
from Cryptodome import Random
from PIL import Image, ImageDraw
import os
import sys
from Cryptodome.Random import random
import urllib.request
import requests
xrange = range

Window = Tk()
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
def encrypt(filename, key):
    infile = open(filename, "r")
    plain_text = infile.read()
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    plain_text = pad(plain_text)
    iv = Random.new().read(AES.block_size)
    plain_text = plain_text.encode()
    plain_text = bytearray(plain_text)
    cipher = AES.new(private_key, AES.MODE_CFB, iv)
    return base64.b64encode(iv + cipher.encrypt(plain_text))

def decrypt(cipher_text, key):
    private_key = hashlib.sha256(key.encode("utf-8")).digest()
    cipher_text = base64.b64decode(cipher_text)
    iv = cipher_text[:16]
    cipher = AES.new(private_key, AES.MODE_CFB, iv )
    return unpad(cipher.decrypt(cipher_text[16:]))

def encrypt_image(infile):
    if not os.path.isfile(infile):
        print("That file does not exist.")
        exit()

    img = Image.open(infile)
    f, e = os.path.splitext(infile)
    out_filename_A = f+"_A.png"
    out_filename_B = f+"_B.png"
    img = img.convert('1')  # convert image to 1 bit
    # Prepare two empty slider images for drawing
    width = img.size[0]*2
    height = img.size[1]*2
    out_image_A = Image.new('1', (width, height))
    out_image_B = Image.new('1', (width, height))
    draw_A = ImageDraw.Draw(out_image_A)
    draw_B = ImageDraw.Draw(out_image_B)
    
    # There are 6(4 choose 2) possible patterns and it is too late for me to think in binary and do these efficiently
    patterns = ((1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1),
                (0, 1, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1))
    # Cycle through pixels
    for x in xrange(0, int(width/2)):
        for y in xrange(0, int(height/2)):
            pixel = img.getpixel((x, y))
            pat = random.choice(patterns)
            # A will always get the pattern
            draw_A.point((x*2, y*2), pat[0])
            draw_A.point((x*2+1, y*2), pat[1])
            draw_A.point((x*2, y*2+1), pat[2])
            draw_A.point((x*2+1, y*2+1), pat[3])
            if pixel == 0:  # Dark pixel so B gets the anti pattern
                draw_B.point((x*2, y*2), 1-pat[0])
                draw_B.point((x*2+1, y*2), 1-pat[1])
                draw_B.point((x*2, y*2+1), 1-pat[2])
                draw_B.point((x*2+1, y*2+1), 1-pat[3])
            else:
                draw_B.point((x*2, y*2), pat[0])
                draw_B.point((x*2+1, y*2), pat[1])
                draw_B.point((x*2, y*2+1), pat[2])
                draw_B.point((x*2+1, y*2+1), pat[3])
    out_image_A.save(out_filename_A, 'PNG')
    out_image_B.save(out_filename_B, 'PNG')
    print("Done.")
    
def decrypt_image(infile1, infile2):
    img1 = Image.open(infile1, mode='r')
    img2 = Image.open(infile2, mode='r')
    img1.paste(img2, (0,0), mask = img2)
    img1 = img1.convert(mode=None, matrix=None, dither=None, palette=0, colors=256)
    #out_image.save(infile1,'png')
    #img1.show()
    img1.save('hello.png')
    #img1.show()
lbl1=Label(Window, text="Choose file to encrypt: ")
lbl1.place(x=80,y=60)
txt1=Entry()
txt1.place(x=250,y=60)

lbl2=Label(Window, text="Enter Key")
lbl2.place(x=80,y=130)
txt2=Entry()
txt2.place(x=250,y=130)

lbl3=Label(Window, text="Choose file to decrypt: ")
lbl3.place(x=80,y=200)
txt3=Entry()
txt3.place(x=250,y=200)

lbl4=Label(Window, text="Enter Key")
lbl4.place(x=80,y=270)
txt4=Entry()
txt4.place(x=250,y=270)

n = tkinter.StringVar()
files = ttk.Combobox(Window, width = 27, textvariable = n)
files.place(x=100,y=400)
files['values'] = (' ', ' Text', ' Image')
files['state'] = 'readonly'
  

def choose_file(event):
    txt1.delete(0,'end')
    filetypes = (('text files', '*.txt'),('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
    txt1.insert(END,filename)

def encrypt_event(event):
    m = files.get()
    if(m==' Text'):
        if not txt1.get():
            messagebox.showinfo("Error", "Enter all details.")
        elif not txt2.get():
            messagebox.showinfo("Error", "Enter all details.")
        else:
            filename=txt1.get()
            key = txt2.get()
            array = encrypt(filename, key)
            array = array.decode('utf-8')
            print(array)
            b=urllib.request.urlopen('https://api.thingspeak.com/update?api_key=EGNJ2ZRY1IJ6QM7J&field1='+array)
            messagebox.showinfo("ENC", "Successfully Encrypted")
    elif(m==' Image'):
        if not txt1.get():
            messagebox.showinfo("Error", "Enter all details.")
        else:
            infile = txt1.get()
            encrypt_image(infile)
            messagebox.showinfo("ENC", "Successfully Encrypted")
    
    else:
        messagebox.showinfo("Error", "Please Select the type of file")
def choose_file_dec(event):
    m = files.get()
    txt3.delete(0,'end')
    filetypes = (('text files', '*.txt'),('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
    txt3.insert(END,filename)
#    m = files.get()
    if(m==' Image'):
        global txt5
        lbl5=Label(Window, text="Second File: ")
        lbl5.place(x=80,y=230)
        txt5=Entry()
        txt5.place(x=250,y=230)
        messagebox.showinfo("File", "Choose Another Image for Decryption")
        txt5.delete(0,'end')
        filetypes = (('text files', '*.txt'),('All files', '*.*'))
        filename = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
        txt5.insert(END,filename)
        
        
def decrypt_event(event):

    msg=requests.get("https://thingspeak.com/channels/1741325/field/1")
    msg=msg.json()['feeds'][-1]['field1']
    m = files.get()
    if(m==' Text'):
        if not txt3.get():
            messagebox.showinfo("Error", "Enter all details.")
        elif not txt4.get():
            messagebox.showinfo("Error", "Enter all details.")
        else:
            
            filename=txt3.get()
            key = txt4.get()
            print(msg)
            out = decrypt(msg,key)
            print(out)
            outputFile = open(filename,'wb')
            outputFile.write(out)
            outputFile.close()
            messagebox.showinfo("DEC", "Successfully Decrypted")

    elif(m==' Image'):
        if not txt3.get():
            messagebox.showinfo("Error", "Please Select Image1.")
        elif not txt5.get():
            messagebox.showinfo("Error", "Please Select Image2.")
        else:
            infile1=txt3.get()
            infile2=txt5.get()
            decrypt_image(infile1,infile2)
            messagebox.showinfo("DEC", "Successfully Decrypted")
            
    else:
        messagebox.showinfo("Error", "Please Select the type of file")
btn1=Button(Window, text="Choose Files", fg='blue')
btn1.bind('<Button-1>', choose_file)
btn1.place(x=400,y=60)

btn2=Button(Window, text="Encrypt", fg='blue')
btn2.bind('<Button-1>', encrypt_event)
btn2.place(x=100,y=350)

btn3=Button(Window, text="Choose file to decrypt", fg='blue')
btn3.bind('<Button-1>', choose_file_dec)
btn3.place(x=400,y=180)

btn4=Button(Window, text="Decrypt", fg='blue')
btn4.bind('<Button-1>', decrypt_event)
btn4.place(x=300,y=350)

Window.title('AES')
Window.geometry("800x800+0+0")
Window.mainloop()




