from flask import Flask, request, make_response
import pystache
import model
import os
import config

app = Flask(__name__)
app.debug = True


def render(filename, data):
    with open(filename, encoding='utf8') as f:
        return pystache.render(f.read(), data)


@app.route('/company', methods=['GET', 'POST'])
def haha():
    data = None
    if 'cer' in request.args:
        data = model.query(cer=request.args['cer'])
    elif 'nodeid' in request.args:
        data = model.query(node_id=request.args['nodeid'])
    elif 'accessid' in request.args:
        data = model.query(access_id=request.args['accessid'])
    elif 'companyname' in request.args:
        data = model.query(company_name=request.args['companyname'])
    if data:
        return render("company.html", data)
    else:
        return """lack args：cer | nodeid | accessid | companyname
        <br>or no this company
        """


@app.route('/node', methods=['GET', 'POST'])
def node():
    node_id = request.args['node_id']
    f = open(os.path.join(config.html, node_id), encoding='utf8')
    ans = f.read()
    f.close()
    return ans


@app.route('/res', methods=['GET', 'POST'])
def res():
    f = open(os.path.join(config.res, request.args['file']), 'rb')
    resp = make_response(f.read())
    if f.name.endswith('pdf'):
        resp.headers['content-type'] = 'application/pdf'
    elif f.name.endswith('jpg') or f.name.endswith('jpeg'):
        resp.headers['content-type'] = 'image/jpeg'
    elif f.name.endswith('doc') or f.name.endswith('docx'):
        resp.headers['content-type'] = 'application/msword'
    return resp


@app.route('/', methods=['GET'])
def all():
    beg = request.args['beg'] if 'beg' in request.args else 0
    size = request.args['size'] if 'size' in request.args else 10
    if not beg: beg = 0
    if not size: size = 10
    data = model.get_all_company(beg, size)
    return render('all.html', {'data': data})


if __name__ == '__main__':
    app.run()
