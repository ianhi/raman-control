## Capture using Preview

will need to install callbacks for this to work. Carries the benefit of being able to link to a progressbar.

**matlab version**
add a callback to the lightfield object
```matlab
evData = addlistener(exp,'ImageDataSetReceived',@(src,evnt)experimentDataReady_snap(src,evnt,source));
```
then here is the important part of the callback

```matlab
function experimentDataReady_snap(src,evnt,varargin)
global data exp save_dir exp_name i hTaskAO hTaskDO x_steps y_steps raman_peak

fprintf("%d\n",i);

if i==0
%     skip first data frame as the shutter is not open yet
    i=1;
elseif (i<size(data,1))
%     deep copy spectrum into data matrix
    data(i,:) = uint16(varargin{1}.ImageDataSet.GetFrame(0,0).GetData());
    i=i+1;
```

and additional benefit is that Koseki said that the lightfield rep said this approach has lower overhead than the capture method.

## trigger raman on callbacks to pycromanager on multidim acq

##
