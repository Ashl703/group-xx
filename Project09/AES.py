import numpy as np
import functools
import operator
import random
import time
#列混淆常数矩阵
MIX_C  = [[0x2, 0x3, 0x1, 0x1], [0x1, 0x2, 0x3, 0x1], [0x1, 0x1, 0x2, 0x3], [0x3, 0x1, 0x1, 0x2]]
#轮密钥生成涉及的常数矩阵
RCon   = [[0x01,0x00,0x00,0x00], 
       [0x02,0x00,0x00,0x00], 
       [0x04,0x00,0x00,0x00],
       [0x08,0x00,0x00,0x00], 
       [0x10,0x00,0x00,0x00], 
       [0x20,0x00,0x00,0x00], 
       [0x40,0x00,0x00,0x00], 
       [0x80,0x00,0x00,0x00], 
       [0x1B,0x00,0x00,0x00], 
       [0x36,0x00,0x00,0x00]
       ]
#S盒
S_BOX = [[0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76],
      [0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0],
      [0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15],
      [0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75],
      [0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84],
      [0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF],
      [0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8],
      [0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2],
      [0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73],
      [0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB],
      [0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79],
      [0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08],
      [0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A],
      [0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E],
      [0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF],
      [0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16]]

def SubBytes(state):
    state=state.reshape(16)
    for i in range(16):
        a=(state[i]>>4)&0b1111
        b=state[i]&0b1111
        state[i]=S_BOX[a][b]
    return state.reshape(4,4)

def ShiftRows(state):
    s=[state[0,:],np.roll(state[1,:],-1 ),np.roll(state[2,:],-2 ),np.roll(state[3,:],-3 )]
    s=np.vstack(s)
    return s
def bit_split(num):
    '''将num分成形如(0b1+0b10+0b100+...),返回一个列表，被gmul调用'''
    li=[]
    arg=[int(i) for i in format(num,'b')][::-1]
    if arg[0]:
        li.append(1)
    base=1
    for offset in arg[1:]:
        base=base<<1
        if offset:
            li.append(base)
    return li
def _gmul(a,b):
    '''被gmul调用(a为2的n次方)'''
    while a>>1:
        a=a>>1
        x=(b&0b1111111)<<1
        y=(b>>7)*0b11011
        b=x^y
    return b
def gmul(a,b):
    '''在G(2^8)上的乘法a*b'''
    a_li=bit_split(a)
    func=functools.partial(_gmul,b=b)
    return functools.reduce(operator.xor,list(map(func,a_li)))
def multi(cons,state):
    '''const每一行 * state 返回一行数据'''
    li=[]
    for _ in range(4):
        li.append(functools.reduce(operator.xor,list(map(gmul,cons,state[:,_]))))
    return li
def MixColumns(state):
    '''
    域上乘法，调用gmul()
    '''
    li=[]
    const_M=MIX_C #常数矩阵的选择
    const_M=np.array(const_M) #转化为np数组
    for _ in range(4):
        li.append(multi(const_M[_,:],state))
    return np.array(li)
def AddroundKey(state,key):
    s=[]
    for i in range(4):
        s.append(list(map(lambda x,y : x^y,state[:,i],key[:,i])))
    return np.array(s).transpose() #需要进行转置
    

#密钥扩展
def SubWord(byte):#字节替换
    s=[]
    for i in byte:
        a=i>>4#右移四位获得8位二进制串的前4位，通过这个索引S盒的行
        b=i&0b1111#8位bit串和4位bit做运算，会自动匹配后四位，通过这个索引S盒的列
        s.append(S_BOX[a][b])
    return s

def ExpandKey(key):
    key=key.reshape(16)#将4*4的key转化成一维数组操作
    key=list(key)
    w=[]
    i=0
    while i<4:#生成第一轮需要的4个字
        a=[key[4*i],key[4*i+1],key[4*i+2],key[4*i+3]]
        w.append(a)
        i+=1
    while i<44:#AES-128共需要44个字
        x=w[i-1][:]#将原来的数据复制过来，但是在后续过程中改动却不影响w中原来的结果
        if i%4==0:#i%4==0是对每一次轮密钥的第一列进行操作
            x.append(x.pop(0))#循环移位
            x=SubWord(x)#字节替换
            re = list(map(lambda x,y : x^y, x,RCon[i//4 -1]))#lambda表达式，结合map,list函数，将两个列表中对应元素异或后链接成列表
            x=list(re)
        re = list(map(lambda x,y : x^y,w[i-4],x))
        w.append(list(re))
        i=i+1
    w=np.array(w)
    return w.reshape(11,4,4)#11轮密钥，用11*4*4的矩阵表示，方便加密时索引

def encrypt(state,key):
    w=ExpandKey(key)
    state= AddroundKey(state,w[0][:][:])
    for i in range(1,9):#前9轮
        state=SubBytes(state)
        #print("{}sub{}".format(i,state))
        state=ShiftRows(state)
        #print("{}shift{}".format(i,state))
        state=MixColumns(state)
        #print("{}mix{}".format(i,state))
        state= AddroundKey(state,w[i][:][:])
        #print(state)  
    #第10轮
    state=SubBytes(state)
    state=ShiftRows(state)
    state= AddroundKey(state,w[10][:][:])
    print(state)
    return state

def differ(a,b):
    differ=[]
    for i in range(4):
        for j in range(4):
            differ.append(bin(a[i][j]^b[i][j])[2:].zfill(8))
    counter=0
    for i in range(16):
        for j in range(8):
            if differ[i][j]=='1':counter+=1
    print(differ)
    print(counter)

    
#10000000 00000000
state=np.array([[0x80,0x00,0x00,0x00],[0x00,0x00,0x00,0x00],[0x00,0x00,0x00,0x00],[0x00,0x00,0x00,0x00]])
key=np.array([[0x11,0x12,0x13,0x14],[0x15,0x16,0x17,0x18],[0x19,0x20,0x21,0x22],[0x23,0x24,0x25,0x26]])
a=encrypt(state,key)
