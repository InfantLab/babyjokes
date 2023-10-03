# functions to draw annotated frames, videos and time series plots.
# make use of ultralytics.utils where we can.

import ultralytics.utils as ultrautils

def drawOneFrame(baseImage, bboxes = None, keyPoints = None,speechLabels = None,objectData = None):
    '''
    redraw one frame with all the annotations we provide. 
    Use ultralytics.utils.Annotator where we can.

    Args: bboxes - keyPoints, speechLabels, objectData
    Output: annotated image
    '''
    annotator = ultrautils.plotting.Annotator(baseImage)
    for box in bboxes:
        annotator.box_label(box = box[:2], label = f"{box[0]}: {box[1]}", color = 'red')
    for kpts in keyPoints:
        kpts = kpts.reshape(17,3)
        annotator.kpts(kpts)
    return annotator.result()