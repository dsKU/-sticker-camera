import cv2
import dlib
import numpy as np
import math
    
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')    
class Snow():
    def getPoints(self,gray, rect):
        points = []
        shape = predictor(gray, rect)
        for i in range(68):
            part = shape.part(i)
            points.append((part.x, part.y))
        return points
    def extract_index_nparray(self, nparray):
        index = None
        for num in nparray[0]:
            index = num
            break
        return index
    
    def getTriangles(self, landmarks, convexhull, point):
        rect = cv2.boundingRect(convexhull)
        subdiv = cv2.Subdiv2D(rect)
        subdiv.insert(landmarks)
        triangleList = subdiv.getTriangleList()
        triangleList = np.array(triangleList, dtype=np.int32)
        triangles = []
        
        for t in triangleList:        
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])
            index_pt1 = np.where((point == pt1).all(axis=1))
            index_pt1 = self.extract_index_nparray(index_pt1)
        
            index_pt2 = np.where((point == pt2).all(axis=1))
            index_pt2 = self.extract_index_nparray(index_pt2)
        
            index_pt3 = np.where((point == pt3).all(axis=1))
            index_pt3 = self.extract_index_nparray(index_pt3)
        
            if index_pt1 is not None and index_pt2 is not None and index_pt3 is not None:
                triangle = [index_pt1, index_pt2, index_pt3]
                triangles.append(triangle)

        return triangles
    
    def warpTriangle(self, img1, img2, pts1, pts2):
        x1,y1,w1,h1 = cv2.boundingRect(np.float32([pts1]))
        x2,y2,w2,h2 = cv2.boundingRect(np.float32([pts2]))
        
        roi1 = img1[y1:y1+h1, x1:x1+w1]
        roi2 = img2[y2:y2+h2, x2:x2+w2]
        
        offset1 = np.zeros((3,2), dtype=np.float32)
        offset2 = np.zeros((3,2), dtype=np.float32)
        for i in range(3): 
            offset1[i][0], offset1[i][1] = pts1[i][0]-x1, pts1[i][1]-y1
            offset2[i][0], offset2[i][1] = pts2[i][0]-x2, pts2[i][1]-y2
        
        mtrx = cv2.getAffineTransform(offset1, offset2)
        warped = cv2.warpAffine( roi1, mtrx, (w2, h2), None, \
                            cv2.INTER_LINEAR, cv2.BORDER_REFLECT_101 )
        
        mask = np.zeros((h2, w2), dtype = np.uint8)
        cv2.fillConvexPoly(mask, np.int32(offset2), (255))
        
        warped_masked = cv2.bitwise_and(warped, warped, mask=mask)
        roi2_masked = cv2.bitwise_and(roi2, roi2, mask=cv2.bitwise_not(mask))
        roi2_masked = roi2_masked + warped_masked

        img2[y2:y2+h2, x2:x2+w2] = roi2_masked
        
    def Face_Swap(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rects = detector(gray)
            if len(rects) < 2:
                output = img
                #좌표 부족시 예외처리 할 것.
            else:
                img_draw = img.copy()
                # 각 이미지에서 얼굴 랜드마크 좌표 구하기--- ⑥ 
                landmarks1 = self.getPoints(gray, rects[0])  
                landmarks2 = self.getPoints(gray, rects[1])
        
                points1 = np.array(landmarks1,dtype=np.int32) 
                points2 = np.array(landmarks2,dtype=np.int32) 
                # 랜드마크 좌표로 볼록 선체 구하기 --- ⑦
                convexhull1 = cv2.convexHull(points1)
                convexhull2 = cv2.convexHull(points2)
            
                hullIndex = cv2.convexHull(np.array(landmarks2), returnPoints = False)
                hullIndex2 = cv2.convexHull(np.array(landmarks1), returnPoints = False)
                hull1 = [landmarks1[int(idx)] for idx in hullIndex]
                hull2 = [landmarks2[int(idx)] for idx in hullIndex]
                
                # 볼록 선체 안 들로네 삼각형 좌표 구하기 ---⑧ 
                triangles = self.getTriangles(landmarks1, convexhull1, points1)
                triangles2 = self.getTriangles(landmarks2, convexhull2, points2)
                # 각 삼각형 좌표로 삼각형 어핀 변환 ---⑨    
                for i in range(0, len(triangles)):
                    t1 = [landmarks1[triangles[i][j]] for j in range(3)]
                    t2 = [landmarks2[triangles[i][j]] for j in range(3)]
                    self.warpTriangle(img, img_draw, t1, t2)
                
                for i in range(0, len(triangles2)):
                    t1 = [landmarks2[triangles2[i][j]] for j in range(3)]
                    t2 = [landmarks1[triangles2[i][j]] for j in range(3)]
                    self.warpTriangle(img, img_draw, t1, t2)
                
                # 볼록선체를 마스크로 써서 얼굴 합성 ---⑩
                mask = np.zeros(img.shape, dtype = img.dtype)
                mask2= np.zeros(img.shape, dtype = img.dtype)
                cv2.fillConvexPoly(mask, np.int32(hull2), (255, 255, 255))
                cv2.fillConvexPoly(mask2, np.int32(hull1), (255, 255, 255))
            
            
                r = cv2.boundingRect(np.float32([hull2]))
                r2 = cv2.boundingRect(np.float32([hull1]))
                center = ((r[0]+int(r[2]/2), r[1]+int(r[3]/2)))
                center2 = ((r2[0]+int(r2[2]/2), r2[1]+int(r2[3]/2)))
                output = cv2.seamlessClone(np.uint8(img_draw), img, mask2, center2, \
                                        cv2.NORMAL_CLONE)
                output = cv2.seamlessClone(np.uint8(img_draw), output, mask, center, \
                                        cv2.NORMAL_CLONE)
        except:
            output = img
           
        return output 

    def Rabbit_Ears(self, img):
        output = img
        try:
            img_leftear = cv2.imread('./sticker/rabbit_left_ear.png')
            img_rightear = cv2.imread('./sticker/rabbit_right_ear.png')
            img_leftear = cv2.resize(img_leftear, (71,136))
            img_rightear = cv2.resize(img_rightear, (71,136))

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 얼굴 영역 검출
            faces = detector(gray)
            for rect in faces:
                leftOffsetY = 40
                leftOffsetX = 0
                rightOffsetY = 40
                rightOffsetX = 0

                # 얼굴 랜드마크 검출
                shape = predictor(gray, rect)
                
                leftear_area = shape.part(18)
                rightear_area = shape.part(23)

                faceLen = shape.part(16).x - shape.part(0).x      
                leftRate = (shape.part(27).x - shape.part(0).x) / faceLen
                rightRate = (shape.part(16).x - shape.part(27).x) / faceLen
                
                pt1 = (0,  136)
                pt2 = (71, 136)
                pt3 = (0, 0)
                pt4 = (71, 0)
                p1 = np.float32([pt1, pt2, pt3, pt4])
                
                pt1 = (0,  136)
                pt2 = (int(71*leftRate), 136)
                pt3 = (0 ,0)
                pt4 = (int(71*leftRate),0)
                p2 = np.float32([pt1, pt2, pt3, pt4])

                M =cv2.getPerspectiveTransform(p1,p2)
                img_leftear_tmp = cv2.warpPerspective(img_leftear, M,  (int(71*leftRate), 136));

                
                leftear_gray = cv2.cvtColor(img_leftear_tmp, cv2.COLOR_BGR2GRAY) 
                ret, leftear_mask = cv2.threshold(leftear_gray,1,255,cv2.THRESH_BINARY)
                leftear_mask_inv = cv2.bitwise_not(leftear_mask)
                
                pt1 = (0,  136)
                pt2 = (int(71*rightRate), 136)
                pt3 = (0 ,0)
                pt4 = (int(71*rightRate),0)
                p2 = np.float32([pt1, pt2, pt3, pt4])
                
                M =cv2.getPerspectiveTransform(p1,p2)
                img_rightear_tmp = cv2.warpPerspective(img_rightear, M,  (int(71*rightRate), 136));
                #투영변환으로 토끼귀의 크기 조정하
                rightear_gray = cv2.cvtColor(img_rightear_tmp, cv2.COLOR_BGR2GRAY)
                ret, rightear_mask = cv2.threshold(rightear_gray,1,255,cv2.THRESH_BINARY)
                rightear_mask_inv = cv2.bitwise_not(rightear_mask)

                # 왼쪽 귀 비트마스킹
                leftroi = img[leftear_area.y - img_leftear.shape[0] - leftOffsetY : leftear_area.y - leftOffsetY, leftear_area.x - int(71*leftRate) - leftOffsetX : leftear_area.x - leftOffsetX]

                leftear_bg = cv2.bitwise_and(leftroi, leftroi, mask=leftear_mask_inv)
                leftear_fg = cv2.bitwise_and(img_leftear_tmp, img_leftear_tmp, mask=leftear_mask)
                dst = cv2.add(leftear_bg, leftear_fg)

                img[leftear_area.y - img_leftear.shape[0] - leftOffsetY : leftear_area.y - leftOffsetY, leftear_area.x - int(71*leftRate) - leftOffsetX : leftear_area.x - leftOffsetX] = dst
                #오른쪽귀
                rightroi = img[rightear_area.y - img_rightear.shape[0] - rightOffsetY : rightear_area.y - rightOffsetY, rightear_area.x + rightOffsetX : rightear_area.x + int(71*rightRate) + rightOffsetX]

                rightear_bg = cv2.bitwise_and(rightroi, rightroi, mask=rightear_mask_inv)
                rightear_fg = cv2.bitwise_and(img_rightear_tmp, img_rightear_tmp, mask=rightear_mask)
                dst = cv2.add(rightear_bg, rightear_fg)

                img[rightear_area.y - img_rightear.shape[0] - rightOffsetY : rightear_area.y - rightOffsetY, rightear_area.x + rightOffsetX : rightear_area.x + int(71*rightRate) + rightOffsetX] = dst
            #endfor
        except:
            img = output
        return img
    
    def SunGlass(self,img):
        output = img
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_sun_ori = cv2.imread('./sticker/sun3.png')
            # 얼굴 영역 검출
            faces = detector(gray)
            for rect in faces:
                    
                # 얼굴 랜드마크 검출
                shape = predictor(gray, rect)
                for n in range(0, 68):
                        x = shape.part(n).x
                        y = shape.part(n).y

                eye_center = shape.part(27)
                sun_len = shape.part(16).x - shape.part(0).x
                
                if sun_len % 2 != 0:
                    sun_len = sun_len+1
                sun_hei = int(sun_len * 0.7)
                if sun_hei % 2 != 0:
                    sun_hei = sun_hei+1
                    
                leftRate = (shape.part(27).x - shape.part(0).x) / sun_len
                rightRate = (shape.part(16).x - shape.part(27).x) / sun_len
                
                left_side = int(leftRate * sun_len)
                right_side = int(rightRate * sun_len)
                if left_side + right_side != sun_len:
                    sun_len = left_side + right_side        
                
                img_sun = cv2.resize(img_sun_ori, (sun_len,sun_hei))
                
                pt1 = (0, sun_hei)
                pt2 = (sun_len, sun_hei)
                pt3 = (0 ,0)
                pt4 = (sun_len,0)
                p1 = np.float32([pt1, pt2, pt3, pt4])

                pt1 = (0,  sun_hei - (sun_hei * (0.5 - leftRate) / 2))
                pt2 = (sun_len, sun_hei - (sun_hei * (0.5 - rightRate) / 2))
                pt3 = (0, (sun_hei * (0.5 - leftRate) / 2))
                pt4 = (sun_len, (sun_hei * (0.5 - rightRate) / 2))
                p2 = np.float32([pt1, pt2, pt3, pt4])


                M =cv2.getPerspectiveTransform(p1,p2)
                img_sun_tmp = cv2.warpPerspective(img_sun, M,  (sun_len,sun_hei));
                #투영변환을 통해 선글라스 변환
                
                sun_center = int((left_side + int(sun_len/2)) /2)
                sun_left = sun_center
                sun_right = img_sun_tmp.shape[1] - sun_center
                img_sun_gray = cv2.cvtColor(img_sun_tmp, cv2.COLOR_BGR2GRAY) 
                ret, sun_mask = cv2.threshold(img_sun_gray,1,255,cv2.THRESH_BINARY)
                sun_mask_inv = cv2.bitwise_not(sun_mask)
                    
                eyes_roi = img[eye_center.y - int(sun_hei/2)  : eye_center.y + int(sun_hei/2), eye_center.x - sun_center : eye_center.x + sun_right]
                
                sun_bg = cv2.bitwise_and(eyes_roi, eyes_roi, mask=sun_mask_inv)
                sun_fg = cv2.bitwise_and(img_sun_tmp, img_sun_tmp, mask=sun_mask)
                dst = cv2.add(sun_bg, sun_fg)
                img[eye_center.y - int(sun_hei/2)  : eye_center.y + int(sun_hei/2), eye_center.x - sun_center : eye_center.x + sun_right] = dst 
                #이미지 
        except:
            img = output
        return img



        
