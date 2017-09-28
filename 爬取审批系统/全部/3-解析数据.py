import os
import re
import uuid

import pymysql
import requests
from pyquery import PyQuery as pq

import config

cur_company = None


def download_binary(url):
    # 下载二进制文件
    print(download_binary.__name__, url)
    conn, cur = db_get(download_binary.__name__)
    rows = cur.execute("select * from files where url='%s'" % url)
    if rows > 0:
        print("already had")
        return cur.fetchone()['path']
    file = url[len('http://xkzsp.cnis.gov.cn/system/files/'):] if url.startswith(
        'http://xkzsp.cnis.gov.cn/system/files/')else 'sites-' + url[len(
        'http://xkzsp.cnis.gov.cn/sites/default/files/sm/'):]
    file = file.replace('/', '-').lower()
    file = requests.utils.unquote(file)
    file = file.replace('\'', '').replace('"', '')
    print(file)
    if len(file) > 100: file = uuid.uuid1()
    file_name, file_type = os.path.splitext(file)
    rows = cur.execute("select * from files where path='%s'" % file)
    if rows:
        file_id = 0
        while rows > 0:
            file = "%s_%s%s" % (file_name, str(file_id), file_type)
            rows = cur.execute("select * from files where path='%s'" % file)
            if rows == 0: break
            file_id += 1
    cur.execute(
        "insert into files set url='%s' ,path='%s',company='%s'" % (
            conn.escape_string(url),
            conn.escape_string(file),
            cur_company['id']))
    conn.commit()
    return file


def parse_company(whole):
    company_map = {
        # 基本信息27项
        '.field-name-field-address': 'address',  # 地址
        '.field-name-field-production-address': 'produce_address',  # 生产地址
        '.field-name-field-province': 'province',  # 所在省
        # '.field-name-field-district': 'district',  # 所在省市，改成了省市区三项
        '.field-name-field-geo-p': 'company_province',  # 省
        '.field-name-field-geo-c': 'company_city',  # 市
        '.field-name-field-geo-d': 'company_street',  # 区
        '.field-name-field-organization-code': 'organization_code',  # 机构编码
        '.field-name-field-organization-postcode': 'postcode',  # 邮编
        '.field-name-field-fax': 'fax',  # 传真
        '.field-name-field-email': 'email',  # 邮箱
        '.field-name-field-lr-name': 'legal_person',  # 法人
        '.field-name-field-lr-id': 'lp_id',  # 法人身份证号
        '.field-name-field-lr-mobile': 'lp_mobile',  # 法人手机
        '.field-name-field-lr-phone': 'lp_phone',  # 法人电话
        # '.field-name-field-lr-idsm': 'lp_idcard_img',  # 身份证
        '.field-name-field-qm-name': 'quality_manager',  # 质量负责人
        '.field-name-field-qm-id': 'qm_id',  # 质量负责人身份证号
        '.field-name-field-qm-phone': 'qm_phone',  # 质量负责人电话号
        '.field-name-field-qm-mobile': 'qm_mobile',  # 质量负责人手机号
        '.field-name-field-contact-people': 'contact',  # 联系人
        '.field-name-field-ct-id': 'contact_id',  # 联系人id
        '.field-name-field-contact-phone': 'contact_phone',  # 联系人电话
        '.field-name-field-mobile': 'contact_mobile',  # 联系人手机
        '.field-name-field-biz-regno': 'licence_number',  # 营业执照编号
        # '.field-name-field-yyzzsm': 'licence_image',  # 营业执照图片
        '.field-name-field-gsdjjg': 'register_org',  # 注册机构
        '.field-name-field-gsclrq': 'establish_date',  # 创建日期
        '.field-name-field-gsjyqx': 'run_date',  # 经营期限
        '.field-name-field-gszczj': 'register_capital',  # 注册资本
        '.field-name-field-gdzc': 'fixed_capital',  # 固定资本
        '.field-name-field-nzcz': 'annual_money',  # 年收入
        '.field-name-field-nxse': 'annual_sales',  # 年销售量
        '.field-name-field-nlsje': 'annual_tax',  # 年纳税额
        '.field-name-field-nlr': 'annual_profit',  # 年利润,
        '.field-name-field-gross-output': 'annual_gross_output',  # 年总产值
        '.field-name-field-profit-tax': 'annual_profit_tax',  # 年利税金额
        '.field-name-field-employee-number': 'total_staff',  # 从业人员数
        '.field-name-field-jsrys': 'technology_staff',  # 技术人员人数
        '.field-name-field-jyrys': 'test_staff',  # 测试人员人数
        '.field-name-field-scrys': 'produce_staff',  # 生产人员人数
        '.field-name-field-enterprise-scale': 'company_scale',  # 企业规模
        '.field-name-field-lr-title': 'lp_job',  # 法人职位
        '.field-name-field-phone': 'company_phone',  # 企业电话
    }
    ans = translate(company_map, whole)
    ans['name'] = whole('.pane-title').eq(0).text()
    if whole('.field-name-field-lr-idsm'):
        href = whole('.field-name-field-lr-idsm a').attr('href')
        ans['lp_idcard_img'] = download_binary(href)
    if whole('.field-name-field-yyzzsm'):
        href = whole('.field-name-field-yyzzsm a').attr('href')
        ans['licence_image'] = download_binary(href)
    if whole('.field-name-field-district'):
        s = whole('.field-name-field-district .shs-hierarchy').text()
        s = s.split()
        if len(s) >= 1: ans['sheng'] = s[0]
        if len(s) >= 2: ans['shi'] = s[1]
        if len(s) >= 3: ans['xian'] = s[2]
    for i in ['total_staff', 'test_staff',
              'technology_staff', 'produce_staff']:
        if i in ans:
            ans[i] = to_int(ans[i])
    return ans


def parse_apply(whole):
    apply_map = {
        # 申请信息12项
        # '.field-name-field-qycn': 'promise',  # 企业承诺
        # '.field-name-field-product-detail': 'product_detail',  # 明细
        # '.field-name-field-product-detail-n': 'add_unit_detail',  # 增项明细
        # '.field-name-field-product-unit-ref': 'product_unit',  # 产品单元
        '.field-name-field-unit-number': 'product_unit_count',  # 产品单元个数
        '.field-name-field-product-ref': 'product_name',  # 产品名称
        '.field-name-field-certificate-number': 'certificate_number',  # 证书编号
        '.field-name-field-certificate-expiration-dat': 'certificate_expired_date',  # 证书有效期
        '.field-name-field-explanation': 'explanation',  # 说明
        '.field-name-field-license-type': 'certificate_type',  # 发证类别
        # '.field-name-field-app-type': 'apply_type',  # 申请类别
        '.field-name-field-test-agency': 'test_agency',  # 检验机构
        # '.field-name-field-policy-material': 'policy_material',  # 实施细则规定应提交的其他材料
        '.field-name-field-province-policy': 'province_policy',  # 其它
        # '.field-name-field-mcpjybg': 'qualification_report',  # 监督抽查合格报告
        '.field-name-field-notes': 'notes',  # 备注,
        '.field-name-field-oxkzno': 'old_certificate_number',  # 原许可证编码
        '.field-name-field-oxkzfzrq': 'old_certificate_date',  # 原许可证发证日期,
        '.field-name-field-oxkzexp': 'old_certificate_expire_date',  # 原许可证有效日期
        # '.field-name-field-oxkzsm': 'old_certificate_image',  # 原许可证照片
        '.field-name-field-xkfwbg': 'certificate_change_reason',  # 许可范围变更事项
        '.field-name-field-cyzccn': 'industry_policy_promise',  # 产业政策承诺
        '.field-name-field-multimedia': 'media',  # 多媒体,
        # 补领
        '.field-name-field-blyy': 'replace_reason',  # 补领原因，
        '.field-name-field-blysrq': 'miss_date',  # 遗失或损毁时间
        '.field-name-field-blzslx': 'replace_type',  # 补领整数类型
        '.field-name-field-blkdbzmc': 'newspaper',  # 刊登报纸名称,
        '.field-name-field-blkdbzrq': 'newspaper_date',  # 声明刊登日期
        '.field-name-field-blyssm': 'miss_announcement',  # 遗失声明文件
        '.field-name-field-other-notes': 'other_notes',  # 其他情况说明（含符合产业政策情况说明）（company_id:255647）
        # 文档下载
        '.field-name-field-registration-file': 'apply_document',  # 企业申请书
        '.field-name-field-all-files': 'other_material',  # 其它材料
        # 变更
        '.field-name-field-oqymc': 'old_company_name',  # 变更前企业名称
        '.field-name-field-nqymc': 'new_company_name',  # 变更前企业名称
        '.field-name-field-oyyzzbh': 'old_license_number',  # 变更前营业执照编号
        '.field-name-field-nyyzzbh': 'new_license_number',  # 变更前营业执照编号
        '.field-name-field-oyyzzfzrq': 'old_license_create_date',  # 变更前营业执照发证日期
        '.field-name-field-nyyzzfzrq': 'new_license_create_date',  # 变更后营业执照发证日期
        '.field-name-field-ozs': 'old_address',  # 变更前住所名称
        '.field-name-field-nzs': 'new_address',  # 变更后住所名称
        '.field-name-field-oscdz': 'old_produce_address',  # 变更前生产地址
        '.field-name-field-nscdz': 'new_produce_address',  # 变更后生产地址
        '.field-name-field-yxqt': 'continue_explanation',  # 其他说明（延续）
        # 不予许可原因
        '.field-name-field-disapprove-reason': 'dismiss_reason'  # 不予许可原因
    }
    ans = translate(apply_map, whole)
    if whole('.field-name-field-product-ref'):
        product_node_id = whole('.field-name-field-product-ref').find('a').attr('href')
        ans['product_node_id'] = re.search('\d+', product_node_id).group()
    if whole('.field-name-field-product-detail'):
        s = whole('.field-name-field-product-detail').find('.field-item').eq(0).html()
        if s:
            ans['product_detail'] = handle_p(s)
    if whole('.field-name-field-product-detail-n'):
        s = whole('.field-name-field-product-detail-n').find('.field-item').eq(0).html()
        if s:
            ans['add_unit_detail'] = handle_p(s)
    if whole('.field-name-field-product-unit-ref'):
        items = whole('.field-name-field-product-unit-ref .field-item')
        s = []
        for i in range(items.length):
            s.append(items.eq(i).text())
        ans['product_unit'] = ';'.join(s)
    if whole('.field-name-field-app-type'):
        items = whole('.field-name-field-app-type .field-item')
        s = []
        for i in range(items.length):
            s.append(items.eq(i).text())
        ans['apply_type'] = ';'.join(s)
    if whole('.field-name-field-mcbg'):
        items = whole('.field-name-field-mcbg .field-item')
        s = []
        for i in range(items.length):
            s.append(items.eq(i).text())
        ans['name_change_type'] = ';'.join(s)

    if whole('.field-name-field-yxspecial'):
        items = whole('.field-name-field-yxspecial .field-item')
        s = []
        for i in range(items.length):
            s.append(items.eq(i).text())
        ans['continue_deduction'] = ';'.join(s)
    if whole('.field-name-field-msdhccn'):
        ans['deduction_promise'] = handle_files(whole('.field-name-field-msdhccn'))
    if whole('.field-name-field-oxkzsm'):
        items = whole('.field-name-field-oxkzsm a')
        s = []
        for it in range(items.length):
            href = items.eq(it).attr('href')
            fname = download_binary(href)
            s.append(fname)
        ans['old_certificate_image'] = ';'.join(s)
    if whole('.field-name-field-scy-ref'):  # 审查人员
        items = whole('.field-name-field-scy-ref a')
        s = []
        for it in range(items.length):
            href = items.eq(it).attr('href')
            href = re.search('\d+', href).group()
            name = items.eq(it).text()
            person = '%s$%s' % (name, href)
            s.append(person)
        ans['inspect_workers'] = ';'.join(s)
    if whole('.field-name-field-oyyzzsm'):
        href = whole('.field-name-field-oyyzzsm a').attr('href')
        ans['old_license_image'] = download_binary(href)
    if whole('.field-name-field-gsgmzmsm'):
        href = whole('.field-name-field-gsgmzmsm a').attr('href')
        ans['gsj_prove'] = download_binary(href)
    if whole('.field-name-field-zsgmzmsm'):
        href = whole('.field-name-field-zsgmzmsm a').attr('href')
        ans['mzj_prove'] = download_binary(href)
    if whole('.field-name-field-qycn'):
        href = whole('.field-name-field-qycn a').attr('href')
        ans['promise'] = download_binary(href)
    for i in ['product_unit_count']:
        if i in ans:
            ans[i] = to_int(ans[i])
    return ans


def parse_apply_material(whole):
    items = whole('.field-name-field-policy-material').children('.field-items').children('.field-item')
    ans = []
    print(parse_apply_material.__name__, len(items))
    for i in range(len(items)):
        it = dict()
        file = handle_files(items.eq(i).find('.field-name-field-policy-file').find('.field-items'))
        filename = items.eq(i).find('.field-name-field-policy-filename').find('.field-items').text()
        it['name'] = filename
        it['path'] = file
        ans.append(it)
    return ans


def parse_qualification_report(whole):  # 监督抽查合格报告
    qualification_report_map = {
        '.field-name-field-jdcc-poduct': 'product_name',
        '.field-name-field-product-unit-r': 'product_unit',
        '.field-name-field-jdcc-ir': 'report'
    }
    items = whole('.field-name-field-mcpjybg').children('.field-items').children('.field-item')
    ans = []
    print(parse_qualification_report.__name__, len(items))
    for i in range(items.length):
        it = translate(qualification_report_map, items.eq(i))
        ans.append(it)
    return ans


def parse_apply_detail(whole):
    apply_detail_map = {
        '.field-name-field-product-unit-r': 'product_unit',  # 产品单元
        '.field-name-field-product-unit-detail': 'product_unit_detail',  # 品种规格型号
        '.field-name-field-app-type-r': 'apply_type',  # 申请类型
        '.field-name-field-inspection-result': 'inspect_result',  # 实地核查报告
        '.field-name-field-inspection-record': 'inspect_record',  # 实地核查记录
        '.field-name-field-defect-summary': 'inspect_advice',  # 实地核查不符合项及建议改进条款汇总表
        '.field-name-field-inspection-report': 'inspect_report',  # 检验报告
        '.field-name-field-jyjg-ref': 'test_org',  # 检验机构
        '.field-name-field-workers-info': 'worker_info',  # 人员信息表
        '.field-name-field-equipment-info': 'device_info'  # 设备信息表
    }
    items = whole('.field-name-field-pdl').children('.field-items').children('.field-item')
    ans = []
    print(parse_apply_material.__name__, len(items))
    for i in range(items.length):
        it = translate(apply_detail_map, items.eq(i))
        ans.append(it)
    return ans


def parse_process(whole):
    process_map = {
        # 进度信息17项
        '.field-name-field-certificate-creation-date': 'certificate_create_date',  # 许可证创建日期
        '.field-name-field-examiner': 'certificate_examiner',  # 审查人
        '.field-name-field-apply-date': 'certificate_apply_date',  # 申请日期
        '.field-name-field-accept-date': 'certificate_accept_date',  # 受理日期
        '.field-name-field-scbreceive-date': 'receive_material_date',  # 审查部接收材料日期
        '.field-name-field-inspect-date': 'inspect_date',  # 核查日期
        '.field-name-field-recvsample-date': 'receive_sample_date',  # 接收样品日期
        '.field-name-field-test-date': 'test_date',  # 检验日期
        '.field-name-field-pass-date': 'manager_check_date',  # 中心主任审核日期
        '.field-name-field-czapprove-date': 'director_check_date',  # 主管审核日期
        '.field-name-field-zgfszapprove-date': 'deputy_check_date',  # 主管副司长审核日期
        '.field-name-field-applicant': 'applicant',  # 申请人
        '.field-name-field-accept-user': 'handler',  # 受理人
        '.field-name-field-sjsend-date': 'send_province_date',  # 省局寄送日期
        '.field-name-field-pseudo-sjsendinfo': 'send_province_info',  # 省局寄送信息
        '.field-name-field-pseudo-accept': 'province_receive_info',  # 省局受理信息
        # '.field-name-field-license-log':'operation_log',#操作日志,
        '.field-name-field-scbsend-date': 'send_review_date',  # 审查部寄送日期
        '.field-name-field-pseudo-scbsendinfo': 'send_review_info',  # 审查部寄送信息
        '.field-name-field-pseudo-checkin': 'review_receive_info',  # 审查中心登记
        '.field-name-field-pseudo-pass': 'review_pass_info',  # 材料审查通过
        '.field-name-field-pseudo-permit': 'final_office_pass',  # 总局审批通过
        '.field-name-field-pseudo-print': 'certificate_print_info',  # 证书打印日期
        '.field-name-field-pseudo-export': 'certificate_public_info',  # 数据公示日期
    }
    ans = translate(process_map, whole)
    ans['state'] = whole('.field-name-field-state').find('ul').text()
    if whole('.field-name-field-material-ref'):
        ans['register_material'] = whole('.field-name-field-material-ref').find('a').text()
        href = whole('.field-name-field-material-ref').find('a').attr('href')
        ans['register_material_id'] = re.search('\d+', href).group()
    if whole('.field-name-field-check-ref'):
        ans['small_sign'] = whole('.field-name-field-check-ref').find('a').text()
        href = whole('.field-name-field-check-ref').find('a').attr('href')
        ans['small_sign_id'] = re.search('\d+', href).group()
    if whole('.field-name-field-report-ref'):
        ans['big_sign'] = whole('.field-name-field-report-ref').find('a').text()
        href = whole('.field-name-field-report-ref').find('a').attr('href')
        ans['big_sign_id'] = re.search('\d+', href).group()
    if whole('.field-name-field-license-log'):
        s = []
        items = whole('.field-name-field-license-log').find('.field-item')
        for i in range(items.length):
            s.append(items.eq(i).text())
        ans['operation_log'] = ';'.join(s)
    return ans


def handle_p(s):
    s = re.sub('<br/?>', '\n', s)
    s = re.sub('<.*?>', '', s)
    s = re.sub('(\n)+', '\n', s)
    return s


def handle_files(field_items):
    # 处理文件
    files = field_items('.file')
    file_name = []
    for i in range(files.length):
        url = files.eq(i).find('a').attr('href')
        fname = download_binary(url)
        file_name.append(fname)
    return ';'.join(file_name)


def translate(translate_map, whole):
    # 根据translate_map抽取信息，返回一个实体
    ans = dict()
    for tag, attr in translate_map.items():
        if not whole(tag): continue
        items = whole.find(tag).children('.field-items')
        it = items.children('.field-item')
        if not it:
            continue
        if it.find('.file'):
            ans[attr] = handle_files(items)
            continue
        if len(it) == 0:
            continue
        else:
            ans[attr] = it.text()
        if len(it) > 1:
            print('item 个数很多\n')
    return ans


def to_int(x):
    x = re.sub('\s', '', x)
    return x


db_map = dict()


def db_get(name):
    if name not in db_map:
        conn = pymysql.connect(**config.database)
        cur = conn.cursor(pymysql.cursors.DictCursor)
        db_map[name] = (conn, cur)
    return db_map[name]


def db_close():
    for i in db_map:
        db_map[i][1].close()
        db_map[i][0].close()


def db_had(company_id):
    conn, cur = db_get(db_had.__name__)
    rows = cur.execute("select * from company where id='%s'" % company_id)
    return rows != 0


def grab(company_id, company_node_id):
    # 根据公司的id抓取公司数据
    f = open(os.path.join(config.html, company_node_id), encoding='utf8')
    html = f.read()
    f.close()
    whole = pq(html)
    company = parse_company(whole)
    company['id'] = company_id
    company['node_id'] = company_node_id
    apply = parse_apply(whole)
    apply_detail = parse_apply_detail(whole)
    apply_material = parse_apply_material(whole)
    process = parse_process(whole)
    qualification_report = parse_qualification_report(whole)
    apply['id'] = uuid.uuid1()
    apply['company'] = company['id']
    process['id'] = uuid.uuid1()
    process['apply_id'] = apply['id']
    for i in apply_detail:
        i['id'] = uuid.uuid1()
        i['apply_id'] = apply['id']
    for i in apply_material:
        i['id'] = uuid.uuid1()
        i['apply_id'] = apply['id']
    for i in qualification_report:
        i['id'] = uuid.uuid1()
        i['apply_id'] = apply['id']
    # pprint(('company', company))
    # pprint(('apply', apply))
    # pprint(('apply_detail', apply_detail))
    # pprint(('process', process))
    # pprint(('apply_material', apply_material))
    # pprint(('qualification_report', qualification_report))
    # return
    conn, cur = db_get(grab.__name__)
    config.insert('company', company, cur, conn)
    config.insert('apply', apply, cur, conn)
    config.insert('process', process, cur, conn)
    for i in apply_detail:
        config.insert('apply_detail', i, cur, conn)
    for i in apply_material:
        config.insert('apply_material', i, cur, conn)
    for i in qualification_report:
        config.insert('qualification_report', i, cur, conn)
    conn.commit()


def scrawl():
    global cur_company
    conn, cur = db_get(scrawl.__name__)
    rows = cur.execute('select * from company_ids')
    for i in range(rows):
        co = cur.fetchone()
        cur_company = co
        print(i, co)
        if db_had(co['id']):
            print('already had')
            continue
        grab(co['id'], co['node_id'])


scrawl()
db_close()
