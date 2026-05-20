import enum


class CameraStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class AlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"   # fixed typo (Crittial → CRITICAL)


class AlertStatus(enum.Enum):
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class DetectionType(enum.Enum):
    PERSON = "person"
    CAR = "car"
    BICYCLE = "bicycle"
    BACKPACK = "backpack"
    MOTORBIKE = "motorbike"
    UNKNOWN = "unknown"