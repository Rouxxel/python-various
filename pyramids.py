import sys


def left_pyramid(line_num):
    if line_num>0:
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)

            #print stars
            for j in range(0,stars):
                print("*",end="")
            
            print("\n")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)       

def pyramid(line_num):
    if (line_num>0):
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)
            #Num of spaces in line
            spaces= int((pyr_base - stars)/2)
        
            #print spaces
            for k in range(0,spaces):
                print(" ",end="")  
            #print stars
            for j in range(0,stars):
                print("*",end="")
            
            print("\n")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def right_pyramid(line_num):
    if (line_num>0):
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)
            #Num of spaces in line
            spaces= (pyr_base - stars)
        
            #print spaces
            for k in range(0,spaces):
                print(" ",end="")  
            #print stars
            for j in range(0,stars):
                print("*",end="")
            
            print("\n")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def left_inverted_pyramid(line_num):
    if line_num > 0:
        #Number of stars in the base line
        pyr_base = 1 + ((line_num * 2) - 2)
        
        for lines in range(line_num, 0, -1):
            #Number of stars in line
            stars = 1 + (2 * (lines)-2)

            #Print stars
            for j in range(stars):
                print("*", end="")
            
            print("\n")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def inverted_pyramid(line_num):
    if line_num > 0:
        #Number of stars in the base line
        pyr_base = 1 + ((line_num * 2) - 2)
        
        for lines in range(line_num, 0, -1):
            #Number of stars in line
            stars = 1 + (2 * (lines)-2)
            #Number of spaces in line
            spaces = int((pyr_base - stars) / 2)
        
            #Print spaces
            for k in range(spaces):
                print(" ", end="")  
            #Print stars
            for j in range(stars):
                print("*", end="")
            
            print("\n")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def right_inverted_pyramid(line_num):
    if line_num > 0:
        #Number of stars in the base line
        pyr_base = 1 + ((line_num * 2) - 2)
        
        for lines in range(line_num, 0, -1):
            #Number of stars in line
            stars = 1 + (2 * (lines)-2)
            #Number of spaces in line
            spaces = int((pyr_base - stars))
        
            #Print spaces
            for k in range(spaces):
                print(" ", end="")  
            #Print stars
            for j in range(stars):
                print("*", end="")
            
            print("\n")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

################################################################
    