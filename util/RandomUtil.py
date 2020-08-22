
import random

def pwd():

    all_char = '0123456789qazwsxedcrfvtgbyhnujmikolpQAZWSXEDCRFVTGBYHNUJIKOLP'

    index = len(all_char)-1

    passward = ''

    for _ in range (6):

        n=random.randint(0,index)
        passward += all_char[n]

    return  passward

print(pwd())
