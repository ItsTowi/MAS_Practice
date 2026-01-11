 شامل
</think>

{
  "timestamp": "2024-05-20T12:00:00Z",
  "rovers": [
    {
      "id": "rover_0",
      "location": "unspecified_start",
      "battery_level": 20.0,
      "status": "planning"
    }
  ],
  "drones": [
    {
      "id": "drone_0",
      "flight_status": "active",
      "surveilled_area": [
        "N1"
      ]
    },
    {
      "id": "drone_1",
      "flight_status": "active",
      "surveilled_area": [
        "N2"
      ]
    },
    {
      "id": "drone_2",
      "flight_status": "active",
      "surveilled_area": [
        "N25"
      ]
    },
    {
      "id": "drone_3",
      "flight_status": "active",
      "surveilled_area": [
        "N75"
      ]
    },
    {
      "id": "drone_4",
      "flight_status": "active",
      "surveilled_area": [
        "N53"
      ]
    }
  ],
  "hazards": [
    {
      "type": "orbit_congestion",
      "affected_nodes": [
        "satellite_0",
        "satellite_1"
      ],
      "severity": "medium"
    },
    {
      "type": "communication_window_mismatch",
      "affected_nodes": [
        "satellite_1",
        "satellite_3"
      ],
      "severity": "high"
    },
    {
      "type": "bottleneck",
      "affected_nodes": [
        "satellite_2"
      ],
      "severity": "critical"
    }
  ],
  "global_weather_status": "unknown"
}