from django.contrib.gis.geos import Point, Polygon
pnt = Point(1, 1)
poly = Polygon( ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)) )
<trkpt lat="36.936607018" lon="-122.091610313"></trkpt>
    <trkpt lat="36.958683905" lon="-122.162639595"></trkpt>
    <trkpt lat="36.987815521" lon="-122.21506135"></trkpt>
    <trkpt lat="36.985890676" lon="-122.407740579"></trkpt>
    <trkpt lat="36.938457841" lon="-122.407684788"></trkpt>
    <trkpt lat="36.547896033" lon="-122.403661688"></trkpt>
    <trkpt lat="36.54776547" lon="-121.992926099"></trkpt>
    <trkpt lat="36.593976161" lon="-121.989732818"></trkpt>
    <trkpt lat="36.651878564" lon="-121.95285214"></trkpt>
    <trkpt lat="36.661324564" lon="-121.909793526"></trkpt>
    <trkpt lat="36.626844509" lon="-121.880774172"></trkpt>
    <trkpt lat="36.700304474" lon="-121.835279292"></trkpt>
    <trkpt lat="36.761488333" lon="-121.823453925"></trkpt>
    <trkpt lat="36.803637867" lon="-121.812197052"></trkpt>
    <trkpt lat="36.876714034" lon="-121.853754579"></trkpt>
    <trkpt lat="36.940579814" lon="-121.895316436"></trkpt>
    <trkpt lat="36.961193612" lon="-121.929400728"></trkpt>
    <trkpt lat="36.940762557" lon="-121.971105151"></trkpt>
    <trkpt lat="36.948092066" lon="-122.002927721"></trkpt>
    <trkpt lat="36.936402112" lon="-122.028084038"></trkpt>
    <trkpt lat="36.936607018" lon="-122.091610313"></trkpt>



poly.contains(pnt)
