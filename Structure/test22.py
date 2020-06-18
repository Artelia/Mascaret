import pickle
class ClassInfoParamFG:
    def __init__(self):
        self.param_fg = {}
        self.link_name_id = {}
        self.list_poly_trav = {}
        self.list_poly_pil = {}
        self.profil = {}
        self.param_g = {}
        self.abac = {}

# # take user input to take the amount of data
# data=ClassInfoParamFG()
#
# # open a file, where you ant to store the data
# file = open('important', 'wb')
#
# # dump information to that file
# pickle.dump(data, file)
#
# # close the file
# file.close()

# open a file, where you stored the pickled data
file = open('../mascaret/cli_fg.obj', 'rb')

# dump information to that file
data = pickle.load(file)

# close the file
file.close()

print(data)
print(data.link_name_id)

