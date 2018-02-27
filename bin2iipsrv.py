import flask

##DATA LOADING (about)
# ...?mat1=(filepath or data)&mat2=....

##OPERATIONS (about)
# reads right to left, perfoming operations, last return is rendered
# ops=1SCALTHRESHOLDEAND2
# threshold=0.6
# scale=2
# scales mat1 by 2x, result elementiwse if gte 0.6, logical and with mat2

## HELPER FUNCTIONS
#input to matrix
def mat_in(data):
    return 0
#matrix threshold
def mat_threshold(mat, threshold):
    return 0
#matrix scale value elementwise
def mat_scale(mat, scale):
    return 0
#matrix and elementwise
def mat_and(mat1, mat2):
    return 0
#matrix or elementwise
def mat_or(mat1, mat2):
    return 0
#matrix not elementwise
def mat_not(mat1, mat2):
    return 0
#matrix xor elementwise
def mat_xor(mat1, mat2):
    return 0
#get pyramidal image file at position for mat
def mat_img(mat, zoom, pos, options):
    return 0
#metadata file generation
def metadata(mat, options):
    return 0

# needs to associate data/ops with a uid
# we want not to waste uids

# ROUTES
