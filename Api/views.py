from rest_framework.decorators import api_view, permission_classes
from Statistics.serializers import CaseSerializer
from .models import FoundPersonLocation, MissingPerson, FoundPerson, MissingPersonLocation
import face_recognition
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from .serializers import FoundPersonLocationSerializer, MissingPersonLocationSerializer, MissingPersonSerializer, ReportedSeenPersonSerializer
from .models import MissingPerson
from .models import FoundPerson
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


# view to get all  missing persons


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Missing(request):
    if request.method == 'GET':
        try:
            persons = MissingPerson.objects.all()

            serialized_data = []

            for person in persons:
                data = MissingPersonSerializer(person).data

                data['created_by'] = person.created_by.user_name
                serialized_data.append(data)

            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# view to get all  found persons
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Found(request):
    if request.method == "GET":
        try:
            persons = FoundPerson.objects.all()

            serialized_data = []

            for person in persons:
                data = ReportedSeenPersonSerializer(person).data

                data['created_by'] = person.created_by.user_name
                serialized_data.append(data)
            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# view to serve a single seen person using the id
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Seen_Details(request, id):
    if request.method == 'GET':
        try:
            person = FoundPerson.objects.get(id=id)
            location = FoundPersonLocation.objects.get(found_person=person)
            location_serialized = FoundPersonLocationSerializer(
                location).data

            serialized_data = []

            data = ReportedSeenPersonSerializer(person).data

            data['created_by'] = person.created_by.user_name
            data['uid'] = person.created_by.u_id
            data['name_'] = location_serialized.get('name', "")
            data['county_'] = location_serialized.get('county', '')
            data['time_seen'] = location_serialized.get('time_seen', '')
            serialized_data.append(data)

            return Response(serialized_data, status=status.HTTP_200_OK)

        except FoundPerson.DoesNotExist:
            return Response({"error": "Found person not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to serve a single missing person using the trackCode


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Missing_Details(request, trackCode):
    if request.method == 'GET':
        try:
            serialized_data = []
            person = MissingPerson.objects.get(trackCode=trackCode)

            location = MissingPersonLocation.objects.get(
                missing_person=person)
            location_serialized = MissingPersonLocationSerializer(
                location).data

            data = MissingPersonSerializer(person).data
            data['created_by'] = person.created_by.user_name
            data['name_'] = location_serialized.get('name', "")
            data['county_'] = location_serialized.get('county', '')
            data['time_seen'] = location_serialized.get('time_seen', '')

            serialized_data.append(data)

            return Response(serialized_data, status=status.HTTP_200_OK)

        except MissingPerson.DoesNotExist:
            return Response({"error": "Missing person not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# send a post request with the id and response include not found or found including pic name location

# view to do the facial recognition part


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Find(request, pid):
    if request.method == "GET":
        try:
            data = []
            matches = []

            person = MissingPerson.objects.get(trackCode=pid)
            serializer = MissingPersonSerializer(person)
            data.append(serializer.data)

            img_path = "." + serializer.data["image"]
            image = face_recognition.load_image_file(img_path)
            image_encodings = face_recognition.face_encodings(image)

            found_persons = FoundPerson.objects.all()
            serializer = ReportedSeenPersonSerializer(found_persons, many=True)
            found_persons_array = serializer.data

            for found_person in found_persons_array:
                fimg_path = "." + found_person["image"]
                fimage = face_recognition.load_image_file(fimg_path)
                fimage_encodings = face_recognition.face_encodings(fimage)

                if len(fimage_encodings) > 0:
                    results = face_recognition.compare_faces(
                        image_encodings[0], fimage_encodings)
                    if results[0]:
                        matches.append({
                            "name": found_person["first_name"],
                            "id": found_person["id"],
                            "image": found_person["image"],
                            "age": found_person["age"]
                        })
            return Response({"matches": matches, "mps": data}, status=status.HTTP_200_OK)

        except MissingPerson.DoesNotExist:
            return Response({"error": "Missing person not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to report a missing person to reported seen persons db


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def Report_Person(request):
    if request.method == 'POST':
        try:
            # Extract data from the request
            data = request.data

            required_fields = ['first_name', 'last_name', 'eye_color', 'hair_color', 'age',
                               'description', 'gender', 'image', 'county', 'name', 'latitude', 'longitude', 'time_found']
            if not all(field in data for field in required_fields):
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare data for serialization
            found_person_data = {
                'first_name': data.get('first_name'),
                'middle_name': data.get('middle_name'),
                'last_name': data.get('last_name'),
                'eye_color': data.get('eye_color'),
                'hair_color': data.get('hair_color'),
                'age': data.get('age'),
                'description': data.get('description'),
                'nick_name': data.get('nick_name'),
                'image': data.get('image'),
                'gender': data.get('gender'),
                'created_by': request.user.id
            }

            # Serialize found person data
            serializer = ReportedSeenPersonSerializer(data=found_person_data)
            if serializer.is_valid():
                found_person = serializer.save()

                # Prepare case data
                case_data = {'found_person': found_person.id, 'type': 'found'}
                case_serializer = CaseSerializer(data=case_data)
                if case_serializer.is_valid():

                    case = case_serializer.save()
                else:
                    found_person.delete()
                    return Response({"error": "Failed to create case", "details": case_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                # Prepare location data for serialization
                found_person_location_data = {
                    'county': data.get('county'),
                    'name': data.get('name'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'time_found': data.get('time_found'),
                    'found_person': found_person.id
                }

                seen_person_serializer = FoundPersonLocationSerializer(
                    data=found_person_location_data)
                if seen_person_serializer.is_valid():
                    seen_person_serializer.save()
                    return Response({"message": "Thank you for successfully adding a missing person"}, status=status.HTTP_201_CREATED)
                else:
                    found_person.delete()
                    case.delete()
                    return Response({"error": "Failed to add location data", "details": seen_person_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Failed to add found person data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to add missing person to missing person db and create them a case


@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def Add_Person(request):
    if request.method == 'POST':
        try:
            missing_person_data = {}
            for field in MissingPerson._meta.fields:
                field_name = field.name
                if field_name in request.data:
                    missing_person_data[field_name] = request.data[field_name]

            # Set the 'created_by' field to the current user
            missing_person_data['created_by'] = request.user.id

            # Save the missing person
            missing_person_serializer = MissingPersonSerializer(
                data=missing_person_data)
            if not missing_person_serializer.is_valid():
                return Response({"error": "Failed to add missing person", "details": missing_person_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            missing_person = missing_person_serializer.save()

            # Create a case for the missing person
            case_data = {
                'missing_person': missing_person.id, "type": "missing"}
            case_serializer = CaseSerializer(data=case_data)
            if not case_serializer.is_valid():
                missing_person.delete()
                return Response({"error": "Failed to create a case", "details": case_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            new_case = case_serializer.save()
            # Add location details for the missing person
            location_data = {}
            for field in MissingPersonLocation._meta.fields:
                field_name = field.name
                if field_name in request.data:
                    location_data[field_name] = request.data[field_name]

            # Set the missing person for the location
            location_data['missing_person'] = missing_person.id

            # Save the location details
            location_serializer = MissingPersonLocationSerializer(
                data=location_data)
            if not location_serializer.is_valid():
                missing_person.delete()
                new_case.delete()
                return Response({"error": "Failed to add location details", "details": location_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            location_serializer.save()

            return Response({"message": "Missing person added successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# view to get locations
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getLocations(request):
    if request.method == "GET":
        try:
            persons = []

            missing_persons = MissingPersonLocation.objects.select_related(
                'missing_person').all()
            serializer_missing = MissingPersonLocationSerializer(
                missing_persons, many=True).data
            for mp in serializer_missing:
                mp_instance = MissingPerson.objects.get(
                    id=mp["missing_person"])
                mp_data = {
                    "name": mp_instance.first_name + " " + mp_instance.last_name,
                    "status": "missing",
                    "location": {"lat": float(mp["latitude"]), "lng": float(mp["longitude"])}
                }
                persons.append(mp_data)

            found_persons = FoundPersonLocation.objects.select_related(
                'found_person').all()
            serializer_found = FoundPersonLocationSerializer(
                found_persons, many=True).data
            for fp in serializer_found:
                fp_instance = FoundPerson.objects.get(id=fp["found_person"])
                fp_data = {
                    "name": fp_instance.first_name + " " + fp_instance.last_name,
                    "status": "found",
                    "location": {"lat": float(fp["latitude"]), "lng": float(fp["longitude"])}
                }
                persons.append(fp_data)

            return Response({"persons": persons}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
