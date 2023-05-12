from __future__ import division
from .jsondata import load_json

def calculate_acc(i1,i2,i3,i4,t):
    i1=float(i1)
    i2=float(i2)
    i3=float(i3)
    i4=float(i4)
    t=str(t)
    data=load_json()
    n1=int(data.get(t)[0])
    n2=int(data.get(t)[1])
    n3=int(data.get(t)[2])
    n4=int(data.get(t)[3])
    acc1=i1
    acc2=(i2*(n2+n1)-i1*n1)/n2
    acc3=(i3*(n3+n2+n1)-i2*(n2+n1))/n3
    acc4=(i4*(n4+n3+n2+n1)-i3*(n3+n2+n1))/n4
    return acc1,acc2,acc3,acc4