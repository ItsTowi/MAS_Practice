# Satellite Integration Report

## Orbit
- **satellite_0**: orbit_4 (3h communication window)
- **satellite_1**: orbit_4 (1h communication window)
- **satellite_2**: orbit_3 (7h communication window)
- **satellite_3**: orbit_5 (1h communication window)
- **satellite_4**: orbit_2 (9h communication window)

## Imaging Plan
- **High-priority target**: satellite_4 (orbit_2, 9h window)
- **Medium-priority target**: satellite_2 (orbit_3, 7h window)
- **Low-priority target**: satellite_0 (orbit_4, 3h window)
- **Backup satellites**: satellite_1 and satellite_3 (1h windows)

## Communications
- **Primary path**: satellite_4 ↔ satellite_2 (confirmed successful communication)
- **Critical check**: satellite_4 (9h window) and satellite_2 (7h window) maintain reliable communication for high-priority targets
- **Potential bottleneck**: satellite_2's 7h window may limit data throughput for medium-priority targets compared to satellite_4

## Environment / Risks
1. **Orbit congestion**: Two satellites (satellite_0 and satellite_1) share orbit_4, risking imaging interference
2. **Communication window mismatch**: satellite_1 and satellite_3 have 1h windows, increasing risk of data loss during critical operations
3. **Critical path vulnerability**: satellite_2 (7h window) may become a bottleneck for high-priority data when satellite_4 (9h window) is fully utilized
4. **Recommendation**: Retask satellite_1 from orbit_4 to orbit_3 to share load with satellite_2 and improve medium-priority coverage. Retask satellite_3 from orbit_5 to orbit_2 to enhance high-priority communication resilience.