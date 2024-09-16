import sys

def full_left_pyramid(line_num):
    if line_num>0:
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)

            #print stars
            for j in range(0,stars):
                print("*",end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)       

def full_pyramid(line_num):
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
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def full_right_pyramid(line_num):
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
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def full_left_inverted_pyramid(line_num):
    if line_num > 0:
        
        for lines in range(line_num, 0, -1):
            #Number of stars in line
            stars = 1 + (2 * (lines)-2)

            #Print stars
            for j in range(stars):
                print("*", end="")
            
            print("")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def full_inverted_pyramid(line_num):
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
            
            print("")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def full_right_inverted_pyramid(line_num):
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
            
            print("")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

################################################################

def left_pyramid(line_num):
    if line_num>0:
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)
            
            #print stars
            if lines == line_num - 1:
                for j in range(0,stars):
                    print("*", end="")
            else:
                for j in range(0,stars):
                    if j == 0 or j == stars - 1:
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1) 

def pyramid (line_num):
    if (line_num > 0):
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)
            #Num of spaces in line
            spaces= int((pyr_base - stars)/2)
        
            #print spaces
            for j in range(0,spaces):
                print(" ",end="")  
            #print stars
            if lines == line_num - 1:
                for j in range(stars):
                    print("*", end="")
            else:
                for j in range(stars):
                    if j == 0 or j == stars - 1:
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def right_pyramid (line_num):
    if (line_num > 0):
        #Number of stars in the line
        pyr_base= 1 + ((line_num*2)-2)
    
        for lines in range(0,line_num):
        
            #Num of stars in line
            stars= 1 + (2*lines)
            #Num of spaces in line
            spaces= int((pyr_base - stars))
        
            #print spaces
            for j in range(0,spaces):
                print(" ",end="")  
            #print stars
            if lines == line_num - 1:
                for j in range(stars):
                    print("*", end="")
            else:
                for j in range(stars):
                    if j == 0 or j == stars - 1:
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def left_inverted_pyramid(line_num):
    if line_num > 0:
        
        for lines in range(line_num, 0, -1):
            #Number of stars in line
            stars = 1 + (2 * (lines)-2)

            if (lines==line_num):
                #Print stars in a full line
                for j in range(0,stars):
                    print("*", end="")
            else:
                #print the rest
                for j in range(stars):
                    if(j==0) or (j==stars-1):
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")  #Move to the next line after printing stars

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
            if (lines == line_num):
                for j in range(stars):
                    print("*", end="")
            else:
                for j in range(stars):
                    if(j==0) or (j==stars-1):
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")  #Move to the next line after printing stars

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
            if(lines==line_num):
                for j in range(stars):
                    print("*", end="")
            else:
                for j in range(stars):
                    if(j==0) or (j==stars-1):
                        print("*", end="")
                    else:
                        print(" ", end="")
            
            print("")  #Move to the next line after printing stars

    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

################################################################
################################################################

def full_square(sides):
    if sides > 0:
        for v_side in range(0,sides):
            
            for h_side in range(0,sides):
                print("*",end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)

def full_rectangle(width, height):
    if (width > 0) and (height > 0):
        for heights in range(0,height):
            for widths in range(0,width):
                print("*", end="")

            
            print("")
    else:
        print("Invalid input. Please enter positive integers for width and height.")
        sys.exit(1)
    

################################################################

def square(sides):
    if sides > 0:
        for v_side in range(0,sides):
            
            #Always print a star and the left side
            print("*", end="")
            
            if (v_side == 0 or v_side == sides - 1):
                for h_side in range(0,sides-1):
                    print("*",end="")
            else:
                for h_side in range(0,sides-2):
                    print(" ",end="")
                print("*", end="")
            
            print("")
    else:
        print("Invalid input. Please enter a positive integer greater than 0.")
        sys.exit(1)
        
def rectangle(width, height):
    if (width > 0) and (height > 0):
        for heights in range(0,height):
            #Always print a star and the left side
            print("*", end="")
            
            if (heights == 0 or heights == height - 1):
                for widths in range(0,width-1):
                    print("*", end="")
            else:
                for widths in range(0,width-2):
                    print(" ", end="")
                print("*", end="")
            
            print("")
    else:
        print("Invalid input. Please enter positive integers for width and height.")
        sys.exit(1)

full_rectangle(20,4)