import flask
import numpy
import pypng
import base64
import os

# DATA LOADING (about)
# ...?mat1=(filepath or base64)&mat2=....

##OPERATIONS (about)
# reads right to left, perfoming operations, last return is rendered
# datatype=uint8
# ops=sta (scale, threshold, and)
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
def operate(mat_list, operations, threshold):
    dual_ops = {"a": mat_and, "o": mat_or, "n": mat_not, "x": mat_xor}
    mat = mat_list.pop(0)
    for op in operations:
        op = op.lower()
        if op == "s":
            mat = single_ops[op](mat)
        elif op == "t":
            mat = single_ops[op](mat, threshold)
        elif op in dual_ops.keys():
            mat = dual_ops[op](mat,mat_list.pop(0))
    return mat

# IIP related dunctions

# get pyramidal image file at position for mat
def mat_img(mat, zoom, pos, options):
    return 0

# metadata file generation
def metadata(mat, options):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"\n' +
       'Format="png"\n' +
       'Overlap="0"\n' +
       'TileSize="' + options.get(tilesize, 256) + '" >\n' +
    '<Size Height="' + mat.shape[1] + '"\n' +
          'Width="' +  mat.shape[0] + '"/>\n' +
    '</Image>'
    return xml

# TODO needs to eventually associate data/ops with a uid (i.e. cache sessions)
# we want not to waste uids (and calculation involved)


# ROUTES
app = flask.Flask(__name__)


@app.route("/")
def about_bin2iip():
    return "bin2iip! Documentation coming soon!"


# generate the dzi url
@app.route("/dzi")
def link_get():
    dt = request.args.get("datatype")
    mats = []
    # support up to 9 matrix objects (single character in ops)
    for i in range(1, 9):
        k = "mat"+str(i)
        if k in request.args:
            mats.push(mat_in(request.args.get(k), dt))
            continue
        else:
            break
    request.args.get("ops")
    request.args.get("threshold")
    return "bin2iip! Documentation coming soon!"

# the svs url for metadata
@app.route("/img/<uid>/")
def metadata_get(uid):
    return "bin2iip! Documentation coming soon!"

@app.route("/img/<uid>/<level>/<fn>")
def image_get(uid, level, fn):
    # support up to 9 matrix objects (single character in ops)
    for i in range(1, 9):
        k = "mat"+str(i)
        if k in request.args:
            mats.push(request.args[k])
            continue
        else:
            break
    request.args.get("ops")
    request.args.get("threshold")
    return "bin2iip! Documentation coming soon!"
