from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, time, timedelta, datetime
from rest_framework.permissions import AllowAny, IsAuthenticated

from Api.models import FoundPerson, MissingPerson
from Api.serializers import MissingPersonSerializer, ReportedSeenPersonSerializer
from Statistics.models import Case, Remark
from Statistics.serializers import CaseSerializer, RemarksSerializer
from Users.models import User
from Users.serializers import CustomUserSerializer
from django.db.models import Q
from django.core.mail import send_mail


"""
Daily Activity Report:
Weekly/Monthly Activity Summary:
Case Status Report:
Face Recognition Performance Report:
Geographical Distribution Report:
User Activity Report:
"""


class Daily_Activity(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, y, m, d):

        missing_persons = self.new_missing_persons(y, m, d)
        found_persons = self.new_found_persons(y, m, d)
        created_users = self.user_activity(y, m, d)
        return Response({"Missing_persons": missing_persons, "found_persons": found_persons, "accounts": created_users})

    @classmethod
    def new_missing_persons(cls, y, m, d):
        """
        get all missing persons
        whose created at is same as todays date
        """
        target_date = datetime(y, m, d)

        missing_persons = MissingPerson.objects.filter(
            created_at__date=target_date.date())
        missing_persons_serializer = MissingPersonSerializer(
            missing_persons, many=True).data

        return {"missing_persons": missing_persons_serializer, "count": missing_persons.count()}

    @classmethod
    def new_found_persons(cls, y, m, d):
        """
        get all found persons
        whose created at is same as todays date
        """
        target_date = datetime(y, m, d)

        found_persons = FoundPerson.objects.filter(
            created_at__date=target_date.date())
        found_persons_serializer = ReportedSeenPersonSerializer(
            found_persons, many=True).data

        return {"found_persons": found_persons_serializer, "count": len(found_persons_serializer)}

    @classmethod
    def user_activity(cls, y, m, d):
        target_date = datetime(y, m, d)
        """
        get all users created today
        whose created at is same as todays date
        """
        all_users = User.objects.filter(
            Q(start_date__date=target_date) & Q(is_staff=False))
        all_users_serializer = CustomUserSerializer(all_users, many=True).data
        user_details = []
        for user in all_users_serializer:

            user_details.append(
                {"email": user["email"], "user_name": user["user_name"]})

        return {"users": user_details, "total_count": len(all_users_serializer)}


class Weekly_Activity(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, y, m, d):
        missing_persons = self.new_missing_persons_range(y, m, d)
        found_persons = self.new_found_persons_range(y, m, d)
        created_users = self.user_activity_range(y, m, d)
        return Response({"Missing_persons": missing_persons, "found_persons": found_persons, "accounts": created_users})

    @classmethod
    def new_missing_persons_range(cls, y, m, d):
        """
        get all missing persons
        whose created in last six days
        """
        end_date = datetime(y, m, d)
        six_days = timedelta(days=6)
        start_date = end_date-six_days

        missing_persons = MissingPerson.objects.filter(
            created_at__date__range=[start_date.date(), end_date.date()])
        missing_persons_serializer = MissingPersonSerializer(
            missing_persons, many=True).data

        return {"missing_persons": missing_persons_serializer, "count": missing_persons.count()}

    @classmethod
    def new_found_persons_range(cls, y, m, d):
        """
        get all found persons
        whose created in last six days
        """
        end_date = datetime(y, m, d)
        six_days = timedelta(days=6)
        start_date = end_date-six_days

        found_persons = FoundPerson.objects.filter(
            created_at__date__range=[end_date.date(), start_date.date()])
        found_persons_serializer = ReportedSeenPersonSerializer(
            found_persons, many=True).data

        return {"found_persons": found_persons_serializer, "count": len(found_persons_serializer)}

    @classmethod
    def user_activity_range(cls, y, m, d):
        """
        Get all users created within a date range
        """
        end_date = datetime(y, m, d)
        six_days = timedelta(days=6)
        start_date = end_date-six_days

        all_users = User.objects.filter(
            Q(start_date__date__range=[start_date, end_date]) & Q(is_staff=False))
        all_users_serializer = CustomUserSerializer(all_users, many=True).data
        user_details = []

        for user in all_users_serializer:
            user_details.append(
                {"email": user["email"], "user_name": user["user_name"]}
            )

        return {"users": user_details, "total_count": len(all_users_serializer)}


class Allcases(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cases = Case.objects.all()
        case_serializer = CaseSerializer(cases, many=True).data
        return Response(case_serializer, status=status.HTTP_200_OK)


class CaseDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            cases = Case.objects.get(case_number=id)
            cs = CaseSerializer(cases).data
            if cs.get('missing_person'):
                mp = MissingPerson.objects.get(id=cs.get('missing_person'))
                cs['name'] = mp.first_name + " " + mp.last_name
            if cs.get('found_person'):
                fp = FoundPerson.objects.get(id=cs.get('found_person'))
                cs['name'] = fp.first_name + " " + fp.last_name

            remarks = Remark.objects.filter(case_id=cases.id)
            remarks_serializer = RemarksSerializer(remarks, many=True).data
            for remark in remarks_serializer:
                creator_id = User.objects.get(id=remark.get("created_by"))
                remark["created_by_name"] = creator_id.user_name
            cs['remarks'] = remarks_serializer

            return Response(cs, status=status.HTTP_200_OK)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        except MissingPerson.DoesNotExist:
            return Response({"error": "Missing person not found"}, status=status.HTTP_404_NOT_FOUND)
        except FoundPerson.DoesNotExist:
            return Response({"error": "Found person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Remark.DoesNotExist:
            return Response({"error": "Remarks not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# if we dont get a math then we just add remarks  here

    def post(self, request, id):
        data = request.data
        cases = Case.objects.get(case_number=id)
        case_serializer = CaseSerializer(data=data, instance=cases)
        if case_serializer.is_valid():
            case_serializer.save()
            return Response({"msg": "successfully added information"}, status=status.HTTP_200_OK)


class AddRemark(APIView):
    def post(self, request, id):

        try:
            data = request.data
            fp = FoundPerson.objects.get(id=id)
            pf_case = Case.objects.get(found_person=fp.id)
            created_by = request.user.id
            remarks = data.get('remarks', "none")
            remark_data = {'remarks': remarks,
                           'case_id': pf_case.id, 'created_by': created_by}
            remark_serializer = RemarksSerializer(data=remark_data)

            if not remark_serializer.is_valid():
                return Response({"error": remark_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            remark_serializer.save()

            recipient_email = fp.created_by.email
            sender_email = request.user.email
            message = data.get(
                "message", "We conducted a search but could not find any match. We will keep sending you these emails to notify you of our progress.")

            try:
                send_mail(
                    "Follow-up on Reported Missing Person",
                    message,
                    sender_email,
                    [recipient_email],
                    fail_silently=False,
                )
            except Exception as e:
                raise Exception(f"Failed to send email: {str(e)}")

            return Response({"Msg": "Success"}, status=status.HTTP_201_CREATED)
        except FoundPerson.DoesNotExist:
            return Response({"error": "Found person not found"}, status=status.HTTP_404_NOT_FOUND)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TableData(APIView):

    def get(self, request):

        missing_persons = MissingPerson.objects.all().values('created_at')
        mp_serialized = [entry['created_at'] for entry in missing_persons]

        found_persons = FoundPerson.objects.all().values('created_at')
        fp_serialized = [entry['created_at'] for entry in found_persons]

        return Response({"missing_persons": mp_serialized, "found_persons": fp_serialized}, status=status.HTTP_200_OK)


class SearchCase(APIView):
    def post(self, request):
        try:
            case_found = {}
            case_no = request.data.get("searchVal", "")
            print(case_no)
            case_instance = Case.objects.get(case_number=case_no)
            case_serialized = CaseSerializer(case_instance).data
            case_found['type'] = case_serialized.get("type")
            case_found['case_number'] = case_serialized.get("case_number")
            case_found['status'] = case_serialized.get('status')
            return Response(case_found, status=status.HTTP_200_OK)
        except Case.DoesNotExist:
            return Response({"error": "Case not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
