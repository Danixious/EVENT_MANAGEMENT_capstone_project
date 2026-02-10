import pandas as pd

# df = pd.read_csv("D:/EM_38/data/VenueLook2.csv",encoding="latin-1")

# df = df.rename(columns ={ 
#            'bg_img_link':'Image_link',
#            'mark':'Location',
#            'address':'Description',
#            'category': 'listing_type',
#            'role':'venue_space_type'})
# df.to_csv("D:/EM_38/data/Venue_master.csv",index = False,encoding = 'utf-8')

df2 = pd.read_csv("D:/EM_38/data/Venue_master.csv",encoding = "latin-1")
df2 = df2.rename(columns = {
    'name': 'Name',
    'city':'City',
    'listing_type':'Listing_type',
    'rating':'Rating',
    'price':"Price",
    'venue_space_type':'Venue_space_type',
    'city':'City',
    'int_price':"Initial_price"
})
df2.to_csv("D:/EM_38/data/Venue_master.csv",index = False,encoding = 'utf-8')

