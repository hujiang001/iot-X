/**
 * Author: hujiang001@gmail.com
 * ChangeLog: 2016-03-21 created

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
 **/

/**
 * user configure
 **/
var serverUrl = "http://127.0.0.1:8888"; //iotx server url
var version = "v1.0"

function makeUrl(resName, paraList){
    var url = serverUrl+"/"+version;
    switch (resName){
        case "user":
            url = url+"/users";
            break;
        case "userOne":
            url = url+"/user/"+String(paraList[0]);
            break;
        case "device":
            url = url+"/devices";
            break;
        case "deviceOne":
            url = url+"/device/"+String(paraList[0]);
            break;
        case "sensor":
            url = url+"/device/"+String(paraList[0])+"/sensors";
            break;
        case "sensorOne":
            url = url+"/device/"+String(paraList[0])+"/sensor/"+String(paraList[1]);
            break;
        case "dataSet":
            url = url+"/device/"+String(paraList[0])+"/sensor/"+String(paraList[1])+"/dataSet";
            break;
        case "commandSet":
            url = url+"/device/"+String(paraList[0])+"/sensor/"+String(paraList[1])+"/commandSet";
            break;
        case "commandSetOne":
            url = url+"/device/"+String(paraList[0])+"/sensor/"+String(paraList[1])+"/commandSet/"+paraList[2];
            break;
        case "accessKey":
            url = url+"/accessKey";
            break;
        case "deviceAuth":
            url = url+"/deviceauth";
            break;
        case "userLogin":
            url = url+"/userLogin";
            break;
        case "userLogout":
            url = url+"/userLogout/"+String(paraList[0]);
            break;
        default:
            return "null";
    }
    return url;
}

/****************************
 settings is JSON type, eg.
 settings = {
    "method":"GET",
    "url":"http://127.0.0.1:8888",
    "urlparas":{"p1":v1,"p2":v2},
    "success":function(){
    },
    "error":function(){
    },
    "data":{"x":1,"y":2},
    "header":{"user":"root","pwd":"!23jd34Xdk_=#d"}
 }
 method:GET\POST\DELETE\PUT, required
 url:required
 success:Handling callback when successful response is received, optional.
        @param: data
 error:Handling callback when error response is received, optional.
        @param: data
        @param: status
        @param: retCode
 data:Set http data,JSON type,optional. GET method cannot use data, use urlparas instead.
 urlparas: urlparas and data, two choose one.
 header:Set header parameters,JSON type,optional
 ****************************/
function send(settings){
    var xmlhttp;
    var isUrlparaUsed = false;
    var url;

    function getJsonObjLength(jsonObj) {
        var Length = 0;
        for (var item in jsonObj) {
            Length++;
        }
        return Length;
    }

    if ((settings==null)
        || (getJsonObjLength(settings)==0)){
        console.error("settings is null");
        return;
    }

    // required paras check
    if ((settings["method"]==null)
        ||(settings["url"]==null)){
        console.error("required para in null");
        return;
    }

    // urlparas and data, two choose one
    if ((settings["urlparas"]!=null)
        &&(settings["data"]!=null)){
        console.error("urlparas and data, two choose one");
        return;
    }

    if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        console.warn("XMLHttpRequest is not supported, you can use IE7+, Firefox, Chrome, Opera, Safari");
    }

    //set url paras
    url = settings["url"];
    if ((settings["urlparas"]!=null)
        && (getJsonObjLength(settings["urlparas"])!=0)){
        settings["urlparas"]["arg_carrier"]="uri";
        isUrlparaUsed = true;
        url += "?";
        var isFirst = true;
        for (var key in settings["urlparas"]){
            if (!isFirst)
                url +="&";
            isFirst = false;
            url += key+"="+String(settings["urlparas"][key]);
        }
    }

    //async is default
    xmlhttp.open(settings["method"], url, true);

    //set header
    if (settings["header"]!=null) {
        for (var key in settings["header"]) {
            xmlhttp.setRequestHeader(key, settings["header"][key]);
        }
    }

    //set body data
    if ((settings["data"]!=null)
        && (!isUrlparaUsed)) {
        //alert(JSON.stringify(settings["data"]));
        xmlhttp.send(JSON.stringify(settings["data"]));
    }else {
        xmlhttp.send();
    }

    //callback
    xmlhttp.onreadystatechange = function(){
        if(xmlhttp.readyState==4){
            if (xmlhttp.status == 200){
                if (settings["success"]!=null) {
                    settings["success"](xmlhttp.responseText);
                }
            }
            else{
                if (settings["error"]!=null) {
                    settings["error"](xmlhttp.responseText,xmlhttp.status,xmlhttp.getResponseHeader("retcode"));
                }
            }
        }

    };

}

