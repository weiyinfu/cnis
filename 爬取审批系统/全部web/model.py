import pymysql

database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'haha',
    'db': 'company',
    'charset': 'utf8'
}


def query(cer=None, node_id=None, access_id=None, company_name=None):
    conn = pymysql.connect(**database)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    page_data = dict()
    if cer:
        cer = conn.escape_string(cer)
        rows = cur.execute("select * from apply where certificate_number='%s'" % cer)
        if rows:
            apply = cur.fetchone()
            page_data['apply'] = apply
        else:
            return None
        rows = cur.execute("select * from company where id='%s'" % apply['company'])
        if rows:
            company = cur.fetchone()
            page_data['company'] = company
    else:
        if node_id:
            node_id = conn.escape_string(node_id)
            rows = cur.execute("select * from company where node_id='%s'" % node_id)
            if rows:
                company = cur.fetchone()
                page_data['company'] = company
            else:
                return None
        elif access_id:
            access_id = conn.escape_string(access_id)
            rows = cur.execute("select * from company where access_id='%s'" % access_id)
            if rows:
                company = cur.fetchone()
                page_data['company'] = company
            else:
                return None
        if company_name:
            company_name = conn.escape_string(company_name)
            rows = cur.execute("select*from company where name='%s'" % company_name)
            if rows:
                company = cur.fetchone()
                page_data['company'] = company
            else:
                return None
        rows = cur.execute("select * from apply where company='%s'" % company['id'])
        if rows:
            apply = cur.fetchone()
            page_data['apply'] = apply

    rows = cur.execute("select * from process where apply_id='%s'" % apply['id'])
    if rows:
        page_data['process'] = cur.fetchone()
    rows = cur.execute("select * from apply_material where apply_id='%s'" % apply['id'])
    if rows:
        page_data['apply_material'] = cur.fetchall()
    rows = cur.execute("select * from apply_detail where apply_id='%s'" % apply['id'])
    if rows:
        page_data['apply_detail'] = cur.fetchall()
    rows = cur.execute("select * from qualification_report where apply_id='%s'" % apply['id'])
    if rows:
        page_data['qualification_report'] = cur.fetchall()
    return page_data


def get_all_company(beg, sz):
    conn = pymysql.connect(**database)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    rows = cur.execute("select certificate_number,id from apply limit %s,%s" % (beg, sz))
    return cur.fetchall()


if __name__ == '__main__':
    print(query('XK11-001-00261'))
