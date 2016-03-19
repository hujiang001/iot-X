

<span id="top">


* [Overview](#overview) 
* [下载和安装](#下载和安装)
* [第一个例子](#第一个例子)
* [RESTFul实现](#RESTFul实现) 
* [认证](#认证) 
* [权限管理](#权限管理) 
* [安全性考虑](#安全性考虑) 
* [websocket支持](#websocket支持) 
* [RESTFul API参考](#api)


<span id="overview">
###Overview<span style="font-size:11px">[top↑](#top)</span>
 iotx是一个开源的物联网平台，提供从设备(传感器)到远端云平台的一整套解决方案。 
 iotx的特点是：
 
 1. 完全开源，遵循MIT lincese，无论是个人还是商用，都可以免费下载使用。[去github下载](https://github.com/hujiang001/iot-X)
 *  部署简单灵活，仅需要简单的步骤，用户便可以轻松搭建自己的物联网系统。
 *  可扩展性强，iotx的设备无关性，使其支持几乎所有设备接入和控制。
 *  兼容性，iotx兼容目前主流的物联网协议，包括restful、mqtt、coap、alljoyn等。
 *  提供基于raspberryPi和auduiro的廋终端，并且提供丰富的设备驱动。
 *  支持大数据处理。
 *  客户端可定制。
 
 iotx同时搭建了服务器（iotx游乐场playground），用户可以轻松接入进行体验：[去playground体验]()
 
 

<span id="下载和安装">
###下载和安装<span style="font-size:11px">[top↑](#top)</span>
 
<span id="第一个例子">
###第一个例子<span style="font-size:11px">[top↑](#top)</span>
 

<span id="RESTFul实现"> 
###RESTFul实现<span style="font-size:11px">[top↑](#top)</span>

iotX支持通过RESTFul方式接入服务器。它是基于tornado实现的http服务。

* 消息格式和携带方式

  **Request消息** 支持通过http协议的body携带，以JSON格式组织数据。同样，为了某些场景中使用的简便，我们也支持通过URL问号(?)的方式携带参数，这种方式下你需要在URL中携带特殊的参数`arg_carrier=uri`。两种方式携带的参数定义保持一致。

  >注意，在下面的API参考中，我们只介绍通过body携带的JSON格式

  **Response消息** 通过http协议中的body携带。返回的Response消息中还包含了status信息和错误码。其中错误码是通过header中的`retcode`参数携带。[查看status和错误码的定义](#errcode)

* RESTFul资源定义

  参见[RESTFul API参考](#api)
  
* user
  
  user中预留了userDefArea字段，使用者可以自己定义额外的用户信息。我们只定义了一些必须的参数。

* 设备数据上报和查询

  通过dataSet实现数据的上报和查询。我们不关心数据的具体含义和内容，仅透传。数据应该由使用者，也就是业务层面来进行定义。

* command

  通过command来实现对设备的远程控制。同样地，我们对command的具体含义也做透传，由使用者去定义。
  >注意，如果不支持websocket，那么http协议无法做到server端主动向设备推送命令，需要设备端轮询command的状态。iotx的廋终端将提供轮询接口

<span id="认证">
###认证<span style="font-size:11px">[top↑](#top)</span>

<span id="权限管理">
###权限管理<span style="font-size:11px">[top↑](#top)</span>



<span id="安全性考虑">
###安全性考虑<span style="font-size:11px">[top↑](#top)</span>


<span id="websocket支持">
###websocket支持<span style="font-size:11px">[top↑](#top)</span>









<span id="api"> 
###RESTFul API 参考<span style="font-size:11px">[top↑](#top)</span>
1. [user](#user)
* [userOne](#userOne)
* [device](#device)
* [deviceOne](#deviceOne)
* [sensor](#sensor)
* [sensorOne](#sensorOne)
* [dataSet](#dataSet)
* [commandSet](#commandSet)
* [commandSetOne](#commandSetOne)
* [accessKey](#accessKey)
* [deviceAuth](#deviceAuth)
* [userLogin](#userLogin)
* [userLogout](#userLogout)
* [错误码&status定义](#errcode)

<span id="user"> 
###user <span style="font-size:10px">[api list↑](#api)</span>



**URI: **`/v1.0/users`

**Method List: ** [GET](#user_get)  [POST](#user_post)

--------

<span id="user_get"> 
**Method:** GET<span style="font-size:11px">[back↑](#user)</span>

**功能描述：**获取user列表

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘user’ | all       | get      |

系统默认只有超级管理员有此权限

**Request:**

JSON

    {
         'sort':'DESC', 
         'maxNum':0, 
         'skipNum':0
     }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|O|sort   | 排序方式 DESC\ASC| string|  DESC|
|M|maxNum   | 查询个数| integer|  0|
|O|skipNum   | 查询偏移数，系统会将结果偏移一定数目再获取maxNum条数据。可以使用该参数来分批获取大量数据。| integer|  0|


注意，有些参数是可选的，有而些则是必选的[^optional]


[^optional]: O:optional  M:Mandatory

**Response：**

* body

JSON

    {
        'num':0,
        'isEof':False,
        'list':[ ] 
    }

| params | description | type    |
| ------ | --------- | ----------|
| num   | list的记录条数| integer|
| isEof   | 是否是最后一条记录| boolean|
| list | user列表。列表的具体内容参考userOne的GET返回值|list|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  

<span style="font-size:11px">[back↑](#user)

-------------------
<span id="user_post"> 

**Method:** POST<span style="font-size:11px">[back↑](#user)</span>

**功能描述：**创建一个user

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘user’ | all       | add      |

系统默认所有人都可以创建用户，即注册用户。

**Request:**

JSON

    {
         'name':'', 
         'pwd':‘’，
         'userDefArea':‘’
     }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| name   | 用户名| string|  None|
| pwd   | 密码| string|  None|
| userDefArea   | 用户自定义域。可以自定义一些用户数据，比如电话号码、住址等，系统不关心仅透传，建议用JSON组织数据。| string|  None|

**Response：**

* body

JSON

    {
        'id':0 
    }

| params | description | type    |
| ------ | --------- | ----------|
| id   | user id，如果失败，id填0| integer|



* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#user)</span>

---------------------  
  
  
  
<span id="userOne"> 
###userOne<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/user/$id`

**Method List: ** [GET](#userOne_get)  [PUT](#userOne_put) [DELETE](#userOne_delete)

--------
<span id="userOne_get">
**Method:** GET<span style="font-size:11px">[back↑](#userOne)</span>

**功能描述：**获取一个指定的user信息

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘user’ | id       | get      |


**Request:**

id：从URI中提取


**Response：**

* body

JSON

    {
       'id':0,
       'name':'',
       'regTime':'',
       'lastLoginTime':'',
       'state':'offline',
       'userDefArea':'',
       'deviceList':[ ]
     }

| params | description | type    |
| ------ | --------- | ----------|
| id   | user id| integer|
| name   | user name| string|
| regTime | user注册时间，也就是post时间.格式："%Y-%m-%d %H:%M:%S"|string|
| lastLoginTime| user最近一次登录时间.格式："%Y-%m-%d %H:%M:%S"|string|
|state|user状态。offline\online|string|
|userDefArea|用户注册时的自定义域|string|
|deviceList|该用户的deviceId列表|list|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#userOne)</span>

-------------------
<span id="userOne_put">
**Method:** PUT<span style="font-size:11px">[back↑](#userOne)</span>

**功能描述：**更新一个指定的user

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘user’ | id       | upd      |



**Request:**

id：从URI中提取

JSON

     {
         'oldpwd':None, 
         'pwd':None，
         'userDefArea':None
     }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| oldpwd   | 老的密码，只有修改密码时该值才必须填写| string|  None|
| pwd   | 新的密码| string|  None|
| userDefArea   | 用户自定义域。| string|  None|

**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#userOne)</span>  
  
-------------------
<span id="userOne_delete">
**Method:** DELETE<span style="font-size:11px">[back↑](#userOne)</span>

**功能描述：**删除一个指定的user

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘user’ | id       | del      |



**Request:**

id：从URI中提取


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
 
<span style="font-size:11px">[back↑](#userOne)</span>

-------------------  

  
<span id="device"> 
###device<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/devices`

**Method List: ** [GET](#device_get)  [POST](#device_post)

--------

<span id="device_get"> 
**Method:** GET<span style="font-size:11px">[back↑](#device)</span>

**功能描述：**获取device列表

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | all       | get      |

系统默认只有超级管理员有此权限

**Request:**

JSON

    {
         'sort':'DESC', 
         'maxNum':0, 
         'skipNum':0
     }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| sort   | 排序方式 DESC\ASC| string|  DESC|
| maxNum   | 查询个数| integer|  0|
| skipNum   | 查询偏移数，系统会将结果偏移一定数目再获取maxNum条数据。可以使用该参数来分批获取大量数据。| integer|  0|

**Response：**

* body

JSON

    {
        'num':0,
        'isEof':False,
        'list':[ ] 
    }

| params | description | type    |
| ------ | --------- | ----------|
| num   | list的记录条数| integer|
| isEof   | 是否是最后一条记录| boolean|
| list | user列表。列表的具体内容参考deviceOne的GET返回值|list|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#device)</span>

-------------------
<span id="device_post"> 

**Method:** POST<span style="font-size:11px">[back↑](#device)</span>

**功能描述：**创建一个device

**认证方式：**user和accessKey，accessKey通过[GET](#accessKey_get)方法申请

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | all       | add      |


**Request:**

JSON

    {
        'name':'',
        'description':'',
        'local':'',
        'latitude':0.0,
        'longitude':0.0,
        'userDefArea':''
    }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| name   | 设备名| string|  None|
| description   | 设备描述| string|  None|
| local| 设备位置描述|string|None|
|latitude|设备所处经度|float|0.0|
|longitude|设备所处纬度|float|0.0|
| userDefArea   | 设备自定义域。可以自定义一些设备数据，系统不关心仅透传，建议用JSON组织数据。| string|  None|

**Response：**

* body

JSON

    {
        'id':0 
    }

| params | description | type    |
| ------ | --------- | ----------|
| id   | 设备 id，如果失败，id填0| integer|



* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#device)</span>

------------------------  
  
  
  
<span id="deviceOne"> 
###deviceOne<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$id`

**Method List: ** [GET](#deviceOne_get)  [PUT](#deviceOne_put) [DELETE](#deviceOne_delete)

--------
<span id="deviceOne_get">
**Method:** GET<span style="font-size:11px">[back↑](#deviceOne)</span>

**功能描述：**获取一个指定的device信息

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | id       | get      |


**Request:**

id：从URI中提取


**Response：**

* body

JSON

    {
        'id':0, 
        'name':'',
        'description':'', 
        'regTime':'', 
        'local':'Beijing',
        'latitude':0.0,
        'longitude':0.0,
        'userDefArea':'',
        'userIdList':[ ], 
        'sensorList':[ ],
        'key':'' 
     }

| params | description | type    |
| ------ | --------- | ----------|
| id   | device id| integer|
| name   | device name| string|
| description   | device的描述信息| string|
| regTime | device注册时间，也就是post时间.格式："%Y-%m-%d %H:%M:%S"|string|
| local| 设备位置描述|string|
|latitude|设备所处经度|float|
|longitude|设备所处纬度|float|
| userDefArea   | 设备自定义域| string| 
|userIdList|该设备所属的用户Id列表|list|
|sensorList|该设备下的sensorId列表|list|
|key|该设备的accessKey|string|

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#deviceOne)</span>

-------------------
<span id="deviceOne_put">
**Method:** PUT<span style="font-size:11px">[back↑](#deviceOne)</span>

**功能描述：**更新一个指定的device

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | id       | upd      |



**Request:**

id：从URI中提取


JSON

    {
        'name':'',
        'description':'', 
        'local':'Beijing',
        'latitude':0.0,
        'longitude':0.0,
        'userDefArea':''
     }

| params | description | type    |default|
| ------ | --------- | ----------|-------|
| name   | device name| string|None|
| local| 设备位置描述|string|None|
|latitude|设备所处经度|float|None|
|longitude|设备所处纬度|float|None|
| userDefArea   | 设备自定义域| string|None|


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#deviceOne)</span>  
  
-------------------
<span id="deviceOne_delete">
**Method:** DELETE<span style="font-size:11px">[back↑](#deviceOne)</span>

**功能描述：**删除一个指定的device

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | id       | del      |



**Request:**

id：从URI中提取


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#deviceOne)</span>

--------------------




  
<span id="sensor"> 
###sensor<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$deviceId/sensors`

**Method List: ** [GET](#sensor_get)  [POST](#sensor_post)

--------

<span id="sensor_get"> 
**Method:** GET<span style="font-size:11px">[back↑](#sensor)</span>

**功能描述：**获取指定device下的sensor列表

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId  | get      |
| ‘sensor’ | all       | get      |

首先必须拥有所属device的get权限，同时也需要拥有sensor的get权限。

**Request:**

deviceId：从URI中提取

JSON

    {
         'sort':'DESC', 
         'maxNum':0, 
         'skipNum':0
     }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| sort   | 排序方式 DESC\ASC| string|  DESC|
| maxNum   | 查询个数| integer|  0|
| skipNum   | 查询偏移数，系统会将结果偏移一定数目再获取maxNum条数据。可以使用该参数来分批获取大量数据。| integer|  0|

**Response：**

* body

JSON

    {
        'num':0,
        'isEof':False,
        'list':[ ] 
    }

| params | description | type    |
| ------ | --------- | ----------|
| num   | list的记录条数| integer|
| isEof   | 是否是最后一条记录| boolean|
| list | sensor列表。列表的具体内容参考sensorOne的GET返回值|list|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#sensor)</span>

-------------------
<span id="sensor_post"> 

**Method:** POST<span style="font-size:11px">[back↑](#sensor)</span>

**功能描述：**创建一个指定device的sensor

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |

拥有所属device的upd权限即可添加sensor

**Request:**

deviceId：从URI中提取

JSON

    {
        'name':'',
        'description':'',
        'userDefArea':''
    }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| name   | sensor名| string|  None|
| description   | sensor描述| string|  None|
| userDefArea   | sensor自定义域。可以自定义一些sensor信息，系统不关心仅透传，建议用JSON组织数据。| string|  None|

**Response：**

* body

JSON

    {
        'id':0 
    }

| params | description | type    |
| ------ | --------- | ----------|
| id   | sensor id，如果失败，id填0| integer|



* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#sensor)</span>
  
-----------------------  
  
  
  
<span id="sensorOne"> 
###sensorOne<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$deviceId/sensor/$sensorId`

**Method List: ** [GET](#sensorOne_get)  [PUT](#sensorOne_put) [DELETE](#sensorOne_delete)

--------
<span id="sensorOne_get">
**Method:** GET<span style="font-size:11px">[back↑](#sensorOne)</span>

**功能描述：**获取一个指定的sensor信息

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | get      |
| ‘sensor’ | sensorId       | get      |

首先必须拥有所属device的get权限，同时也需要拥有sensor的get权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

**Response：**

* body

JSON

    {
        'id':0, 
        'name':'',
        'description':'', 
        'regTime':'', 
        'deviceId':0,
        'userDefArea':'' 
     }

| params | description | type    |
| ------ | --------- | ----------|
| id   | sensor id| integer|
| name   | sensor name| string|
| description   | sensor的描述信息| string|
| regTime | sensor注册时间，也就是post时间.格式："%Y-%m-%d %H:%M:%S"|string|
|deviceId|所属device的Id|integer|
| userDefArea   | sensor自定义域| string| 

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#sensorOne)</span>

-------------------
<span id="sensorOne_put">
**Method:** PUT<span style="font-size:11px">[back↑](#sensorOne)</span>

**功能描述：**更新一个指定sensor的信息

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | upd      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的upd权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取


JSON

    {
        'name':'',
        'description':'', 
        'userDefArea':''
     }

| params | description | type    |default|
| ------ | --------- | ----------|-------|
| name   | sensor name| string|None|
| description| sensor描述信息|string|None|
| userDefArea   | sensor自定义域| string|None|


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#sensorOne)</span>

-------------------
<span id="sensorOne_delete">
**Method:** DELETE<span style="font-size:11px">[back↑](#sensorOne)</span>

**功能描述：**删除一个指定的sensor

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | del      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的del权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#sensorOne)</span>

---------------------



<span id="dataSet"> 
###dataSet<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$deviceId/sensor/$sensorId/dataSet`

**Method List: ** [GET](#dataSet_get)  [POST](#dataSet_post) [PUT](#dataSet_put) [DELETE](#dataSet_delete)

--------
<span id="dataSet_get">
**Method:** GET<span style="font-size:11px">[back↑](#dataSet)</span>

**功能描述：**获取data

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | get      |
| ‘sensor’ | sensorId       | get      |

首先必须拥有所属device的get权限，同时也需要拥有sensor的get权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

JSON

    {
        'sort':'desc',
        'orderBy':'',
        'maxNum':0,
        'skipNum':0,
        'createTimeStart':None,
        'createTimeEnd':None,
        'lastUpdateTimeStart':None,
        'lastUpdateTimeEnd':None,
        'key':None,
        'valueMin':None,
        'valueMax':None 
     }

| params | description | type    |default|
| ------ | --------- | ----------|-------|
| sort   | 排序方式，DESC\ASC| string|DESC|
| orderBy|排序字段，CREATE_TIME\LAST_UPDATE_TIME\KEY\VALUE | string|CREATE_TIME|
| maxNum   |最多返回的记录条数| integer|0|
| skipNum | 偏移的记录条数|integer|0|
|createTimeStart|过滤条件：创建时间大于等于值。格式："%Y-%m-%d %H:%M:%S"|string|None|
|createTimeEnd|过滤条件：创建时间小于等于值。格式："%Y-%m-%d %H:%M:%S"|string|None|
|key|过滤条件：key值等于|string|None|
|valueMin|过滤条件：value值大于等于值|string|None|
|valueMax|过滤条件：value值小于等于值|string|None|


**Response：**

* body

JSON

    {
        'num':0,
        'isEof':False,
        'list':[ 
        		{
                    'createTime':'',
                    'lastUpdateTime':'',
                    'key':'', 
                    'value':''
                }
        ] 
    }

| params | description | type    |
| ------ | --------- | ----------|
| num   | list的记录条数| integer|
| isEof   | 是否是最后一条记录| boolean|
| list | data列表|list|
| createTime | 创建时间，格式："%Y-%m-%d %H:%M:%S"|string|
| lastUpdateTime | 最后一次更新时间，格式："%Y-%m-%d %H:%M:%S"|string|
| key | data的key值，由使用者自己定义，系统不感知|string|
| value | data的value值|string|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#dataSet)</span>

-------------------

<span id="dataSet_post">
**Method:** POST<span style="font-size:11px">[back↑](#dataSet)</span>

**功能描述：**创建一个data

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | upd      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的upd权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

JSON

    {
        'key':None,
        'value':None
     }

| params | description | type    |default|
| ------ | --------- | ----------|--------|
|key|data的key值，使用者定义，系统不感知|string|None|
|value|data的value|string|None|


**Response：**

* body

JSON

    {
        'createTime':‘’
    }

| params | description | type    |
| ------ | --------- | ----------|
| createTime | 创建时间，格式："%Y-%m-%d %H:%M:%S"|string|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#dataSet)</span>

-------------------



<span id="dataSet_put">
**Method:** PUT<span style="font-size:11px">[back↑](#dataSet)</span>

**功能描述：**更新一个或多个data

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | upd      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的upd权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

JSON

    {
    	‘createTime’:None
        'key':None,
        'value':None
     }

|| params | description | type    |default|
|-| ------ | --------- | ----------|--------|
|O|createTime | 创建时间作为过滤条件，格式："%Y-%m-%d %H:%M:%S"|string|None|
|M|key|data的key值|string|None|
|M|value|data的value|string|None|


**Response：**

* body

{ } or None


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#dataSet)</span>

-------------------




<span id="dataSet_delete">
**Method:** DELETE<span style="font-size:11px">[back↑](#dataSet)</span>

**功能描述：**删除一个或多个data

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | upd      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的upd权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

JSON

    {
    	‘createTimeStart’:None,
    	‘createTimeEnd’:None
        'key':None
     }

|| params | description | type    |default|
|-| ------ | --------- | ----------|--------|
|O|createTimeStart | 创建时间作为过滤条件，格式："%Y-%m-%d %H:%M:%S"|string|None|
|O|createTimeEnd | 创建时间作为过滤条件，格式："%Y-%m-%d %H:%M:%S"|string|None|
|O|key|data的key值|string|None|


**Response：**

* body

{ } or None


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#dataSet)</span>

-------------------





  
<span id="commandSet"> 
###commandSet<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$deviceId/sensor/$sensorId/commandSet`

**Method List: ** [GET](#commandSet_get)  [POST](#commandSet_post)

--------

<span id="commandSet_get"> 
**Method:** GET<span style="font-size:11px">[back↑](#commandSet)</span>

**功能描述：**获取指定sensor的command列表

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId  | get      |
| ‘sensor’ | sensorI   | get      |

首先必须拥有所属device的get权限，同时也需要拥有sensor的get权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取


JSON

    {
         'sort':'DESC', 
         'maxNum':0, 
         'skipNum':0
     }

| params | description | type    | default |
| ------ | --------- | ----------| --------|
| sort   | 排序方式 DESC\ASC| string|  DESC|
| maxNum   | 查询个数| integer|  0|
| skipNum   | 查询偏移数，系统会将结果偏移一定数目再获取maxNum条数据。可以使用该参数来分批获取大量数据。| integer|  0|

**Response：**

* body

JSON

    {
        'num':0,
        'isEof':False,
        'list':[ ] 
    }

| params | description | type    |
| ------ | --------- | ----------|
| num   | list的记录条数| integer|
| isEof   | 是否是最后一条记录| boolean|
| list | command列表。列表的具体内容参考commandSetOne的GET返回值|list|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#commandSet)</span>

-------------------
<span id="commandSet_post"> 

**Method:** POST<span style="font-size:11px">[back↑](#commandSet)</span>

**功能描述：**创建一个指定sensor的command

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId  | upd      |
| ‘sensor’ | sensorId  | command      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的command权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取


JSON

    {
        'command':'',
        'value':''
    }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|M| command   | command名字，系统不感知具体含义，使用者自己定义| string|  None|
|M| value   | command的值| string|  None|


**Response：**

* body

{ } or None



* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#commandSet)</span>
  
-----------------------  
  
  
  
<span id="commandSetOne"> 
###commandSetOne<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/device/$deviceId/sensor/$sensorId/commandSet/$command`

**Method List: ** [GET](#commandSetOne_get)  [PUT](#commandSetOne_put) [DELETE](#commandSetOne_delete)

--------
<span id="commandSetOne_get">
**Method:** GET<span style="font-size:11px">[back↑](#commandSetOne)</span>

**功能描述：**获取一个指定的command信息

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | get      |
| ‘sensor’ | sensorId       | get      |

首先必须拥有所属device的get权限，同时也需要拥有sensor的get权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

command：从URI中提取


**Response：**

* body

JSON

    {
        'command':'',
        'value':'',
        'createTime':'',
        'lastUpdateTime':''
     }

| params | description | type    |
| ------ | --------- | ----------|
| command   | command名| string|
| value   | command的值| string|
| createTime | command创建的时间.格式："%Y-%m-%d %H:%M:%S"|string|
| lastUpdateTime | command最近一次更新的时间.格式："%Y-%m-%d %H:%M:%S"|string|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#commandSetOne)</span>

-------------------
<span id="commandSetOne_put">
**Method:** PUT<span style="font-size:11px">[back↑](#commandSetOne)</span>

**功能描述：**更新一个指定command的值

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | command      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的command权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

command：从URI中提取



JSON

    {
        'value':''
     }

|| params | description | type    |default|
|-| ------ | --------- | ----------|-------|
|M| value   |command的值| string|None|


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#commandSetOne)</span>

-------------------
<span id="commandSetOne_delete">
**Method:** DELETE<span style="font-size:11px">[back↑](#commandSetOne)</span>

**功能描述：**删除一个指定的command

**认证方式：**user或者accessKey

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId       | upd      |
| ‘sensor’ | sensorId       | command      |

首先必须拥有所属device的upd权限，同时也需要拥有sensor的command权限。

**Request:**

deviceId：从URI中提取

sensorId：从URI中提取

command：从URI中提取


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)
  
<span style="font-size:11px">[back↑](#commandSetOne)</span>

---------------------



  
<span id="deviceAuth"> 
###deviceAuth<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/deviceauth`

**Method List: ** [POST](#deviceAuth_post)  [DELETE](#deviceAuth_delete)

--------

<span id="deviceAuth_post"> 
**Method:** POST<span style="font-size:11px">[back↑](#deviceauth)</span>

**功能描述：**为一个user增加device的权限

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId  | privilege_add      |



**Request:**

JSON

    {
         'deviceId':0, 
         'userId':0, 
         'privilege':None,
         'role':None
     }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|M| deviceId| device id| integer|  0|
|M| userId   | user id| integer|  0|
|O| privilege   | 该device的操作权限列表，以'\|'分隔。权限的取值请参考[权限管理](#权限管理)| string|  None|
|O| role   |用户角色。角色的定义请参考[权限管理](#权限管理)| string|  None|

>注意，privilege和role两个参数二选一即可，如果两个都有效，那么系统以privilege为准。

**Response：**

* body

{ } or None


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#deviceAuth)</span>

-------------------

<span id="deviceAuth_delete"> 
**Method:** DELETE<span style="font-size:11px">[back↑](#deviceauth)</span>

**功能描述：**删除use的一个device的权限

**认证方式：**user

**权限要求：**

| object | object_id | operlist |
| ------ | --------- | -------- |
| ‘device’ | deviceId  | privilege_del      |



**Request:**

JSON

    {
         'deviceId':0, 
         'userId':0
     }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|M| deviceId| device id| integer|  0|
|M| userId   | user id| integer|  0|


>注意，目前不支持删除单个权限，如果权限变更，需要全部删除后再重新添加

**Response：**

* body

{ } or None


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#deviceAuth)</span>

-------------------


<span id="accessKey"> 
###accessKey<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/accessKey`

**Method List: ** [GET](#accessKey_get)

--------

<span id="accessKey_get"> 
**Method:** GET<span style="font-size:11px">[back↑](#accessKey)</span>

**功能描述：**申请一个accessKey

**认证方式：**user

**权限要求：**

系统默认登录用户即可申请accessKey


**Request:**

JSON

    {
         'userId':0
     }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|M| userId   | user id| integer|  0|


**Response：**

* body

JSON

    {
         'key':''
     }

|params | description | type    | default |
| ------ | --------- | ----------| --------|
| key   | 申请成功的key，如果失败则返回None| string|  None|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#accessKey)</span>

-------------------


<span id="userLogin"> 
###userLogin<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/userLogin`

**Method List: ** [POST](#userLogin_post)

--------

<span id="userLogin_post"> 
**Method:** POST<span style="font-size:11px">[back↑](#userLogin)</span>

**功能描述：** user登录

**认证方式：** None

**权限要求：**

None


**Request:**

JSON

    {
         'name':None,
         'pwd':None
     }

|| params | description | type    | default |
|-| ------ | --------- | ----------| --------|
|M| name   | user name| string|  None|
|M| pwd   | user password| string|  None|


**Response：**

* body

JSON

    {
         'id':0
     }

|params | description | type    | default |
| ------ | --------- | ----------| --------|
| id   | user id| integer|  0|


* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#userLogin)</span>

-------------------


<span id="userLogout"> 
###userLogout<span style="font-size:11px">[api list↑](#api)</span>

**URI: **`/v1.0/userLogout/$id`

**Method List: ** [POST](#userLogout_post)

--------

<span id="userLogout_post"> 
**Method:** POST<span style="font-size:11px">[back↑](#userLogout)</span>

**功能描述：** user登出

**认证方式：** user

**权限要求：**

None


**Request:**

id：从URI中提取


**Response：**

* body

{ } or None

* status
  
  参考[错误码&status定义](#errcode)

* retcode
  
  参考[错误码&status定义](#errcode)

<span style="font-size:11px">[back↑](#userLogout)</span>

-------------------


  
<span id="errcode">  
###错误码&status定义<span style="font-size:11px">[api list↑](#api)</span>

>注意：错误码是通过HTTP头里面的‘retcode’字段携带。

* status

  200 - OK
  
  401 - 处理失败，详细信息以retcode为准。
  
  500 - 服务器处理异常，详细信息以retcode为准。

* retcode
  
  ‘USER_OFFLINE’：user没有登录，或者用户名密码认证失败
  
  ‘NO_PRIVILEGE’：用户没有操作权限


























