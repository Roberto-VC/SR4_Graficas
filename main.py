import struct
from time import *
from random import *
import math
from vector import *

class Bitmap():
  def __init__(self, width, height):
    self._bcBitCount = 24
    self._headerbits = 14
    self._headerbitmap = 40
    self._bcWidth = width
    self._bcHeight = height
    self._color = (45, 0, 0)
    self._bfSize = self._bcWidth*3*self._bcHeight
    self._dotsx= []
    self._dotsy= []
    self.clear()


  def clear(self):
    self._fondo = [ [self._color]*self._bcWidth for i in range(self._bcHeight)]
    self._zbuffer = [ [-999999]*self._bcWidth for i in range(self._bcHeight)]
    

  def clearColor(self, r, g, b):
    self._color = (b,g,r)

  def Vertex(self, x, y):
    if isinstance(self._color, tuple):
      if x < 0 or y < 0 or x > self._bcWidth or y > self._bcHeight:
        raise ValueError('Coords out of range')
      if len(self._color) != 3:
        raise ValueError('Color must be a tuple of 3 elems')
      self._fondo[y-1][x-1] = (self._color[0], self._color[1], self._color[2])
      self._dotsx.append(x)
      self._dotsy.append(y)
  
    else:
      raise ValueError('Color must be a tuple of 3 elems')


  def getDotx(self):
      return self._dotsx

  def getDoty(self):
      return self._dotsy

  def Clear(self):
    self._dotsx.clear()
    self._dotsy.clear()
    
  def write(s, file):
    with open(file, 'wb') as f:
      f.write(struct.pack('<hlhhl', 
                   19778,
                   14+40+s._bcHeight*s._bcWidth*3, 
                   0,
                   0,
                   40+14)) # Writing BITMAPFILEHEADER
      f.write(struct.pack('<lllhhllllll', 
                   40, 
                   s._bcWidth, 
                   s._bcHeight, 
                   1, 
                   s._bcBitCount,
                   0,
                   s._bfSize,
                   0,
                   0,
                   0,
                   0)) # Writing BITMAPINFO
      for x in range(s._bcWidth):
        for y in range(s._bcHeight):
          f.write(struct.pack('<BBB', s._fondo[x][y][0], s._fondo[x][y][1], s._fondo[x][y][2]))


  def linea(self, A, B):
    
    x0 = round(A.x)
    x1 = round(B.x)
    y0 = round(A.y)
    y1 = round(B.y)
    
    dx = abs(x1-x0)
    dy = abs(y1-y0)
    
    inclinado = dy>dx
    if inclinado:
      x0, y0 = y0, x0
      x1, y1 = y1, x1
  
    if x0 > x1:
      x0,x1=x1,x0
      y0,y1=y1,y0

    dy = abs(y1 - y0)
    dx = abs(x1 - x0)
    
    offset = 0
    thres = dx
    y = y0

    for x in range(x0,x1+1):
      if inclinado:
        self.Vertex(y, x)
      else:
        self.Vertex(x, y)

        
      
      offset += dy*2
      if offset >= thres:
        y += 1 if y0<y1 else -1
        thres += dx *2


    
      
        
  

#(165, 380) (185, 360) (180, 330) (207, 345) (233, 330) (230, 360) (250, 380) (220, 385) (205, 410) (193, 383)

class Obj(object):
  def __init__(self, filename):
    with open(filename) as f:
      self.lines = f.read().splitlines()
      self.vertices = []
      self.faces = []

      for line in self.lines:
        prefix, value = line.split(" ",1)
        if prefix == "v":
          self.vertices.append((list(map(float,value.split(' ')))))
        if prefix == "f":
          self.faces.append([list(map(int,face.split("/"))) for face in value.split()])

def bounding_box(A,B,C):
  xs = [A.x, B.x, C.x]
  ys = [A.y, B.y, C.y]

  xs.sort()
  ys.sort()
  
  return xs[0], xs[-1], ys[0], ys[-1]

def cross(V1,V2):
  return (
      V1.y * V2.z - V1.z * V2.y,
      V1.z * V2.x - V1.x * V2.z,
      V1.x * V2.y - V1.y * V2.x
  )

def barycentric(A,B,C,P):
  cx, cy, cz = cross(
    V3(B.x-A.x, C.x-A.x, A.x-P.x),
    V3(B.y-A.y, C.y-A.y, A.y-P.y)
  )

  u = cx/cz
  v = cy/cz
  w = 1-u-v

  return(w,v,u)

def transform_vertex(vertex,scale,translate):
  return[
       (vertex[0]*scale[0])+translate[0],
       (vertex[1]*scale[1])+translate[1],
       (vertex[2]*scale[2])+translate[2]
  ]


print()
def main():

  scale_factor = (100,100,100)
  transform_factor = (400,400,10)
  

  
  side = 900
  zubat =  Obj("zubat.obj")
  b = Bitmap(side,side) 
  b.clearColor(200,0,225)


  


  def triangle(A,B,C):

    L=V3(0,0,1)
    N = (B-A)*(C-A)

    i= N.normalize() @ L.normalize()

    if i <0:
      return

    grey = (round(255 * i), round(255 * i), round(255 * i))
    b._color = grey
    p,q,r,s = bounding_box(A,B,C)
    d = 0
    for x in range(round(p), round(q)+1):
      for y in range(round(r), round(s)+1):
        try:
          w,v,u = barycentric(A,B,C, V3(x,y))
        except:
          continue
        if (w<0 or v<0 or u<0):
          continue
        z = A.z*w+B.z*v+C.z*u
        if (b._zbuffer[x][y] < z):
           b._zbuffer[x][y] = z
           b.Vertex(x,y)

        
  print("Bienvenido al renderizador. Que quiere hacer?\n")
  print("1. Renderizar modelo.\n2.Activar/Desactivar z-buffer") 
  int(input())    

  d = 0
  for face in zubat.faces:
    if len(face) == 4:
      f1 = face[0][0]-1
      f2 = face[1][0]-1
      f3 = face[2][0]-1
      f4 = face[3][0]-1

      
      v1 = transform_vertex(zubat.vertices[f1], scale_factor, transform_factor)
      v2 = transform_vertex(zubat.vertices[f2], scale_factor, transform_factor)
      v3 = transform_vertex(zubat.vertices[f3], scale_factor, transform_factor)
      v4 = transform_vertex(zubat.vertices[f4], scale_factor, transform_factor)

      triangle(V3(v1[0],v1[1],v1[2]), V3(v2[0],v2[1],v2[2]), V3(v3[0],v3[1],v3[2]))
      triangle(V3(v1[0],v1[1],v1[2]), V3(v4[0],v4[1],v4[2]), V3(v3[0],v3[1],v3[2]))
    else:
      
      f1 = face[0][0]-1
      f2 = face[1][0]-1
      f3 = face[2][0]-1

      v1 = transform_vertex(zubat.vertices[f1], scale_factor, transform_factor)
      v2 = transform_vertex(zubat.vertices[f2], scale_factor, transform_factor)
      v3 = transform_vertex(zubat.vertices[f3], scale_factor, transform_factor)

      triangle(V3(v3[0],v3[1],v3[2]), V3(v1[0],v1[1],v1[2]), V3(v2[0],v2[1],v2[2]))

  print(":)")
  b.write("resultado.bmp")

   

if __name__ == '__main__':
  main()