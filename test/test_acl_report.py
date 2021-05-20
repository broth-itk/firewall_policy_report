import re
import os

# From the named script import the functions to be tested
from main import create_fw_dict
import asa
import ckp
from .example_acls import ckp_acl


# INPUT_DATA: Tests that the input file of FWs is converted into corretc data-model format
def test_data_model():
    my_vars = dict(user='glob_user', pword='glob_pword',
                asa=dict(user='asa_user', pword='asa_pword', fw=[dict(ip_name='10.10.10.1', user='fw_user', pword='fw_pword'), dict(ip_name='10.10.10.2')]),
                ckp=dict(fw=[dict(ip_name='10.10.20.1', user='fw_user', pword='fw_pword'), dict(ip_name='10.10.20.2')]))
    fw_type = []    # Required to stop errors
    assert dict(create_fw_dict(my_vars, 'asa')) == {'asa': [{'10.10.10.1': ('fw_user', 'fw_pword')}, {'10.10.10.2': ('asa_user', 'asa_pword')}]}
    assert dict(create_fw_dict(my_vars, 'ckp')) == {'ckp': [{'10.10.20.1': ('fw_user', 'fw_pword')}, {'10.10.20.2': ('glob_user', 'glob_pword')}]}

# ASA_FORMAT: Loads test ACLs and ensures that the ACL and Expanded ACL are output in the correct formated
def test_asa_format_data():
    # Load the files and remove blanks from acl_brief (cant do in script as in function that requires device connectivity)
    with open(os.path.join(os.path.dirname(__file__), 'example_acls', 'asa_acl_brief.txt')) as file_content:
        acl_brief_temp = file_content.read()
    with open(os.path.join(os.path.dirname(__file__), 'example_acls', 'asa_acl_expanded.txt')) as file_content:
        acl_expanded = file_content.read()
    acl_brief = []
    for item in acl_brief_temp:
        for line in item.splitlines():
            if re.match(r"^\S{8}\s\S{8}\s", line):
                acl_brief.append(line)

    acl = asa.format_acl('1.1.1.1', acl_brief, acl_expanded)
    assert acl['1.1.1.1_acl'] == [['stecap', '1', 'permit', 'ip', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                  ['stecap', '2', 'permit', 'tcp', '10.10.10.0/32', 'any_port', 'any', '443', '0', '', '', ''] ,
                                  ['mgmt', '2', 'permit', 'icmp', 'any', 'any_port', 'any', 'echo', '13759', '', '', ''] ,
                                  ['mgmt', '3', 'permit', 'icmp', '1.1.1.1/32', 'any_port', 'any', 'echo-reply', '0', '', '', ''] ,
                                  ['mgmt', '4', 'permit', 'icmp', 'any', 'any_port', '2.2.2.2/32', 'unreachable', '3028', '', '', ''] ,
                                  ['mgmt', '5', 'permit', 'icmp', '10.10.10.0/24', 'any_port', 'any', 'time-exceeded', '0', '', '', ''] ,
                                  ['mgmt', '6', 'deny', 'icmp', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                  ['mgmt', '9', 'permit', 'tcp', '10.10.10.1/32', 'any_port', 'obj_67-68', 'any_port', '0', '', '', 'inactive'] ,
                                  ['mgmt', '10', 'permit', 'tcp', 'any', '22', '20.20.20.0/24', '67-68', '9222', '', '', ''] ,
                                  ['mgmt', '11', 'permit', 'tcp', '10.10.10.1/32', 'any_port', 'obj_67-68', 'any_port', '0', '', '', ''] ,
                                  ['mgmt', '12', 'permit', 'tcp', '20.20.20.0/24', '22', 'any', '22', '1227', '', '', ''] ,
                                  ['Outside_mpc', '1', 'permit', 'icmp', 'any', 'any_port', 'any', 'echo-reply', '30', '', '', ''] ,
                                  ['Outside_mpc', '2', 'permit', 'ip', 'any', 'any_port', '185.4.167.128/28', 'any_port', '0', '', '', 'inactive'] ,
                                  ['Outside_mpc', '3', 'permit', 'tcp', 'any', 'any_port', 'obj_dc1dmznpgp03', 'any_port', '114382', '', '', ''] ,
                                  ['Outside_mpc', '4', 'permit', 'udp', 'obj_dc1dmznpgp03', 'any_port', 'obj_dc2dmzdns03', '53', '114382', '', '', ''] ,
                                  ['Outside_mpc', '5', 'permit', 'svc-grp_TCPUDP', 'intf_Outside_mpc', 'any_port', 'grp_UMB_DNS', 'domain', '0', '', '', ''] ,
                                  ['Outside_mpc', '6', 'deny', 'icmp', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                  ['outside', '2', 'deny', 'tcp', 'any', 'any_port', 'grp_HTTP_HTTPS', 'any_port', '0', '', '', ''] ,
                                  ['outside', '3', 'deny', 'ip', 'any', 'any_port', 'grp_LOCAL_NETWORKS', 'any_port', '24876', '', '', '']]

    assert acl['1.1.1.1_exp_acl'] == [['stecap', '1', 'permit', 'ip', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                      ['stecap', '2', 'permit', 'tcp', '10.10.10.0/32', 'any_port', 'any', '443', '0', '', '', ''] ,
                                      ['stecap', '2', 'permit', 'tcp', 'any', 'any_port', '10.10.10.0/24', '443', '0', '', '', ''] ,
                                      ['mgmt', '2', 'permit', 'icmp', 'any', 'any_port', 'any', 'echo', '13759', '', '', ''] ,
                                      ['mgmt', '3', 'permit', 'icmp', '1.1.1.1/32', 'any_port', 'any', 'echo-reply', '0', '', '', ''] ,
                                      ['mgmt', '4', 'permit', 'icmp', 'any', 'any_port', '2.2.2.2/32', 'unreachable', '3028', '', '', ''] ,
                                      ['mgmt', '5', 'permit', 'icmp', '10.10.10.0/24', 'any_port', 'any', 'time-exceeded', '0', '', '', ''] ,
                                      ['mgmt', '5', 'permit', 'icmp', 'any', 'any_port', '10.10.10.0/24', 'time-exceeded', '0', '', '', ''] ,
                                      ['mgmt', '6', 'deny', 'icmp', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                      ['mgmt', '10', 'permit', 'tcp', 'any', '22', '20.20.20.0/24', '67-68', '9222', '', '', ''] ,
                                      ['mgmt', '12', 'permit', 'tcp', '20.20.20.0/24', '22', 'any', '22', '1227', '', '', ''] ,
                                      ['Outside_mpc', '1', 'permit', 'icmp', 'any', 'any_port', 'any', 'echo-reply', '30', '', '', ''] ,
                                      ['Outside_mpc', '2', 'permit', 'ip', 'any', 'any_port', '185.4.167.128/28', 'any_port', '0', '', '', 'inactive'] ,
                                      ['Outside_mpc', '3', 'permit', 'tcp', 'any', 'any_port', '10.255.111.85/32', 'https', '96119', '', '', ''] ,
                                      ['Outside_mpc', '3', 'permit', 'tcp', 'any', 'any_port', '10.255.111.85/32', 'ldaps', '15681', '', '', ''] ,
                                      ['Outside_mpc', '3', 'permit', 'tcp', 'any', 'any_port', '10.255.111.85/32', 'ldap', '2582', '', '', ''] ,
                                      ['Outside_mpc', '4', 'permit', 'udp', '10.255.111.85/32', 'any_port', '10.255.211.211/32', '53', '114382', '', '', ''] ,
                                      ['Outside_mpc', '5', 'permit', 'udp', 'intf_Outside_mpc', 'any_port', '10.255.120.14/32', 'domain', '0', '', '', ''] ,
                                      ['Outside_mpc', '5', 'permit', 'tcp', 'intf_Outside_mpc', 'any_port', '10.255.120.14/32', 'domain', '0', '', '', ''] ,
                                      ['Outside_mpc', '6', 'deny', 'icmp', 'any', 'any_port', 'any', 'any_port', '0', '', '', ''] ,
                                      ['outside', '2', 'deny', 'tcp', 'any', 'www', 'any', 'any_port', '0', '', '', ''] ,
                                      ['outside', '2', 'deny', 'tcp', 'any', 'https', 'any', 'any_port', '0', '', '', ''] ,
                                      ['outside', '3', 'deny', 'ip', 'any', 'any_port', '10.10.10.0/24', 'any_port', '24876', '', '', ''] ,
                                      ['outside', '3', 'deny', 'ip', 'any', 'any_port', '10.10.20.0/24', 'any_port', '0', '', '', '']]

# CKP_FORMAT: Loads test ACLs and ensures that the ACL and Expanded ACL are output in the correct formated
def test_ckp_format_data():
    acl_brief =  ckp_acl.acl_brief
    acl_expanded = ckp_acl.acl_expanded
    acl = ckp.format_acl('1.1.1.1', acl_brief, acl_expanded)
    assert acl['1.1.1.1_acl'] == [['appctrl', 1, 'Accept', 'app', 'net_10.0.0.0', 'any_port', 'Internet', 'Office365', 0, '', '', ''],
                                  ['appctrl', 2, 'Accept', 'app', 'net_172.16.0.0', 'any_port', 'Internet', 'Facebook', 0, '', '', ''],
                                  ['appctrl', 2, 'Accept', 'app', 'net_172.16.0.0', 'any_port', 'Internet', 'Facebook Apps', 0, '', '', ''],
                                  ['appctrl', 2, 'Accept', 'app', 'net_192.168.0.0', 'any_port', 'Internet', 'Facebook', 0, '', '', ''],
                                  ['appctrl', 2, 'Accept', 'app', 'net_192.168.0.0', 'any_port', 'Internet', 'Facebook Apps', 0, '', '', ''],
                                  ['appctrl', 3, 'Accept', 'app-grp', 'grp_RFC1918', 'any_port', 'Internet', 'sites', 0, '', '', ''],
                                  ['appctrl', 4, 'Drop', 'tcp', 'net_172.16.0.0', 'any_port', 'hst_google', '443', 0, '', '', ''],
                                  ['appctrl', 4, 'Drop', 'tcp', 'net_172.16.0.0', 'any_port', 'hst_google', '80', 0, '', '', ''],
                                  ['appctrl', 5, 'Drop', 'any', 'Any', 'any_port', 'Any', 'any', 0, '', '', ''],
                                  ['inline_app_ctrl', 1, 'Drop', 'app', 'net_10.0.0.0', 'any_port', 'grp_amb_dmz_svrs', 'stesworld', 0, '', '', ''],
                                  ['inline_app_ctrl', 2, 'Accept', 'app', 'Any', 'any_port', 'Internet', 'Office365-Outlook', 0, '', '', ''],
                                  ['inline_app_ctrl', 2, 'Accept', 'app', 'Any', 'any_port', 'Internet', 'Outlook Web Access', 0, '', '', ''],
                                  ['Network', 1, 'Accept', 'any', 'rpt_hme-ckp-gw01', 'any_port', 'mgr_hme-ckp-mgmt01', 'any', 0, '', '', ''],
                                  ['Network', 1, 'Accept', 'any', 'rpt_hme-ckp-gw01', 'any_port', 'rpt_hme-ckp-gw01', 'any', 0, '', '', ''],
                                  ['Network', 1, 'Accept', 'any', 'mgr_hme-ckp-mgmt01', 'any_port', 'mgr_hme-ckp-mgmt01', 'any', 0, '', '', ''],
                                  ['Network', 1, 'Accept', 'any', 'mgr_hme-ckp-mgmt01', 'any_port', 'rpt_hme-ckp-gw01', 'any', 0, '', '', ''],
                                  ['Network', 2, 'Accept', 'svc-grp', 'NOT_grp_amb_dmz_svrs', 'any_port', 'unknown_vpn_range', 'grp_dns_dhcp', 0, '', '', ''],
                                  ['Network', 3, 'Accept', 'svc-grp', 'grp_blu_servers', 'any_port', 'NOT_grp_RFC1918', 'grp_http_https', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_INET_10.99.99.0', 'any_port', 'net_network_10.10.10.0', 'NOT_22', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_INET_10.99.99.0', 'any_port', 'net_network_10.10.10.0', 'NOT_179', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_INET_10.99.99.0', 'any_port', 'net_network_10.20.8.0', 'NOT_22', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_INET_10.99.99.0', 'any_port', 'net_network_10.20.8.0', 'NOT_179', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_network_10.99.10.0', 'any_port', 'net_network_10.10.10.0', 'NOT_22', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_network_10.99.10.0', 'any_port', 'net_network_10.10.10.0', 'NOT_179', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_network_10.99.10.0', 'any_port', 'net_network_10.20.8.0', 'NOT_22', 0, '', '', ''],
                                  ['Network', 4, 'Drop', 'tcp', 'net_network_10.99.10.0', 'any_port', 'net_network_10.20.8.0', 'NOT_179', 0, '', '', ''],
                                  ['Network', 5, 'Drop', 'svc-grp', 'hst_dmz_svr2', 'any_port', 'net_192.168.0.0', 'NOT_grp_dns_dhcp', 0, '', '', ''],
                                  ['Network', 5, 'Drop', 'svc-grp', 'hst_dmz_svr2', 'any_port', 'net_192.168.0.0', 'NOT_grp_http_https', 0, '', '', ''],
                                  ['Network', 5, 'Drop', 'svc-grp', 'hst_dmz_svr2', 'any_port', 'net_172.16.0.0', 'NOT_grp_dns_dhcp', 0, '', '', ''],
                                  ['Network', 5, 'Drop', 'svc-grp', 'hst_dmz_svr2', 'any_port', 'net_172.16.0.0', 'NOT_grp_http_https', 0, '', '', ''],
                                  ['Network', 6, 'Accept', 'svc-grp', 'grp_blu_servers', 'any_port', 'grp_amb_dmz_svrs', 'icmp-requests', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'dce-rpc', 'hst_dmz_svr1', 'any_port', 'grp_RFC1918', 'ALL_DCE_RPC', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'svc-grp', 'hst_dmz_svr1', 'any_port', 'grp_RFC1918', 'kerberos', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'svc-grp', 'hst_dmz_svr1', 'any_port', 'grp_RFC1918', 'dns', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'udp', 'hst_dmz_svr1', 'any_port', 'grp_RFC1918', '514', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'udp', 'hst_dmz_svr1', 'any_port', 'grp_RFC1918', '49', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'dce-rpc', 'hst_server1', 'any_port', 'grp_RFC1918', 'ALL_DCE_RPC', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'svc-grp', 'hst_server1', 'any_port', 'grp_RFC1918', 'kerberos', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'svc-grp', 'hst_server1', 'any_port', 'grp_RFC1918', 'dns', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'udp', 'hst_server1', 'any_port', 'grp_RFC1918', '514', 0, '', '', ''],
                                  ['Network', 7, 'Accept', 'udp', 'hst_server1', 'any_port', 'grp_RFC1918', '49', 0, '', '', ''],
                                  ['Network', 8, 'Accept', 'any', 'Any', 'any_port', 'grp_amb_dmz_svrs', 'any', 0, '', '', ''],
                                  ['Network', 9, 'POLICY_inline_app_ctrl', 'svc-grp', 'grp_RFC1918', 'any_port', 'Any', 'grp_http_https', 0, '', '', ''],
                                  ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', 'grp_RFC1918', 'any_port', 'Any', '8080', 0, '', '', '']]

    assert acl['1.1.1.1_exp_acl'] == [['appctrl', 1, 'Accept', 'app', '10.0.0.0/8', 'any_port', 'Internet', 'Office365', 0, '', '', ''],
                                      ['appctrl', 2, 'Accept', 'app', '172.16.0.0/12', 'any_port', 'Internet', 'Facebook Apps', 0, '', '', ''],
                                      ['appctrl', 2, 'Accept', 'app', '172.16.0.0/12', 'any_port', 'Internet', 'Facebook', 0, '', '', ''],
                                      ['appctrl', 2, 'Accept', 'app', '192.168.0.0/16', 'any_port', 'Internet', 'Facebook Apps', 0, '', '', ''],
                                      ['appctrl', 2, 'Accept', 'app', '192.168.0.0/16', 'any_port', 'Internet', 'Facebook', 0, '', '', ''],
                                      ['appctrl', 3, 'Accept', 'app-grp', '10.0.0.0/8', 'any_port', 'Internet', 'sites', 0, '', '', ''],
                                      ['appctrl', 3, 'Accept', 'app-grp', '192.168.0.0/16', 'any_port', 'Internet', 'sites', 0, '', '', ''],
                                      ['appctrl', 3, 'Accept', 'app-grp', '172.16.0.0/12', 'any_port', 'Internet', 'sites', 0, '', '', ''],
                                      ['appctrl', 4, 'Drop', 'tcp', '172.16.0.0/12', 'any_port', '8.8.8.8/32', '443', 0, '', '', ''],
                                      ['appctrl', 4, 'Drop', 'tcp', '172.16.0.0/12', 'any_port', '8.8.8.8/32', '80', 0, '', '', ''],
                                      ['appctrl', 5, 'Drop', 'any', 'any', 'any_port', 'any', 'any', 0, '', '', ''],
                                      ['inline_app_ctrl', 1, 'Drop', 'app', '10.0.0.0/8', 'any_port', '10.80.2.100-10.80.2.167', 'stesworld', 0, '', '', ''],
                                      ['inline_app_ctrl', 1, 'Drop', 'app', '10.0.0.0/8', 'any_port', '10.99.10.10/32', 'stesworld', 0, '', '', ''],
                                      ['inline_app_ctrl', 1, 'Drop', 'app', '10.0.0.0/8', 'any_port', '10.99.10.20/32', 'stesworld', 0, '', '', ''],
                                      ['inline_app_ctrl', 2, 'Accept', 'app', 'any', 'any_port', 'Internet', 'Office365-Outlook', 0, '', '', ''],
                                      ['inline_app_ctrl', 2, 'Accept', 'app', 'any', 'any_port', 'Internet', 'Outlook Web Access', 0, '', '', ''],
                                      ['Network', 1, 'Accept', 'any', '10.10.10.31/32', 'any_port', '10.10.10.32/32', 'any', 0, '', '', ''],
                                      ['Network', 1, 'Accept', 'any', '10.10.10.31/32', 'any_port', '10.10.10.31/32', 'any', 0, '', '', ''],
                                      ['Network', 1, 'Accept', 'any', '10.10.10.32/32', 'any_port', '10.10.10.32/32', 'any', 0, '', '', ''],
                                      ['Network', 1, 'Accept', 'any', '10.10.10.32/32', 'any_port', '10.10.10.31/32', 'any', 0, '', '', ''],
                                      ['Network', 2, 'Accept', 'udp', 'NOT_grp_amb_dmz_svrs', 'any_port', '10.80.2.100-10.80.2.167', '53', 0, '', '', ''],
                                      ['Network', 2, 'Accept', 'udp', 'NOT_grp_amb_dmz_svrs', 'any_port', '10.80.2.100-10.80.2.167', '67', 0, '', '', ''],
                                      ['Network', 3, 'Accept', 'tcp', '10.10.10.20/32', 'any_port', 'NOT_grp_RFC1918', '80', 0, '', '', ''],
                                      ['Network', 3, 'Accept', 'tcp', '10.10.10.20/32', 'any_port', 'NOT_grp_RFC1918', '443', 0, '', '', ''],
                                      ['Network', 3, 'Accept', 'tcp', '10.10.20.20/32', 'any_port', 'NOT_grp_RFC1918', '80', 0, '', '', ''],
                                      ['Network', 3, 'Accept', 'tcp', '10.10.20.20/32', 'any_port', 'NOT_grp_RFC1918', '443', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.99.0/29', 'any_port', '10.20.8.0/21', 'NOT_22', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.99.0/29', 'any_port', '10.20.8.0/21', 'NOT_179', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.99.0/29', 'any_port', '10.10.10.0/24', 'NOT_22', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.99.0/29', 'any_port', '10.10.10.0/24', 'NOT_179', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.10.0/24', 'any_port', '10.20.8.0/21', 'NOT_22', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.10.0/24', 'any_port', '10.20.8.0/21', 'NOT_179', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.10.0/24', 'any_port', '10.10.10.0/24', 'NOT_22', 0, '', '', ''],
                                      ['Network', 4, 'Drop', 'tcp', '10.99.10.0/24', 'any_port', '10.10.10.0/24', 'NOT_179', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'udp', '10.99.10.20/32', 'any_port', '172.16.0.0/12', 'NOT_67', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'udp', '10.99.10.20/32', 'any_port', '172.16.0.0/12', 'NOT_53', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'tcp', '10.99.10.20/32', 'any_port', '172.16.0.0/12', 'NOT_443', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'tcp', '10.99.10.20/32', 'any_port', '172.16.0.0/12', 'NOT_80', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'udp', '10.99.10.20/32', 'any_port', '192.168.0.0/16', 'NOT_67', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'udp', '10.99.10.20/32', 'any_port', '192.168.0.0/16', 'NOT_53', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'tcp', '10.99.10.20/32', 'any_port', '192.168.0.0/16', 'NOT_443', 0, '', '', ''],
                                      ['Network', 5, 'Drop', 'tcp', '10.99.10.20/32', 'any_port', '192.168.0.0/16', 'NOT_80', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.10/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.10/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.10/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.10/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.20/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.20/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.20/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.99.10.20/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.10.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.10/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.10/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.10/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.10/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.20/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.20/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.20/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.99.10.20/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.80.2.100-10.80.2.167', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.80.2.100-10.80.2.167', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.80.2.100-10.80.2.167', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.50.4-10.10.50.124', 'any_port', '10.80.2.100-10.80.2.167', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.10/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.10/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.10/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.10/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.20/32', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.20/32', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.20/32', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.99.10.20/32', 'echo-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'info-req', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'timestamp', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'mask-request', 0, '', '', ''],
                                      ['Network', 6, 'Accept', 'icmp', '10.10.20.20/32', 'any_port', '10.80.2.100-10.80.2.167', 'echo-request', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.99.10.10/32', 'any_port', '192.168.0.0/16', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '192.168.0.0/16', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '192.168.0.0/16', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '192.168.0.0/16', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '192.168.0.0/16', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.99.10.10/32', 'any_port', '192.168.0.0/16', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.99.10.10/32', 'any_port', '172.16.0.0/12', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '172.16.0.0/12', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '172.16.0.0/12', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '172.16.0.0/12', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '172.16.0.0/12', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.99.10.10/32', 'any_port', '172.16.0.0/12', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.99.10.10/32', 'any_port', '10.0.0.0/8', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '10.0.0.0/8', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '10.0.0.0/8', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '10.0.0.0/8', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.99.10.10/32', 'any_port', '10.0.0.0/8', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.99.10.10/32', 'any_port', '10.0.0.0/8', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.10.10.20/32', 'any_port', '192.168.0.0/16', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '192.168.0.0/16', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '192.168.0.0/16', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '192.168.0.0/16', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '192.168.0.0/16', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.10.10.20/32', 'any_port', '192.168.0.0/16', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.10.10.20/32', 'any_port', '172.16.0.0/12', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '172.16.0.0/12', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '172.16.0.0/12', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '172.16.0.0/12', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '172.16.0.0/12', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.10.10.20/32', 'any_port', '172.16.0.0/12', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'dce-rpc', '10.10.10.20/32', 'any_port', '10.0.0.0/8', 'ALL_DCE_RPC', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '10.0.0.0/8', '514', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '10.0.0.0/8', '750', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '10.0.0.0/8', '49', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'udp', '10.10.10.20/32', 'any_port', '10.0.0.0/8', '53', 0, '', '', ''],
                                      ['Network', 7, 'Accept', 'tcp', '10.10.10.20/32', 'any_port', '10.0.0.0/8', '53', 0, '', '', ''],
                                      ['Network', 8, 'Accept', 'any', 'any', 'any_port', '10.99.10.20/32', 'any', 0, '', '', ''],
                                      ['Network', 8, 'Accept', 'any', 'any', 'any_port', '10.99.10.10/32', 'any', 0, '', '', ''],
                                      ['Network', 8, 'Accept', 'any', 'any', 'any_port', '10.80.2.100-10.80.2.167', 'any', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '10.0.0.0/8', 'any_port', 'any', '80', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '10.0.0.0/8', 'any_port', 'any', '443', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '10.0.0.0/8', 'any_port', 'any', '8080', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '172.16.0.0/12', 'any_port', 'any', '80', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '172.16.0.0/12', 'any_port', 'any', '443', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '172.16.0.0/12', 'any_port', 'any', '8080', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '192.168.0.0/16', 'any_port', 'any', '80', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '192.168.0.0/16', 'any_port', 'any', '443', 0, '', '', ''],
                                      ['Network', 9, 'POLICY_inline_app_ctrl', 'tcp', '192.168.0.0/16', 'any_port', 'any', '8080', 0, '', '', '']]