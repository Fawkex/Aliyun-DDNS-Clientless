# -*- coding: utf-8 -*-
#
# Aliyun DDNS Clientless
# Author: Fawkex
# Date: 2022-07-28
# https://github.com/Fawkex/Aliyun-DDNS-Clientless
#

import os
import json
from urllib.parse import unquote

from Tea.core import TeaCore
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util.client import Client as UtilClient

def get_client(credentials):
    config = open_api_models.Config(
        type='sts',
        access_key_id=credentials.access_key_id,
        access_key_secret=credentials.access_key_secret,
        security_token=credentials.security_token
    )
    return Alidns20150109Client(config)

def handler(environ, start_response):
    # 解码请求
    query_string = unquote(environ['QUERY_STRING'])
    try:
        queries_splited = query_string.split('&')
        queries = {}
        for query in queries_splited:
            try:
                key, value = query.split('=')
                queries[key.lower()] = value.lower()
            except:
                pass
    except:
        pass
    # 检查请求
    ## 密码 secret
    try:
        if queries['secret'] != os.environ['secret'].lower():
            raise Exception()
    except:
        status = '403 Forbidden'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Wrong SECRET.'.encode()]
    ## 记录类型 type
    ## 不填默认为A
    ## 使用IPv6时需要填入value
    if 'type' not in queries.keys():
        queries['type'] = 'A'
    if queries['type'] == 'AAAA' and 'value' not in queries.keys():
        status = '400 Bad Request'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['For Record type AAAA, a VALUE is needed.'.encode()]
    ## 前缀 Prefix
    if 'prefix' not in queries.keys():
        status = '400 Bad Request'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Record PREFIX is needed.'.encode()]
    try:
        queries['type'] = queries['type'].upper()
        if queries['type'] not in ['A', 'AAAA']:
            raise TypeError()
    except NameError:
        status = '400 Bad Request'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Record TYPE is needed.'.encode()]
    except TypeError:
        status = '400 Bad Request'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Record TYPE can only be A or AAAA.'.encode()]
    ## 记录值 value
    if 'value' not in queries.keys():
        value = environ.get('REMOTE_ADDR')
    else:
        value = queries['value']
    # 环境变量
    context = environ['fc.context']
    domain_name = os.environ['domain_name']
    # 构建AliDNS客户端
    client = get_client(context.credentials)
    # 获得当前域名解析记录
    describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
        domain_name=domain_name
    )
    records = client.describe_domain_records(describe_domain_records_request)
    # 添加或更改解析记录
    curent_records = records.body.domain_records.record
    record_exists = False
    current_record = None
    for record in curent_records:
        record = TeaCore.to_map(record)
        if record['RR'] == queries['prefix'] and record['Type'] == queries['type']:
            record_exists = True
            current_record = record
            break
    ## 更新记录
    if record_exists:
        update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
            record_id=current_record['RecordId'],
            rr=queries['prefix'],
            type=queries['type'],
            value=value,
            ttl=600
        )
        try:
            result = client.update_domain_record(update_domain_record_request)
            # Return
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return ['Record updated.'.encode()]
        except Exception as e:
            status = '400 Bad Request'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [str(e).encode()]
    ## 添加记录
    add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
        domain_name=domain_name,
        rr=queries['prefix'],
        type=queries['type'],
        value=value,
        ttl=600
    )
    try:
        result = client.add_domain_record(add_domain_record_request)
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Record added.'.encode()]
    except Exception as e:
        status = '400 Bad Request'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [str(e).encode()]