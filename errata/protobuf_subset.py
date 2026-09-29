"""Dynamic protobuf descriptor for the GTFS-RT subset used by ERRATA.

Field numbers/types mirror the canonical MobilityData gtfs-realtime.proto.
This intentionally implements only FeedMessage -> FeedEntity -> TripUpdate -> TripDescriptor/StopTimeUpdate.
"""
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


def _field(msg, name, number, label, typ, type_name=None, default=None):
    f=msg.field.add(); f.name=name; f.number=number; f.label=label; f.type=typ
    if type_name: f.type_name=type_name
    if default is not None: f.default_value=str(default)


def build_classes():
    fd=descriptor_pb2.FileDescriptorProto()
    fd.name='errata_gtfs_realtime_subset.proto'; fd.package='transit_realtime'; fd.syntax='proto2'
    # FeedHeader
    h=fd.message_type.add(); h.name='FeedHeader'
    _field(h,'gtfs_realtime_version',1,2,9)
    _field(h,'timestamp',3,1,4)
    # TripDescriptor
    td=fd.message_type.add(); td.name='TripDescriptor'
    _field(td,'trip_id',1,1,9); _field(td,'start_time',2,1,9); _field(td,'start_date',3,1,9)
    _field(td,'route_id',5,1,9); _field(td,'direction_id',6,1,13)
    # StopTimeUpdate nested in TripUpdate
    tu=fd.message_type.add(); tu.name='TripUpdate'
    stu=tu.nested_type.add(); stu.name='StopTimeUpdate'
    enum=stu.enum_type.add(); enum.name='ScheduleRelationship'
    for name,num in [('SCHEDULED',0),('SKIPPED',1),('NO_DATA',2),('UNSCHEDULED',3)]:
        v=enum.value.add(); v.name=name; v.number=num
    _field(stu,'stop_sequence',1,1,13); _field(stu,'stop_id',4,1,9)
    _field(stu,'schedule_relationship',5,1,14,'.transit_realtime.TripUpdate.StopTimeUpdate.ScheduleRelationship','SCHEDULED')
    _field(tu,'trip',1,2,11,'.transit_realtime.TripDescriptor')
    _field(tu,'stop_time_update',2,3,11,'.transit_realtime.TripUpdate.StopTimeUpdate')
    _field(tu,'timestamp',4,1,4)
    # FeedEntity
    fe=fd.message_type.add(); fe.name='FeedEntity'
    _field(fe,'id',1,2,9); _field(fe,'is_deleted',2,1,8); _field(fe,'trip_update',3,1,11,'.transit_realtime.TripUpdate')
    # FeedMessage
    fm=fd.message_type.add(); fm.name='FeedMessage'
    _field(fm,'header',1,2,11,'.transit_realtime.FeedHeader'); _field(fm,'entity',2,3,11,'.transit_realtime.FeedEntity')
    pool=descriptor_pool.DescriptorPool(); pool.Add(fd)
    classes={}
    for n in ['FeedMessage','FeedHeader','FeedEntity','TripUpdate','TripDescriptor']:
        classes[n]=message_factory.GetMessageClass(pool.FindMessageTypeByName('transit_realtime.'+n))
    return classes

CLASSES=build_classes()
FeedMessage=CLASSES['FeedMessage']
