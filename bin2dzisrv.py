import flask
import numpy
import scipy
import png
import base64
import os
import PIL

#TODO may want to replace with better cache method
CACHE = {}

# DATA LOADING (about)
# ...?mat1=(filepath or base64)&mat2=....

##OPERATIONS (about)
# first matrix is put on stack
# left to right, scale and threshold operate on stack only
# other operations apply the result of old stack and next matrix to stack
# datatype=uint8
# ops=sta (short for: scale, threshold, and)
# threshold=0.6
# scales mat1 to [0,1], result elementiwse if gte 0.6, logical and with mat2
# transparency on [0,1] expected

# Helper Functions


def mat_in(data, dt):
    """Get a matrix from a base64 string or a file path.

    Args:
        data (str): a base64 string prepended with 'b64' or a file path
        dt (str): a string representation of the datatype to be used

    Returns:
        mat: a numpy matrix of the data, or -1 for error
    """
    # datatype resolve
    supported = ["bool", "int8", "int16", "int32", "int64", "uint8",
                 "uint16", "uint32", "uint64", "float16", "float32", "float64"]
    ops = [numpy.bool_, numpy.int8, numpy.int16, numpy.int32, numpy.int64, numpy.uint8,
           numpy.uint16, numpy.uint32, numpy.uint64, numpy.float16, numpy.float32, numpy.float64]
    dt_pos = supported.index(dt.lower())
    if dt_pos >= 0:
        dt = ops[dt_pos]
    else:
        return -1
    # is it a base64 encoded string?
    if data[:3].lower() == "b64":
        return numpy.frombuffer(data[3:], dtype=dt)
    else:
        # it's a file; does it exist?
        # PLEASE be careful with the permissions of THIS server
        if os.path.isfile(data):
            return numpy.fromFile(data, dtype=dt)
        else:
            return -1
# numpy functions repackaged or not; mostly as reminders on what to do

# matrix threshold


def mat_threshold(mat, threshold):
    return numpy.greater(mat, threshold)
# matrix scale value elementwise


def mat_scale(mat):
    return numpy.multiply(numpy.subtract(mat, mat.min().min()), (mat.max().max()-mat.min().min()))
#matrix and elementwise


def mat_and(mat1, mat2):
    return numpy.logical_and(mat1, mat2)
#matrix or elementwise


def mat_or(mat1, mat2):
    return numpy.logical_or(mat1, mat2)
# matrix not elementwise


def mat_not(mat1, mat2):
    return numpy.logical_not(mat1, mat2)
# matrix xor elementwise


def mat_xor(mat1, mat2):
    return numpy.logical_xor(mat1, mat2)

# work through the instructions
def operate(mat_stack, operations, threshold):
    """Execute a stack of operations, in single-char string form, on a matrix stack

    Args:
        mat_stack (list of numpy.matrix): the matrix stack
        operations (str): the operation stack
        threshold (float): the threshold for the threshold operation
    Returns:
        mat: a numpy matrix of the result
    """
    dual_ops = {"a": mat_and, "o": mat_or, "n": mat_not, "x": mat_xor}
    mat = mat_stack.pop(0)
    for op in operations:
        op = op.lower()
        if op == "s":
            mat = single_ops[op](mat)
        elif op == "t":
            mat = single_ops[op](mat, threshold)
        elif op in dual_ops.keys():
            mat = dual_ops[op](mat,mat_stack.pop(0))
    return mat

# IIP related dunctions

# get pyramidal image file at position for mat
def mat_img(mat, zoom, pos, options):
    p_img = 2.0^zoom# how many pixels is the whole mat at this level?
    ppe = p_img/mat.shape[0] # how many pixels per elem at this level?
    if ppe > 16.0:
        # TODO pixels too big, don't render
        pass
    pos = pos.split("_")
    ts = options.get(tilesize, 256)
    ept = ts/ppe
    bounds = [pos[0]*ept, pos[0]*(ept+1), pos[1]*ept, pos[1]*(ept+1)] # xmin xmax ymin ymax
    # is it binary?
    submat = mat(slice(bounds[0],bounds[1]), slice(bounds[2],bounds[3]))
    rgba = np.zeros((ts, ts, 3), dtype=np.uint8)
    rgba[..., 0] = int(options.color[0:2], 16)
    rgba[..., 1] = int(options.color[2:4], 16)
    rgba[..., 2] = int(options.color[4:6], 16)
    rgba[..., 3] = scipy.misc.imresize(submat, (ts, ts))
    return PIL.Image.fromarray(rgba, "RGBA")

# metadata file generation
def metadata(mat, options):
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"\n'
       'Format="png"\n' +
       'Overlap="0"\n' +
       'TileSize="' + options.get(tilesize, 256) + '" >\n'
    '<Size Height="' + mat.shape[1] + '"\n'
          'Width="' +  mat.shape[0] + '"/>\n'
    '</Image>')
    return xml

def set_cache(args):
    dt = args.get("datatype")
    mats = []
    # support up to 9 matrix objects (single character in ops)
    for i in range(1, 9):
        k = "mat"+str(i)
        if k in request.args:
            mats.push(mat_in(args.get(k), dt))
            continue
        else:
            break
    options = {}
    options.color = request.args.get("color", "4280f4") # hex without "#"
    uid = str(hash(str(args)))[1:]
    # hash of params in deterministic order
    if not uid in cache:
        CACHE[uid] = {"mat": operate(mats, args.get("ops"), args.get("threshold")), "options": options}
    return uid

def send_img(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'PNG', quality=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

# ROUTES
app = flask.Flask(__name__)


@app.route("/")
def about_bin2iip():
    return "bin2iip! Documentation coming soon!"


# generate the dzi url
@app.route("/dzi")
def link_get():
    set_cache(request.args)
    return "/img/"+uid

# the svs url for metadata
@app.route("/img/<uid>/")
def metadata_get(uid):
    # it should be in cache
    if uid in CACHE:
        return metadata(CACHE[uid].mat, CACHE[uid].options)
    else:
        return 404

@app.route("/img/<uid>/<level>/<fn>")
def image_get(uid, level, fn):
    if uid in CACHE:
        return send_img(mat_img(CACHE[uid].mat, level, fn, CACHE[uid].options))
    else:
        return 404
