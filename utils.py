def checkLength(strang, length):
    if (len(strang) > length):
        print("Error: Cannot exceed %d characters. Please try again." % (length))
        return True
