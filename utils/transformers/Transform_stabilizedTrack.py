import argparse
import numpy as np
import cv2
from utils.transformers.Transform_base import Transform_base
from multiprocessing import Process, Queue

def selectROI(queue, frame, flag):
    bbox = cv2.selectROI(frame, flag)
    queue.put(bbox)

class Transform_stabilizedTrack(Transform_base):
    command = 'stabilizedTrack'

    def __init__(self):
        super().__init__()
        tracker_types = ['BOOSTING', 'MIL', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT']
        tracker_type = tracker_types[3]
        print(tracker_type)

        if tracker_type == 'BOOSTING':
            tracker = cv2.legacy.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.legacy.TrackerMIL_create()
        if tracker_type == 'TLD':
            tracker = cv2.legacy.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.legacy.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.legacy.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.legacy.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.legacy.TrackerCSRT_create()

        self.tracker = tracker
        self.tracker_type = tracker_type
            
        print(tracker_type)

    def flow2img(self, flow, BGR=True):
        x, y = flow[:, :,0].astype('float64'), flow[:,  :, 1].astype('float64')
        
        hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype = np.uint8)
        ma, an = cv2.cartToPolar(x, y, angleInDegrees=True)
        hsv[..., 0] = (an / 2).astype(np.uint8)
        hsv[..., 1] = cv2.normalize(ma, None, 0, 255, cv2.NORM_MINMAX)
        hsv[..., 2] = 255
        if BGR:
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        else:
            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        return img

    def getArgParser(self):
        return None

    def processImageCollection(self, model, args):
        frame, _ = model.get(0)
        print(frame.shape, type(frame))
        frame = cv2.resize(frame, (3*frame.shape[1]//4, 3*frame.shape[0]//4))

        # Uncomment the line below to select a different bounding box
        frame_ = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # CAUTIOUS: Now the image browser supports multithreading. This makes the following line fail because opencv only allow window related functions to run on the main thread (on macos).
        # Thus you need to use a new process to run window related functions!
        # # bbox = cv2.selectROI(frame_, False)

        queue = Queue()
        p = Process(target=selectROI, args=(queue, frame_, False))
        p.start()
        p.join()
        bbox = queue.get(True)
        print(bbox)

        # Initialize tracker with first frame and bounding box
        ok = self.tracker.init(frame, bbox)
        bbox1 = bbox
        x0,y0,w,h = bbox
        pts_dst = np.array([[x0,y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])
        img_dst = frame
        prev = frame
        count = 0

        try:
            idx = 1
            while True:
                print('processing', idx)
                if idx >= model.length(): break

                # Read a new frame
                frame, _ = model.get(idx)
                frame = cv2.resize(frame, (3*frame.shape[1]//4, 3*frame.shape[0]//4))
    
                # Start timer
                timer = cv2.getTickCount()
        
                # Update tracker
                ok, bbox = self.tracker.update(frame)
                x0,y0,w,h = bbox
                pts_src = np.array([[x0,y0], [x0+w, y0], [x0+w, y0+h], [x0, y0+h]])
                img_src = frame
        
                #####################################
                # Calculate Affine transformation
            #     ha, status = cv2.estimateAffine2D(pts_src, pts_dst)
            #     frame = cv2.warpAffine(img_src, ha, (img_dst.shape[1],img_dst.shape[0]), borderMode=cv2.BORDER_REPLICATE)
                ha, status = cv2.findHomography(pts_src, pts_dst)
                frame = cv2.warpPerspective(img_src, ha, (img_dst.shape[1],img_dst.shape[0]))
                bbox = bbox1
                #####################################

        
                ################
                curr = frame
                #flow = test_per_pair(prev, curr)
                flow = cv2.calcOpticalFlowFarneback(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY), None, 0.5, 3, 15, 3, 5, 1.2, 0)
            #     dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
            #     flow = dis.calc(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY), None)
                prev = curr
                flowviz = self.flow2img(flow, BGR=True)
                ################
        
        
        
                # Calculate Frames per second (FPS)
                fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

                # Draw bounding box
                if ok:
                    # Tracking success
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            

                else :
                    # Tracking failure
                    cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)

            #     # Display tracker type on frame
            #     cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

            #     # Display FPS on frame
            #     cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);
                # Display result
                # cv2.imshow("Tracking", np.concatenate((frame, flowviz), axis=1)) #TODO
                #cv2.imwrite(os.path.join('dst',"%06d.png"%(count)), frame)

                frame_with_viz = np.concatenate((frame, flowviz), axis=1)
                frame_with_viz = cv2.resize(frame_with_viz, (3*frame_with_viz.shape[1]//4, 3*frame_with_viz.shape[0]//4))
                yield frame_with_viz, model.getImgName(idx)
                count += 1
                del frame

                idx += 1

        except:
            print('An error occurd in the tracker. May caused by missing the tracking object.')
            cv2.destroyAllWindows()
            return
        finally:
            cv2.destroyAllWindows()