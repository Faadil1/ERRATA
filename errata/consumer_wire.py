"""Independent minimal protobuf wire consumer.
Does not import ERRATA's protobuf descriptor or serializer.
Understands only the field numbers used in the prototype GTFS-RT subset.
"""
from __future__ import annotations


def read_varint(buf, i):
    shift=0; out=0
    while True:
        b=buf[i]; i+=1; out |= (b & 0x7f) << shift
        if not b & 0x80: return out,i
        shift += 7
        if shift>70: raise ValueError('varint too long')


def fields(buf):
    i=0; out=[]
    while i<len(buf):
        key,i=read_varint(buf,i); num=key>>3; wire=key&7
        if wire==0:
            val,i=read_varint(buf,i)
        elif wire==2:
            n,i=read_varint(buf,i); val=buf[i:i+n]; i+=n
        else:
            raise ValueError(f'unsupported wire type {wire}')
        out.append((num,wire,val))
    return out


def first(fs,num,default=None):
    for f in fs:
        if f[0]==num:return f
    return default


def parse_feed(buf):
    top=fields(buf)
    header_f=first(top,1)
    if not header_f: raise ValueError('missing header')
    header=fields(header_f[2]); ver=first(header,1)
    version=ver[2].decode() if ver else None
    entities=[]
    for num,wire,val in top:
        if num!=2: continue
        ef=fields(val); eid=first(ef,1); tuf=first(ef,3)
        if not eid or not tuf: continue
        tf=fields(tuf[2]); tripf=first(tf,1)
        trip_fields=fields(tripf[2]); trip_id=first(trip_fields,1)[2].decode(); route_id=first(trip_fields,5)[2].decode(); direction=first(trip_fields,6)[2] if first(trip_fields,6) else None
        stops=[]
        for n,w,v in tf:
            if n!=2: continue
            sf=fields(v); seq=first(sf,1)[2] if first(sf,1) else None; stop=first(sf,4)[2].decode() if first(sf,4) else None; rel=first(sf,5)[2] if first(sf,5) else 0
            stops.append({'stop_sequence':seq,'stop_id':stop,'schedule_relationship':rel})
        entities.append({'id':eid[2].decode(),'trip_id':trip_id,'route_id':route_id,'direction_id':direction,'stops':stops})
    return {'version':version,'entities':entities}
