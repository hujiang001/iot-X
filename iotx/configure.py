#!usr/bin/env python
#-*-coding=utf8-*-
"""
Author: hujiang001@gmail.com
ChangeLog: 2016-02-19 created

LICENCE: The MIT License (MIT)

Copyright (c) [2016] [iotX]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
path_root = os.path.split(os.path.realpath(__file__))[0]
server_ip = '127.0.0.1'
server_port = 8888
super_user_name = 'root'
super_user_password = '!23jd34Xdk_=#d'
authenticate_timeout = 10*60  #unit:second
accessKey_num_total = 1024
accessKey_num_oneUser = 5 #number of keys one user can alloc
accessKey_num_device = 5 #number of devices one key can access

accessControlAllowOrigin = '*' #Cross-Origin Resource Sharing (CORS)
