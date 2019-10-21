# uEagle (non-micro)
(non-)Micropython Rainforest EAGLE client

This branch includes compatibility for non-uPython environments.

Basic, lightweight client for accessing the local REST API of Rainforest Automation's EAGLE device.

Example use:

```python
from uEagle import Eagle
 
CLOUD_ID = '012abc'
INSTALL_CODE = '0123456789abcdef'
ADDRESS = '192.168.1.123' #optional if your platform can resove mDNS
 
eagle = Eagle(CLOUD_ID, INSTALL_CODE, address=ADDRESS)
 
demand_data = eagle.get_instantaneous_demand()
print('Current Usage: {:.3f} kW'.format(demand_data['Demand']))
```
