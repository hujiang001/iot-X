#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <Python.h>
#define MAX_TIME 85
#define DHT11PIN 7
#define ATTEMPTS 5                 //retry 5 times when no response
int dht11_val[5]={0,0,0,0,0};
  
int dht11_read_val_ex(unsigned int *pui_rh, unsigned int *pui_temperature){
    uint8_t lststate=HIGH;         //last state
    uint8_t counter=0;
    uint8_t j=0,i;
    for(i=0;i<5;i++)
        dht11_val[i]=0;
         
    //host send start signal    
    pinMode(DHT11PIN,OUTPUT);      //set pin to output 
    digitalWrite(DHT11PIN,LOW);    //set to low at least 18ms 
    delay(18);
    digitalWrite(DHT11PIN,HIGH);   //set to high 20-40us
    delayMicroseconds(40);
     
    //start recieve dht response
    pinMode(DHT11PIN,INPUT);       //set pin to input
    for(i=0;i<MAX_TIME;i++)         
    {
        counter=0;
        while(digitalRead(DHT11PIN)==lststate){     //read pin state to see if dht responsed. if dht always high for 255 + 1 times, break this while circle
            counter++;
            delayMicroseconds(1);
            if(counter==255)
                break;
        }
        lststate=digitalRead(DHT11PIN);             //read current state and store as last state. 
        if(counter==255)                            //if dht always high for 255 + 1 times, break this for circle
            break;
        // top 3 transistions are ignored, maybe aim to wait for dht finish response signal
        //printf("counter = %d, i = %d\r\n",counter, i);
        if((i>=4)&&(i%2==0)){
            dht11_val[j/8]<<=1;                     //write 1 bit to 0 by moving left (auto add 0)
            if(counter>16)                          //long mean 1
                dht11_val[j/8]|=1;                  //write 1 bit to 1 
            j++;
        }
    }
    // verify checksum and print the verified data
    if((j>=40)&&(dht11_val[4]==((dht11_val[0]+dht11_val[1]+dht11_val[2]+dht11_val[3])& 0xFF))){
        printf("RH:%d,TEMP:%d\n",dht11_val[0],dht11_val[2]);
        *pui_rh = dht11_val[0];
        *pui_temperature = dht11_val[2];
        return 1;
    }
    else
        return 0;
}
int retV[2] = {0,0};
int dht11_read_val(){
    int attempts=ATTEMPTS;
    int ui_rh=0;
    int ui_temperature=0;
    retV[0] = 0;
    retV[1] = 0;
    if(wiringPiSetup()==-1)
        return 0;
    while(attempts){                        //you have 5 times to retry
        int success = dht11_read_val_ex(&ui_rh, &ui_temperature);     //get result including printing out
        if (success) {                      //if get result, quit program; if not, retry 5 times then quit
            retV[0] = ui_temperature;
            retV[1] = ui_rh;
            return 1;
        }
        attempts--;
        delay(1000);
    }
    return 0;
}
int getTemperature()
{
    return retV[0];
}
int getRh()
{
    return retV[1];
}

//封装为python 模块
static PyObject * _read_data(PyObject *self, PyObject *args)
{
    dht11_read_val();
    return (PyObject *)Py_BuildValue("ii",retV[0], retV[1]);
}

static PyMethodDef DHT11ModuleMethods[] = {
    {"dht11_read_val",_read_data,METH_VARARGS,""},
    {"getTemperature",NULL,METH_VARARGS,""},
    {"getRh",NULL,METH_VARARGS,""},
    {NULL, NULL}
};

PyMODINIT_FUNC initDHT11_C(void) {
    (void) Py_InitModule("DHT11_C", DHT11ModuleMethods);
}