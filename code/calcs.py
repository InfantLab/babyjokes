# functions to help with calculations.
# Note: where possible we use ultralytics.utils functions for keypoint
# and bounding box calculations, but we also have some of our own.

# several adapted from vasc.py in github.com/infantlab/vasc

import numpy as np
import librosa


def centreOfGravity(df, frames=(), people="all", bodypart="whole"):
    """find average position of a bodypart across frames and people,
    and add these as new column in the dataframe
    useful for plotting  time series of movement.

    args:   df - dataframe of keypoints
            frames - list of frames to include
            people - list of people to include
            bodypart - which bodypart to use, default is "whole" for all keypoints
    returns:
            dataframe of average positions
    """

    if len(frames) == 0:
        frames = df.frame.unique()

    if people == "all":
        people = df.person.unique()

    if bodypart != "whole":
        raise NotImplementedError("Only whole body implemented for now")

    threshold = 0.5

    # create new columns for the centre of gravity
    df["cog.x"] = np.nan
    df["cog.y"] = np.nan

    for frame in frames:
        for person in people:
            # get the keypoints for this person in this frame
            kpts = df[(df["frame"] == frame) & (df["person"] == person)]

            if not kpts.empty:
                # get the average position of the bodypart
                if bodypart == "whole":
                    xyc = kpts.iloc[:, 8:59].to_numpy()  # just keypoints
                    xyc = xyc.reshape(-1, 3)  # reshape to n x 3 array (x,y,conf
                    avgx, avgy = avgxys(xyc, threshold)

                df.loc[
                    (df["frame"] == frame) & (df["person"] == person), "cog.x"
                ] = avgx
                df.loc[
                    (df["frame"] == frame) & (df["person"] == person), "cog.y"
                ] = avgy

    return df


def avgxys(xyc, threshold=0.5):
    """
    Given a set of x,y,conf values (a n x 3 array) calculate the average x,y values
    for all those with a confidence above the threshold.
    args:   xyc - [nrows x 3] array of x,y,conf values
            threshold - confidence threshold
    returns:    avgx, avgy
    """
    # get the x,y values where conf > threshold
    x = xyc[:, 0]
    y = xyc[:, 1]
    conf = xyc[:, 2]
    x = x[conf > threshold]
    y = y[conf > threshold]
    # calculate the average
    avgx = np.mean(x)
    avgy = np.mean(y)
    return avgx, avgy

def stdevxys(xyc, threshold=0.5):
    """
    Given a set of x,y,conf values (a n x 3 array) calculate the stdev for x,y values
    for all those with a confidence above the threshold.
    args:   xyc - [nrows x 3] array of x,y,conf values
            threshold - confidence threshold
    returns:    stdx, stdy
    """
    # get the x,y values where conf > threshold
    x = xyc[:, 0]
    y = xyc[:, 1]
    conf = xyc[:, 2]
    x = x[conf > threshold]
    y = y[conf > threshold]
    # calculate the average
    stdevx = np.std(x)
    stdevy = np.std(y)
    return stdevx, stdevy

def rowcogs(keypoints1d, threshold=0.5):
    """
    wrapper for avgxys to work with a 1d array of keypoints
    """
    # get the x,y values where conf > threshold
    xyc3 = keypoints1d.to_numpy().reshape(-1, 3)
    return avgxys(xyc3, threshold)

def rowstds(keypoints1d, threshold=0.5):
    """
        wraps stdevxys to work with a 1d array of keypoints
    """
    xycs3 = keypoints1d.to_numpy().reshape(-1, 3)
    return stdevxys(xycs3, threshold)



def normaliseCoordinates(df, xcols, ycols, frameHeight, frameWidth):
    """
    normalise the x and y pixel based coordinates to be between 0 and 1
    input: dataframe, list of column names, frame height and width
    output: dataframe with normalised coordinates
    """
    for col in xcols:
        df.iloc[:, [col]] = df.iloc[:, [col]] / frameWidth
    for col in ycols:
        df.iloc[:, [col]] = df.iloc[:, [col]] / frameHeight
    return df


def denormaliseCoordinates(df, xcols, ycols, frameHeight, frameWidth):
    """
    for normalised x and y coordinates (between 0 and 1) convert back to pixel based coordinates (between 0 and frameHeight/Width
    input: dataframe, list of column names, frame height and width
    output: dataframe with normalised coordinates
    """
    for col in xcols:
        df[col] = df[col] * frameWidth
    for col in ycols:
        df[col] = df[col] * frameHeight
    return df


def xyxy2ltwh(bbox):
    """Convert [x1 y1 x2 y2] box format to [x y w h] format."""
    if isinstance(bbox, np.ndarray):
        bbox = bbox.tolist()
    return [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]


def find_f0(audio_file):
    """
    Extract the fundamental frequency (F0) from an audio file.
    Args:
        audio_file (str): The path to the audio file.
    Returns:
        np.array: The fundamental frequency values.
    """
    # Load the audio file
    y, sr = librosa.load(audio_file)
    # Extract the fundamental frequency
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    return f0