# HACKS
# changes every key in dict to lower case: store = {k.lower():v for k,v in store.iteritems()}
# XPATH - gets all h7 tags in between two h5 tags
#    //*[contains(@class,"shopsList")]/h7[count(preceding-sibling::h5)=3]
#   '=3' is basically a position of those tags (meaning basically it is every store)
def stripList(tempList):
    t = tempList
    t=map(lambda s: s.strip(),t)
    t[:]=[it for it in t if it !='']
    return t

def getHours(days, hours):
    storeHours = []
    for i in range(0, len(days)):
        storeHours.append(days[i] + ' ' + hours[i])
    return storeHours

# Replaces only the last occurence
# s = string in which to replace
# old = character to replace
# new = for this new one
def rreplace(s, old, new):
    li = s.rsplit(old, 1) #Split only once
    return new.join(li)

# is string a number?
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
