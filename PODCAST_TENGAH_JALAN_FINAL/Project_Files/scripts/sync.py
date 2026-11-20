import numpy as np, wave, sys
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32); return a
def env(a, sr=16000, hop=160):
    n=len(a)//hop; e=np.sqrt((a[:n*hop].reshape(n,hop)**2).mean(1)+1e-6); e=np.log(e); e-=np.convolve(e,np.ones(100)/100,'same'); return e
A=env(load(sys.argv[1])); B=env(load(sys.argv[2]))
def xc(A,B):
    n=1<<int(np.ceil(np.log2(len(A)+len(B))))
    c=np.fft.irfft(np.fft.rfft(A,n)*np.conj(np.fft.rfft(B,n)),n)
    return c
c=xc(A,B); lag=np.argmax(c); 
if lag>len(c)//2: lag-=len(c)
print("offset of B within A (s):", lag/100, "peak", c.max()/np.sqrt((A**2).sum()*(B**2).sum()))
# local check: windows of B
for st in range(0,len(B)-6000,6000):
    seg=B[st:st+3000]; cc=xc(A,seg); l=np.argmax(cc); 
    if l>len(cc)//2: l-=len(cc)
    print(f"B {st/100:6.0f}s -> A {l/100:8.2f}s  diff {(l-st)/100:8.2f}  score {cc.max()/np.sqrt((seg**2).sum()*(A[max(l,0):max(l,0)+3000]**2).sum()+1e-9):.3f}")
print("---")
for off in (20.42,1032.08):
    o=int(round(off*100)); row=[]
    for st in range(0,len(B)-3000,3000):
        a=A[st+o:st+o+3000]; b=B[st:st+3000]
        if len(a)<3000: row.append(' -- '); continue
        row.append(f"{(a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()):.2f}")
    print(off, ' '.join(row))
