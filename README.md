# PaserExclusionApi

**What is this?**

 1. FastApi Server for an interactive Exclusion List      
 2. Streamlit Server to serve as the API GUI and advance features
 
## FastApi Server:
The FastApi server contains a single active exclusion list and stores ExclusionIntervals. These intervals contain an id, charge, and min/max bounds for  (mass, rt, ook0 and intensity). All attributes of the ExclusionInterval can be None. Noen valeus are considered to be all inclusive. For example if charge=None, this is interpreseted to mean that this interval applies to all charge states. Similarly, if exclusion_id=None, this interval would applie to all intervals regardless of thier interval_id. Finally, if min_bound/max_bound=None, these are converted to the min_float and max_float values.

see http://127.0.0.1:8000/docs for more information.

$uvicorn main:app --reload --port 8000

**exclusion/**

 - delete: clear active list
 - post: save/load active list
 - get: statistics

**exclusion/file:**  

 - delete: deleted saved file
 - post: upload saved file
 - get: dowload saved file

**exclusion/interval**  
 - delete: deleted interval from active list
 - post: add interval to active list
 - get: query intervals from active list
 - delete: delete intervals from active list
 
**exclusion/point**  
 - get: get overlapping intervals with point

**exclusion/points**  
 - get: boolean list for whether points overlaps with intervals

## Streamlit Server:

The streamlit server is used as an interface to the PaserExclusionApi. In addition to provide a GUI interface for all api calls, it also provides functions to exclude ions from an experiment or a file.

$streamlit run home.py --server.port 8501  
  
## Bugs:
 
**Duplicate Interval (Non critical):**  
  
Currently there is an ID_Table and an IntervalTree used to store the ExclusionIntervals and their associated IDs.  
The IntervalTree does not support duplicate intervals while the ID_Table does. This can create an issue, where  
some ExclusionInterval do not get deleted from both instances, with these 'ghost' intervals still existing in  
the ID_Table. Will be resolved when the underlying data structure is switched to an R-Tree.