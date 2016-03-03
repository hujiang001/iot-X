import os
path_root = os.path.split(os.path.realpath(__file__))[0]
server_ip = '127.0.0.1'
server_port = '8888'
super_user_name = 'root'
super_user_password = '!23jd34Xdk_=#d'
authenticate_timeout = 10*60  #unit:second
accessKey_num_total = 1024
accessKey_num_oneUser = 5 #number of keys one user can alloc
accessKey_num_device = 5 #number of devices one key can access
