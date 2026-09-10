import cv2 
img = cv2.imread("images1.jpg", 1)


img = cv2.line(img, (0,0), (255,255), (0,0,255), 5)

img = cv2.rectangle(img, (245,0),(300,345),(0,0,255), 5)
img = cv2.circle(img, (250,330), 60, (255,0,0), 5)
cv2.imshow("image", img)

cv2.waitKey(0)

cv2.destroyAllWindows()