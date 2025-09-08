import json
import math
import uuid
import boto3
import os
from decimal import Decimal
from datetime import datetime
#import statements


# DynamoDB resource client setup - connects Lambda function to Dynamodb
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# Initilizes a connection to Amazon SNS
sns = boto3.client('sns', region_name='us-east-1')

# Searches for a DynamoDB table name in env vars, and if not provided, uses default GeofenceEvents
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "GeofenceEvents")

# Connect to DynamoDB table so we can read/write data to it
table = dynamodb.Table(TABLE_NAME)

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:288322689819:GeofenceAlerts")


# Configuration of Geofence
# -------------------------

# Geofence anchor point - lat/long marks the center of safe zone, set to default New York City
GEOFENCE_CENTER = (40.7128, -74.0060)  # (latitude, longitude)

# Defines how far geofence extends outward from center point
# Any device within 50 meters of center will be considered "inside" the geofence
GEOFENCE_RADIUS = 50


# Haversine Formula
# ----------------------------------

# Calculates distance in meters between two lat/long points
def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371000  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# Main Lambda Handler
# --------------------
def lambda_handler(event, context):
    try:
        # Store lat/long and device ID from IoT message (event)
        lat = event.get('lat')
        lon = event.get('lon')

        # ID could be device_id or deviceId, if neither exists, we label it unknown
        device_id = event.get("device_id", event.get("deviceId", "unknown"))

        # if GPS coordinates aren't included in message, return error instead of running the geofence logic
        if lat is None or lon is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing lat/lon'})
            }


        # Calculate distance from geofence center
        distance = haversine_distance(lat, lon, GEOFENCE_CENTER[0], GEOFENCE_CENTER[1])

        # Check if inside/outside the geofence
        inside = distance <= GEOFENCE_RADIUS

        # Build the result record to log in DynamoDB
        result = {
            'eventId': str(uuid.uuid4()),  # Unique event ID
            'timestamp': datetime.utcnow().isoformat(),  # Time of event
            'deviceId': device_id,  
            'lat': Decimal(str(lat)),  # Lat as Decimal for DynamoDB
            'lon': Decimal(str(lon)),  # Long as Decimal for DynamoDB
            'insideGeofence': Decimal('1') if inside else Decimal('0'),  # Store as 1/0
            'distanceFromCenterMeters': Decimal(str(round(distance, 2)))  # Rounded distance
        }
        print("Geofence Check:", result)

    
        # Log the event to DynamoDB
        # ---------------------------------
        try:
            table.put_item(Item=result)
        except Exception as db_err:
            print(f"DynamoDB Error: {db_err}")

    
        # Send an SNS alert email
        # -----------------------
        try:
            message = (
                f"Geofence Alert for Device: {device_id}\n"
                f"Location: ({lat}, {lon})\n"
                f"Inside Geofence: {'YES' if inside else 'NO'}\n"
                f"Distance: {round(distance, 2)} meters"
            )
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject=f"Geofence Alert: {device_id}"
            )
        except Exception as sns_err:
            print(f"SNS Error: {sns_err}")

        
        # Return HTTP response
        # --------------------
        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str),  # Convert Decimals to strings for JSON
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        # Catch any unhandled errors
        print(f"Unhandled error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
