# AutoAPT

This project is an automated demo controller for the APT software suite.

It currently has a working installer via pynsist, which can be downloaded via the pynsist-build.zip file.

## Architecture

This system utilizes a few key components to operate the demo system:
- Controller: This is the central intelligence of the demo system. It will spin up the actual demo, trigger job and data generation, and handle signal triggers from the dispatcher. It holds the two deques in use.
- Dispatcher: (Threaded) The dispatcher reads from each of the two controller deques, named command_queue and proc_queue in order to process incoming payload requests, inform the controller on required actions.
- Socket Server: (Threaded) This is a very simple TCP Socket Server handling incoming connections from the APT Server, announcing demo control states (from flask interface) and job control triggers from APT Server.
- Web Interface: The embedded web interface is a small flask website which provides some basic configuration details for the APT System, along with a control interface to start/pause/stop the demo.
- JIF Generator: This is the core of the job control file, and data processing generation. It utilizes configuration files to create a randomized Job to send to APT, along with requisite output data.

This will currently power up to 7 indirect connection devices, providing for a lifelike demo system, along with all historical processing details for a fully fleshed system. Simply turn on and let it run.

## External Modules/Dependancies
- Flask: This is the only current external module (non built in) required for this system.
- APT Server: This is required as the system needs the folder locations created by the APT Server to function. It will not auto-create them at this time (though it should for testing..)

## Running the system
Once you have the system and flask installed, simply run:

```
python autoapt.py
```

Then point a browser to http://127.0.0.1:8080 

The default page is the demo control setup, there is an instruction link in the nav bar for APT Server setup with general instructions.

## License
MIT License

Copyright (c) 2016 Tim Rogers

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
