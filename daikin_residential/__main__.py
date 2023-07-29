import asyncio
import json
import sys
from daikinaltherma.sensor import DaikinSensor
from daikinaltherma.water_heater import DaikinWaterTank
from daikinaltherma.climate import DaikinClimate
from daikinaltherma.daikin_base import Appliance
import time
from daikinaltherma.daikin_api import DaikinApi

# from daikinaltherma import daikin_api

# from daikinaltherma.daikin_api Da


async def main():
    daikin = DaikinApi()
   
    await daikin.retrieveAccessToken("", "")
    apinfo = await daikin.getApiInfo()
    try:
        json_object = json.dumps(apinfo, indent=4)
        with open("DaikinApi.apinfo.json", "w") as fObj:
            fObj.write(json_object)

    except Exception as error:
        pass
  
    devicedetails = await daikin.getCloudDeviceDetails()
    # daikindevices = await daikin.getCloudDevices()
    try:
        json_object = json.dumps(devicedetails, indent=4)
        with open("DaikinApi.devicedetails.json", "w") as fObj:
            fObj.write(json_object)

    except Exception as error:
        pass   
       
    daikindevices:dict[Appliance]  = await daikin.getCloudDevices() 
    await daikin.async_update()
    
    daikinclimate =None
    daikinwater= None
        
    for key,value in daikindevices.items():
        dev:Appliance = value
        cons = dev.energy_consumption("energy_consumption",'heating',"w")

        # await dev.updateData()
        daikinclimate = DaikinClimate(dev)
        daikinwater= DaikinWaterTank(dev)
        temp = daikinclimate.current_temperature
        watertemp=daikinwater.current_temperature
        watertargettemp=daikinwater.target_temperature
        print(temp)
        
    sensors = daikin.createSensors()
     
    while True:
        await daikin.async_update()
        if daikinclimate !=None:
            temp = daikinclimate.current_temperature
            print(temp)
        if daikinwater !=None:
            watertemp=daikinwater.current_temperature
            watertargettemp=daikinwater.target_temperature
            print(watertemp)
            print(watertargettemp)
            current_operation = daikinwater.current_operation
            if current_operation =='off':
                await daikinwater.async_set_tank_state('heat_pump')
            if watertargettemp!=46:
                await daikinwater.async_set_tank_temperature(46)

        for sensor in sensors:
            sens:DaikinSensor = sensor
            name = sens.name
            device_info = sens.device_info
            unique_id = sens.unique_id
            state = sens.state
            print(f"sensor:{name}-{unique_id} = {state}")
            
        time.sleep(5)
        
   

        # logger.error(f"writeMetaDataToFile Error: {error}")
        # logger.info(

    # print(a)


# resp = await controller.getApiInfo()
# _LOGGER.info("\nAPI INFO: %s\n",resp)
# resp = await controller.getCloudDeviceDetails()
# with open("daikin_data.json", 'w') as jsonFile:
# 	_LOGGER.info("Dumping json file daikin_data.json\n")
# 	json.dump(resp, jsonFile, indent=4, sort_keys=True)


if __name__ == "__main__":
    # await main()
    asyncio.run(main())


print("END")

sys.exit(0)
