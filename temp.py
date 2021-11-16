import numpy as np
import winsound
import cv2
import time
import Person1


duration = 1000  # milliseconds
freq = 440 #Hz
cnt_in   = 0
cnt_out = 0
count_in = 0

count_out = 0
state =0


cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output1.mkv',fourcc, 20.0, (640,480))




for i in range(19):
    print (i, cap.get(i))

w = cap.get(3)
h = cap.get(4)
frameArea = h*w
areaTH = frameArea/300
print ('Area Threshold', areaTH)

#Lines coordinate for counting
line_in = int(1*(h/5))
line_out   = int(4*(h/5))

in_limit =   int(.5*(h/5))
out_limit = int(4.5*(h/5))

print ("Red line y:",str(line_out))
print ("Blue line y:", str(line_in))
line_down_color = (255,0,0)
line_up_color = (0,0,255)
pt1 =  [0, line_out];
pt2 =  [w, line_out];
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_in];
pt4 =  [w, line_in];
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, in_limit];
pt6 =  [w, in_limit];
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, out_limit];
pt8 =  [w, out_limit];
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Background Substractor
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)

#Structuring elements for morphographic filters
kernelOp = np.ones((3,3),np.uint8)
kernelOp2 = np.ones((5,5),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Variables
font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
rect_co = []
max_p_age = 1
pid = 1
val = []

while(cap.isOpened()):

    
    ret, frame = cap.read()


    
    
    #Apply background subtraction
    fgmask = fgbg.apply(frame)
    fgmask2 = fgbg.apply(frame)

    #Binarization to eliminate shadows
    try:
        ret,imBin= cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
        ret,imBin2 = cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
        #Opening (erode->dilate) to remove noise.
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, kernelOp)
        #Closing (dilate -> erode) to join white regions.
        mask =  cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernelCl)
    except:
        print('EOF')
        print ('UP:',cnt_in+count_in)
        print ('DOWN:',cnt_out+count_out)
        break

    contours0, hierarchy = cv2.findContours(mask2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        rect = cv2.boundingRect(cnt)
       
        area = cv2.contourArea(cnt)
        if area > areaTH:
           
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt)
            

            new = True
            if cy in range(in_limit,out_limit):
                for i in persons:
                    if abs(cx-i.getX()) <= w and abs(cy-i.getY()) <= h:
                       
                        new = False
                        i.updateCoords(cx,cy)   #update coordinates in the object and resets age
                        if i.going_IN(line_out,line_in) == True:
                            if w > 100:
                                count_in = w/60
                                
                                print ()
                            else:    
                                cnt_in += 1;
                            print ("ID:",i.getId(),'crossed going in at',time.strftime("%c"))
                        elif i.going_OUT(line_out,line_in) == True:
                            if w > 100:
                                count_out = w/60
                               
                            else:
                                cnt_out += 1;
                            print ("ID:",i.getId(),'crossed going out at',time.strftime("%c"))
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'out' and i.getY() > out_limit:
                            i.setDone()
                        elif i.getDir() == 'in' and i.getY() < in_limit:
                            i.setDone()
                    if i.timedOut():
                        #get out of the people list
                        index = persons.index(i)
                        persons.pop(index)
                        del i     #free the memory of i
                if new == True:
                    p = Person1.MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    pid += 1    
        
            cv2.circle(frame,(cx,cy), 5, (0,0,255), -1)
            img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            

    for i in persons:

        cv2.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv2.LINE_AA)

    str_up = 'IN: '+ str(int(cnt_in+count_in))
    str_down = 'OUT: '+ str(int(cnt_out+count_out))
    
    frame = cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
    frame = cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
    
    
    
    frame = cv2.polylines(frame,[pts_L3],True,(255,255,255),thickness=1)
    frame = cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv2.LINE_AA)
    cv2.putText(frame,'',(300,200),font,1,(255,0,0),2)
    if (cnt_in+count_in-cnt_out -count_out)>4:# number of people in the elevator
        winsound.Beep(freq, duration)
    
    out.write(frame)
    cv2.imshow('Frame',frame)
      
    
    #Press ESC to exit
    k = cv2.waitKey(30) & 0xff
    if k == 27:#escape  key
        break

cap.release()
cv2.destroyAllWindows()